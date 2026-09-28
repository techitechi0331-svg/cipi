"""Offline regression tests using real discord.py command registration."""
import asyncio
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
from discord import app_commands

from integrations.discord import bot as b
from automation.human_gate import apply as hg


def interaction(admin=True, guild_id=123):
    return SimpleNamespace(
        guild_id=guild_id, guild=SimpleNamespace(id=guild_id),
        user=SimpleNamespace(guild_permissions=SimpleNamespace(administrator=admin)),
        response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock(), is_done=lambda: False),
        followup=SimpleNamespace(send=AsyncMock()),
    )


def choice(value):
    return app_commands.Choice(name=value, value=value)


SNAPSHOT = {
    "project_id": "virtual_guitar", "freshness": "FRESH", "phase": "READY",
    "generation_id": "gen-test", "source_state_digest": "a" * 64,
    "resume_contract": {"can_resume": True, "can_autonomously_resume": True},
    "human_gates": [
        {"source": "RESEARCH_JOB", "job_id": "job-1", "gates": ["REAL_AUDIO_AB"]},
        {"source": "AUTONOMOUS_TRACK", "track_id": "track-1", "gates": ["REAL_DI_AB"]},
    ],
}


class Channel:
    def __init__(self, messages=()):
        self.id = 10
        self.messages = list(messages)
        self.send = AsyncMock(side_effect=self.add)
        self.history_calls = []

    async def add(self, text, **kwargs):
        msg = self.message(b.bot.user, text, len(self.messages) + 1)
        self.messages.append(msg)
        return msg

    @staticmethod
    def message(author, text, message_id):
        msg = SimpleNamespace(author=author, content=text, id=message_id)

        async def edit(**kwargs):
            msg.content = kwargs["content"]
        msg.edit = AsyncMock(side_effect=edit)
        return msg

    async def history(self, **kwargs):
        self.history_calls.append(kwargs)
        for msg in list(self.messages):
            yield msg

    async def fetch_message(self, message_id):
        for msg in self.messages:
            if msg.id == message_id:
                return msg
        raise discord.NotFound(SimpleNamespace(status=404, reason="missing"), "missing")


class CatalogTests(unittest.TestCase):
    def test_catalog_matches_real_commands_and_metadata(self):
        commands = {c.name: c for c in b.bot.tree.get_commands()}
        self.assertEqual(set(commands), set(b.COMMAND_CATALOG))
        text = b.commands_text()
        self.assertLessEqual(len(text.encode("utf-16-le")) // 2, 2000)
        for name, (_, description, changes, admin) in b.COMMAND_CATALOG.items():
            self.assertEqual(commands[name].description, description)
            self.assertIn(f"**/{name}** — {description}", text)
            self.assertTrue(commands[name].guild_only)
            self.assertEqual(bool(commands[name].default_permissions and
                                  commands[name].default_permissions.administrator), admin)
            line = next(line for line in text.splitlines() if f"**/{name}**" in line)
            self.assertEqual("⚠️" in line, changes)
            self.assertEqual("🔒" in line, admin)

    def test_catalog_overflow_is_detected(self):
        with patch.dict(b.COMMAND_CATALOG, extra=("管理", "x" * 2100, False, False)):
            with self.assertRaises(ValueError):
                b.commands_text()

    def test_renderers_obey_limit_even_with_emoji(self):
        data = copy.deepcopy(SNAPSHOT)
        data["projects"] = [{"project_id": "🧠" * 200, "phase": "READY"}] * 30
        data["resume_contract"]["blocked_dependencies"] = ["🧠" * 2000] * 8
        data["human_gates"][0]["gates"] = ["🧠" * 2000] * 4
        for render in (b.status_text, b.project_text, b.human_gate_text):
            self.assertLessEqual(len(render(data).encode("utf-16-le")) // 2, 2000)

    def test_secret_detection_covers_authoritative_intake_examples(self):
        values = ["ghp_" + "A" * 25, "github_pat_" + "A" * 25,
                  "sk-" + "A" * 25, "AIza" + "A" * 35,
                  "-----BEGIN RSA PRIVATE KEY-----", "api_key=example",
                  "access_token=example", "auth-token: example", "password: example", "secret=example"]
        for value in values:
            self.assertTrue(any(p.search(value) for p in hg.SENSITIVE_PATTERNS))
            with self.assertRaises(b.PublicError):
                b.validate_public_input(value)
        for value in ["DISCORD_BOT_TOKEN=example", "CIPI_CROSS_REPO_TOKEN=example",
                      "A" * 24 + "." + "B" * 6 + "." + "C" * 30, "sk-proj-" + "A" * 30]:
            with self.assertRaises(b.PublicError):
                b.validate_public_input(value)
        b.validate_public_input("https://example.org/evidence/ab-test")

    def test_errors_do_not_echo_payloads(self):
        for error in (RuntimeError("sensitive-response"), ValueError("sensitive-response"),
                      b.aiohttp.ClientError("sensitive-response")):
            self.assertNotIn("sensitive-response", b.error_text(error))

    def test_missing_env_and_invalid_guild_fail_without_values(self):
        with patch.object(b, "TOKEN", ""):
            with self.assertRaises(SystemExit):
                b.main()
        with patch.object(b, "TOKEN", "synthetic"), patch.dict(b.os.environ, DISCORD_GUILD_ID="sensitive-value"):
            with self.assertRaises(SystemExit) as caught:
                b.main()
            self.assertNotIn("sensitive-value", str(caught.exception))


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        for name in ("SYNC_LOCK", "MESSAGE_LOCK", "DISPATCH_LOCK"):
            patcher = patch.object(b, name, asyncio.Lock())
            patcher.start()
            self.addCleanup(patcher.stop)
        for name, value in (("MESSAGE_IDS", {}), ("LAST_DISPATCH", {}),
                            ("GUILD_ID", 123), ("GITHUB_TOKEN", "synthetic")):
            patcher = patch.object(b, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    async def test_commands_is_ephemeral_and_uses_catalog(self):
        i = interaction()
        await b.commands_command.callback(i)
        i.response.send_message.assert_awaited_once_with(b.commands_text(), ephemeral=True)

    async def test_runtime_permissions_and_guild_restriction(self):
        for command in b.bot.tree.get_commands():
            admin = b.COMMAND_CATALOG[command.name][3]
            for i, allowed in ((interaction(), True), (interaction(False), not admin),
                               (interaction(guild_id=999), False), (interaction(guild_id=None), False)):
                if allowed:
                    self.assertTrue(await command.checks[0](i))
                else:
                    with self.assertRaises(app_commands.CheckFailure):
                        await command.checks[0](i)

    async def test_sync_registration_and_only_one_monitor(self):
        with patch.object(b.bot.tree, "copy_global_to") as copy_to, \
             patch.object(b.bot.tree, "sync", new=AsyncMock()) as sync, \
             patch.object(b.monitor, "is_running", return_value=False), \
             patch.object(b.monitor, "start") as start:
            await b.bot.setup_hook()
            self.assertEqual(copy_to.call_args.kwargs["guild"].id, 123)
            sync.assert_awaited_once()
            start.assert_called_once()
        with patch.object(b.monitor, "is_running", return_value=True), \
             patch.object(b.monitor, "start") as start, \
             patch.object(b.bot.tree, "sync", new=AsyncMock()), \
             patch.object(b.bot.tree, "copy_global_to"):
            await b.bot.setup_hook()
            start.assert_not_called()
        with patch.object(b, "sync_once", new=AsyncMock()) as sync:
            await b.on_ready()
            await b.on_ready()
            sync.assert_not_awaited()
            await b.monitor()
            sync.assert_awaited_once()
        self.assertEqual(b.monitor.minutes, 5)

    async def test_create_edit_restart_and_concurrent_upsert(self):
        channel = Channel()
        title = b.COMMAND_TITLE
        await asyncio.gather(*(b.upsert_message(channel, title, title + "\nold") for _ in range(3)))
        channel.send.assert_awaited_once()
        b.MESSAGE_IDS.clear()  # process restart
        await b.upsert_message(channel, title, b.commands_text())
        channel.send.assert_awaited_once()
        channel.messages[0].edit.assert_awaited_once()
        await b.upsert_message(channel, title, b.commands_text())
        channel.messages[0].edit.assert_awaited_once()

    async def test_old_message_and_foreign_author(self):
        for title in (b.COMMAND_TITLE, b.STATUS_TITLE):
            b.MESSAGE_IDS.clear()
            foreign = Channel.message(object(), title, 1)
            owned = Channel.message(b.bot.user, title + "\nold", 2)
            channel = Channel([foreign, owned] + [Channel.message(object(), "chat", x + 3) for x in range(40)])
            await b.upsert_message(channel, title, title + "\nnew")
            channel.send.assert_not_awaited()
            owned.edit.assert_awaited_once()
            foreign.edit.assert_not_awaited()
            self.assertIsNone(channel.history_calls[0]["limit"])

    async def test_deleted_cached_message_is_replaced(self):
        channel = Channel()
        await b.upsert_message(channel, b.COMMAND_TITLE, b.commands_text())
        channel.messages.clear()
        await b.upsert_message(channel, b.COMMAND_TITLE, b.commands_text())
        self.assertEqual(channel.send.await_count, 2)

    async def test_failed_history_never_sends(self):
        channel = Channel()

        async def failing_history(**kwargs):
            raise RuntimeError("history unavailable")
            yield
        channel.history = failing_history
        with self.assertRaises(RuntimeError):
            await b.upsert_message(channel, b.COMMAND_TITLE, b.commands_text())
        channel.send.assert_not_awaited()

    async def test_command_channel_created_in_management_category(self):
        guild, category, channel = object(), object(), Channel()
        with patch.object(b.bot, "get_guild", return_value=guild), \
             patch.object(b, "ensure_category", new=AsyncMock(return_value=category)) as cat, \
             patch.object(b, "ensure_text", new=AsyncMock(return_value=channel)) as text:
            await b.update_commands_channel()
            cat.assert_awaited_once_with(guild, *b.CATEGORY_SPECS[0])
            text.assert_awaited_once_with(guild, category, "コマンド", "command")
            self.assertEqual(channel.messages[0].content, b.commands_text())

    async def test_commands_sync_survives_cipi_outage(self):
        with patch.object(b, "update_commands_channel", new=AsyncMock()) as commands, \
             patch.object(b, "get_json", new=AsyncMock(side_effect=RuntimeError("secret"))):
            errors = await b.sync_once()
            commands.assert_awaited_once()
            self.assertEqual(len(errors), 1)
            self.assertNotIn("secret", errors[0])

    async def test_status_sync_survives_commands_failure(self):
        with patch.object(b, "update_commands_channel", new=AsyncMock(side_effect=RuntimeError())), \
             patch.object(b, "get_json", new=AsyncMock(return_value={})), \
             patch.object(b, "update_status_channel", new=AsyncMock()) as status, \
             patch.object(b, "update_alerts", new=AsyncMock()):
            self.assertEqual(len(await b.sync_once()), 1)
            status.assert_awaited_once()

    async def test_setup_does_not_report_success_after_partial_failure(self):
        i = interaction()
        with patch.object(b, "sync_once", new=AsyncMock(return_value=["failure"])) as sync:
            await b.setup.callback(i)
            sync.assert_awaited_once_with(configure_guild=i.guild)
            self.assertIn("未完了", i.followup.send.call_args.args[0])

    async def test_alert_partial_failure_does_not_repeat_previous_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            channel = SimpleNamespace(name="警告", send=AsyncMock(side_effect=[None, RuntimeError(), None]))
            guild = SimpleNamespace(text_channels=[channel])
            data = {"projects": [{"project_id": "black76", "phase": "BLOCKED"},
                                 {"project_id": "virtual_guitar", "phase": "HUMAN_GATE"}]}
            with patch.object(b, "ALERT_STATE", Path(tmp) / "alerts.json"), \
                 patch.object(b.bot, "get_guild", return_value=guild):
                with self.assertRaises(RuntimeError):
                    await b.update_alerts(data)
                await b.update_alerts(data)
                await b.update_alerts(data)
                self.assertEqual(channel.send.await_count, 3)
                self.assertEqual(b.load_alerts(), {"black76": "BLOCKED", "virtual_guitar": "HUMAN_GATE"})

    async def test_concurrent_dispatch_is_debounced(self):
        with patch.object(b, "workflow_running", new=AsyncMock(return_value=False)), \
             patch.object(b, "post_json", new=AsyncMock()) as post:
            results = await asyncio.gather(b.dispatch(b.GLOBAL_DAG), b.dispatch(b.GLOBAL_DAG), return_exceptions=True)
            post.assert_awaited_once()
            self.assertEqual(sum(isinstance(r, b.PublicError) for r in results), 1)
            self.assertEqual(post.call_args.args[1], {"ref": "main"})

    async def test_timeout_does_not_retry_dispatch(self):
        with patch.object(b, "workflow_running", new=AsyncMock(return_value=False)), \
             patch.object(b, "post_json", new=AsyncMock(side_effect=TimeoutError())) as post:
            with self.assertRaises(TimeoutError):
                await b.dispatch(b.HUMAN_GATE_WORKFLOW)
            with self.assertRaises(b.PublicError):
                await b.dispatch(b.HUMAN_GATE_WORKFLOW)
            post.assert_awaited_once()

    async def test_running_workflow_or_failed_lookup_blocks_dispatch(self):
        for running in (AsyncMock(return_value=True), AsyncMock(side_effect=TimeoutError())):
            with patch.object(b, "workflow_running", new=running), patch.object(b, "post_json", new=AsyncMock()) as post:
                with self.assertRaises((b.PublicError, TimeoutError)):
                    await b.dispatch(b.GLOBAL_DAG)
                post.assert_not_awaited()

    async def test_workflow_lookup_checks_filtered_statuses(self):
        with patch.object(b, "get_json", new=AsyncMock(return_value={"workflow_runs": []})) as get:
            self.assertFalse(await b.workflow_running(b.GLOBAL_DAG))
            urls = [call.args[0] for call in get.await_args_list]
            for state in ("queued", "in_progress", "waiting", "pending", "requested"):
                self.assertTrue(any(f"status={state}&" in url for url in urls))
        with patch.object(b, "get_json", new=AsyncMock(return_value={})):
            with self.assertRaises(b.PublicError):
                await b.workflow_running(b.GLOBAL_DAG)

    async def test_missing_token_and_unknown_project(self):
        with patch.object(b, "GITHUB_TOKEN", ""), patch.object(b, "post_json", new=AsyncMock()) as post:
            with self.assertRaises(b.PublicError):
                await b.dispatch(b.GLOBAL_DAG)
            post.assert_not_awaited()
        with patch.object(b, "get_json", new=AsyncMock()) as get:
            with self.assertRaises(b.PublicError):
                await b.project_state("unknown")
            get.assert_not_awaited()

    async def gate(self, snapshot=None, **overrides):
        args = dict(project=choice("virtual_guitar"), target_type=choice("RESEARCH_JOB"),
                    target_id="job-1", gate="REAL_AUDIO_AB", outcome=choice("COMPLETE"),
                    evidence_ref="https://example.org/ab", rationale="Human reviewed the matched A/B.")
        args.update(overrides)
        i = interaction()
        with patch.object(b, "project_state", new=AsyncMock(return_value=snapshot or SNAPSHOT)), \
             patch.object(b, "dispatch", new=AsyncMock()) as dispatch:
            await b.gate_decision.callback(i, **args)
        return i, dispatch

    async def test_gate_uses_formal_workflow_and_snapshot_identifiers(self):
        i, dispatch = await self.gate()
        workflow, inputs = dispatch.call_args.args
        self.assertEqual(workflow, b.HUMAN_GATE_WORKFLOW)
        self.assertEqual(inputs["source_generation_id"], SNAPSHOT["generation_id"])
        self.assertEqual(inputs["source_state_digest"], SNAPSHOT["source_state_digest"])
        self.assertEqual(inputs["source"], "DISCORD")
        self.assertTrue(i.followup.send.call_args.kwargs["ephemeral"])

    async def test_track_completion_is_record_only(self):
        i, dispatch = await self.gate(target_type=choice("AUTONOMOUS_TRACK"), target_id="track-1", gate="REAL_DI_AB")
        dispatch.assert_awaited_once()
        self.assertEqual(dispatch.call_args.args[0], b.HUMAN_GATE_WORKFLOW)
        self.assertIn("自動再開しません", i.followup.send.call_args.args[0])

    async def test_gate_rejects_stale_unknown_and_secret_inputs(self):
        stale = dict(SNAPSHOT, freshness="STALE")
        missing_digest = dict(SNAPSHOT)
        missing_digest.pop("source_state_digest")
        for kwargs in ({"snapshot": stale}, {"snapshot": missing_digest}, {"target_id": "other"},
                       {"evidence_ref": "api_key=synthetic"}, {"rationale": "password=synthetic-value"}):
            _, dispatch = await self.gate(**kwargs)
            dispatch.assert_not_awaited()

    async def test_continue_fails_closed_and_dispatches_ready_contract(self):
        blocked = [dict(SNAPSHOT, freshness="STALE"), dict(SNAPSHOT, phase="HUMAN_GATE"),
                   dict(SNAPSHOT, phase="BLOCKED"), dict(SNAPSHOT, resume_contract={}),
                   dict(SNAPSHOT, resume_contract={"can_resume": True, "can_autonomously_resume": False})]
        for data in blocked + [SNAPSHOT]:
            with patch.object(b, "project_state", new=AsyncMock(return_value=data)), \
                 patch.object(b, "dispatch", new=AsyncMock()) as dispatch:
                await b.continue_project.callback(interaction(), choice("virtual_guitar"))
                if data is SNAPSHOT:
                    dispatch.assert_awaited_once_with(b.GLOBAL_DAG)
                else:
                    dispatch.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
