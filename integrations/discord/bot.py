import os
import json
import asyncio
import re
import time
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID = 0  # Validated in main(), so importing the catalog never starts the bot.
GITHUB_TOKEN = os.environ.get("CIPI_DISCORD_GITHUB_TOKEN", "")

OWNER = "techitechi0331-svg"
REPO = "cipi"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
STATUS_URL = f"{RAW}/research/continuity/global/current.json"
GLOBAL_DAG = "global-dag-orchestrator.yml"
HUMAN_GATE_WORKFLOW = "human-gate-decision.yml"
ALERT_STATE = Path(__file__).with_name("alert_state.json")
COMMAND_TITLE = "## 🧠 CIPI Bot コマンド一覧"
STATUS_TITLE = "## 🧠 CIPI 開発状況"

# Single source for slash descriptions, access checks and both help surfaces.
COMMAND_CATALOG = {
    "ping": ("状態確認", "CIPI管理Botの動作を確認", False, False),
    "status": ("状態確認", "CIPI全体の開発状況を表示", False, False),
    "project": ("状態確認", "選択した製品・研究プロジェクトの詳細を表示", False, False),
    "continue": ("研究操作", "CIPIの安全条件を確認して研究再開を要求", True, True),
    "human-gate": ("Human Gate", "人間確認が必要な項目を表示", False, False),
    "gate-decision": ("Human Gate", "Human Gateの確認結果をCIPIへ正式記録", True, True),
    "setup": ("管理", "Discord構成を最新状態へ同期", True, True),
    "commands": ("管理", "このコマンド一覧を表示", False, False),
}
SYNC_LOCK = asyncio.Lock()
MESSAGE_LOCK = asyncio.Lock()
DISPATCH_LOCK = asyncio.Lock()
MESSAGE_IDS = {}  # Presentation cache only; rediscovered from Discord after restart.
LAST_DISPATCH = {}  # Short debounce only; CIPI remains the scheduler/authority.


def commands_text():
    lines = [COMMAND_TITLE, "🟢 閲覧のみ ｜ ⚠️ 変更・実行あり（要注意） ｜ 🔒 管理者限定", ""]
    category = None
    for name, (group, description, changes_state, admin_only) in COMMAND_CATALOG.items():
        if category != group:
            lines += [f"【{group}】"]
            category = group
        badges = "⚠️" if changes_state else "🟢"
        if admin_only:
            badges += " 🔒"
        lines += [f"{badges} **/{name}** — {description}"]
    lines += ["", "まず /status で全体を確認し、/project で詳細を確認できます。",
              "再開・Human Gateの反映はCIPIが安全条件を再確認します。",
              "自動研究トラックの決定は記録のみです。秘密情報は入力しないでください。"]
    text = "\n".join(lines)
    if len(text.encode("utf-16-le")) // 2 > 2000:
        raise ValueError("command catalog exceeds Discord message limit")
    return text


def clip_message(text):
    if len(text.encode("utf-16-le")) // 2 <= 1900:
        return text
    return text.encode("utf-16-le")[:3700].decode("utf-16-le", errors="ignore") + "\n…（一部省略）"


class PublicError(RuntimeError):
    """Only fixed, non-sensitive messages may be displayed to users."""


def error_text(error):
    if isinstance(error, PublicError):
        return str(error)
    if isinstance(error, (TimeoutError, aiohttp.ClientError)):
        return "接続を確認できません。送信後のタイムアウトでは受付済みの可能性があります。GitHub Actionsを確認してください。"
    if isinstance(error, discord.Forbidden):
        return "Botのチャンネル閲覧・履歴閲覧・送信権限を確認してください。/setup にはチャンネル管理権限も必要です。"
    return "処理を完了できませんでした。設定・権限・CIPIの状態を確認してください。"


def validate_public_input(value):
    # Standalone bot.py distribution: keep coverage of the authoritative intake
    # patterns (tested against automation.human_gate.apply.SENSITIVE_PATTERNS).
    patterns = (
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
        r"\bsk-[A-Za-z0-9_-]{20,}\b", r"\bAIza[0-9A-Za-z_-]{30,}\b",
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----",
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\s*[:=]",
        r"(?i)\b(?:[A-Z0-9_]*TOKEN|[A-Z0-9_]*API_KEY|PRIVATE_KEY)\s*[:=]",
        r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{20,}\b",
    )
    if any(re.search(pattern, value) for pattern in patterns) or any(
        secret and secret in value for secret in (TOKEN, GITHUB_TOKEN)
    ):
        raise PublicError("秘密情報らしい入力があるため送信しません。公開可能な参照・判断理由だけを入力してください。")

PROJECTS = {
    "amp_simulator": "Amp Simulator", "black76": "76 Black",
    "control_comp": "Vocal Control Comp", "doubler": "Vocal Doubler",
    "master_bus": "Master Bus", "melon": "MELON",
    "mic_simulator": "Mic Simulator", "pre610": "610 Preamp",
    "surface": "Vocal Surface", "virtual_guitar": "Virtual Guitar",
    "vl2a": "VL2A", "vo_prep": "Vo.Prep",
    "vocal_denoise": "Vocal Denoise", "vocal_resonance": "Vocal Resonance",
    "vocal_rider": "Vocal Rider",
}
PROJECT_CHOICES = [app_commands.Choice(name=v, value=k) for k, v in PROJECTS.items()]
TARGET_CHOICES = [
    app_commands.Choice(name="研究ジョブ", value="RESEARCH_JOB"),
    app_commands.Choice(name="自動研究トラック", value="AUTONOMOUS_TRACK"),
]
OUTCOME_CHOICES = [
    app_commands.Choice(name="完了", value="COMPLETE"),
    app_commands.Choice(name="却下", value="REJECT"),
    app_commands.Choice(name="保留", value="DEFER"),
]
PHASES = {
    "IDLE": ("⚪", "待機中"), "AUTO_READY": ("🟢", "自動再開可能"),
    "READY": ("🟢", "準備完了"), "RUNNING": ("🔵", "実行中"),
    "BLOCKED": ("🟡", "ブロック中"), "HUMAN_GATE": ("🔴", "人間の確認待ち"),
    "DONE": ("✅", "完了"), "REJECTED": ("❌", "却下"),
    "REFRESH_REQUIRED": ("🟠", "更新が必要"), "CONFLICT": ("⚠️", "競合"),
}
FORUM_TAGS = ["🟢 準備完了", "🔵 実行中", "🟡 ブロック中", "🔴 人間の確認待ち", "✅ 完了", "❌ 却下"]
OLD_TAGS = ["🟢 READY", "🔵 RUNNING", "🟡 BLOCKED", "🔴 HUMAN GATE", "✅ DONE", "❌ REJECTED"]

CATEGORY_SPECS = [
    ("🧠 00｜管理", "🧠 00｜CONTROL"),
    ("🔬 01｜研究", "🔬 01｜RESEARCH"),
    ("🎛️ 02｜製品", "🎛️ 02｜PRODUCTS"),
    ("🧪 03｜検証", "🧪 03｜VALIDATION"),
    ("🤖 04｜自動化", "🤖 04｜AUTOMATION"),
    ("📦 05｜リリース", "📦 05｜RELEASE"),
]
TEXT_SPECS = {
    "🧠 00｜管理": [("cipi状況", "cipi-status"), ("コマンド", "command"), ("警告", "alerts"), ("runner状況", "runner-status")],
    "🤖 04｜自動化": [("AIプロバイダー状況", "provider-status"), ("クォータ状況", "quota-status"), ("自動化ログ", "automation-log")],
    "📦 05｜リリース": [("booth", "booth")],
}
FORUM_SPECS = {
    "🔬 01｜研究": [("研究", "research"), ("実験", "experiments"), ("却下", "rejected")],
    "🎛️ 02｜製品": [("ボーカルプラグイン", "vocal-plugins"), ("アナログ回路", "analog-circuit"), ("バーチャル楽器", "virtual-instruments")],
    "🧪 03｜検証": [("検証", "validation"), ("バグ", "bugs"), ("人間確認", "human-gates")],
    "📦 05｜リリース": [("リリース", "release")],
}


class CIPIBot(commands.Bot):
    async def setup_hook(self):
        registered = {command.name for command in self.tree.get_commands()}
        if registered != set(COMMAND_CATALOG):
            raise PublicError("コマンド定義と一覧が一致しません。Botを更新してください。")
        commands_text()
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        if not monitor.is_running():
            monitor.start()


bot = CIPIBot(command_prefix="!", intents=discord.Intents.default(),
              allowed_mentions=discord.AllowedMentions.none())


def catalog_command(name):
    _, description, _, admin_only = COMMAND_CATALOG[name]

    async def allowed(interaction):
        if interaction.guild_id != GUILD_ID:
            raise app_commands.CheckFailure("guild")
        if admin_only and not interaction.user.guild_permissions.administrator:
            raise app_commands.CheckFailure("administrator")
        return True

    def decorate(callback):
        callback = app_commands.check(allowed)(callback)
        callback = app_commands.guild_only()(callback)
        if admin_only:
            callback = app_commands.default_permissions(administrator=True)(callback)
        return bot.tree.command(name=name, description=description)(callback)
    return decorate


@bot.tree.error
async def command_error(interaction, error):
    text = ("❌ このサーバーで実行する権限がありません。管理者限定のコマンドもあります。"
            if isinstance(error, app_commands.CheckFailure) else f"❌ {error_text(error)}")
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True)
    else:
        await interaction.response.send_message(text, ephemeral=True)


def gh_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CIPI-Discord-Bot",
    }


async def get_json(url, headers=None):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
        async with s.get(url, headers=headers) as r:
            if r.status != 200:
                raise PublicError(f"GitHubから取得できません（HTTP {r.status}）。設定・権限を確認してください。")
            return await r.json(content_type=None)


async def post_json(url, payload):
    if not GITHUB_TOKEN:
        raise PublicError("CIPI_DISCORD_GITHUB_TOKEN が設定されていません")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
        async with s.post(url, headers=gh_headers(), json=payload) as r:
            if r.status != 204:
                raise PublicError(f"GitHubへの送信に失敗しました（HTTP {r.status}）。GitHub Actionsを確認してください。")


async def project_state(project_id):
    if project_id not in PROJECTS:
        raise PublicError("不明なプロジェクトです")
    return await get_json(f"{RAW}/research/continuity/projects/{project_id}/current.json")


async def dispatch(workflow, inputs=None):
    async with DISPATCH_LOCK:
        if not GITHUB_TOKEN:
            raise PublicError("CIPI_DISCORD_GITHUB_TOKEN が設定されていません")
        if time.monotonic() - LAST_DISPATCH.get(workflow, -float("inf")) < 60:
            raise PublicError("同じ処理を送信済み、または受付状況を確認中です。GitHub Actionsを確認し、少し待ってください。")
        if await workflow_running(workflow):
            raise PublicError("CIPIの同じ処理が実行中です。完了後に状態を確認してください。")
        payload = {"ref": "main"}
        if inputs:
            payload["inputs"] = inputs
        # Reserve before POST: a timeout does not mean GitHub rejected the request.
        LAST_DISPATCH[workflow] = time.monotonic()
        await post_json(f"{API}/actions/workflows/{workflow}/dispatches", payload)


async def workflow_running(workflow):
    if not GITHUB_TOKEN:
        raise PublicError("CIPI_DISCORD_GITHUB_TOKEN が設定されていません")
    for state in ("queued", "in_progress", "waiting", "pending", "requested"):
        data = await get_json(f"{API}/actions/workflows/{workflow}/runs?branch=main&status={state}&per_page=1", gh_headers())
        if not isinstance(data.get("workflow_runs"), list):
            raise PublicError("GitHubの実行状態を確認できないため送信しません。")
        if data["workflow_runs"]:
            return True
    return False


def phase_display(phase):
    return PHASES.get(phase, ("⚫", phase))


def load_alerts():
    try:
        return json.loads(ALERT_STATE.read_text(encoding="utf-8")) if ALERT_STATE.exists() else {}
    except Exception:
        return {}


def save_alerts(value):
    temporary = ALERT_STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(ALERT_STATE)


def find_named(items, names):
    for name in names:
        found = discord.utils.get(items, name=name)
        if found:
            return found
    return None


async def ensure_category(guild, target, old):
    c = find_named(guild.categories, [target, old])
    if c is None:
        c = await guild.create_category(target)
    elif c.name != target:
        await c.edit(name=target)
    return c


async def ensure_text(guild, category, target, old):
    c = find_named(guild.text_channels, [target, old])
    if c is None:
        return await guild.create_text_channel(target, category=category)
    changes = {}
    if c.name != target:
        changes["name"] = target
    if c.category_id != category.id:
        changes["category"] = category
    if changes:
        await c.edit(**changes)
    return c


async def ensure_forum(guild, category, target, old):
    c = find_named(guild.channels, [target, old])
    if c is None or not isinstance(c, discord.ForumChannel):
        c = await guild.create_forum(target, category=category)
    else:
        changes = {}
        if c.name != target:
            changes["name"] = target
        if c.category_id != category.id:
            changes["category"] = category
        if changes:
            await c.edit(**changes)
    existing = list(c.available_tags)
    names = {x.name for x in existing}
    if not (all(x in names for x in FORUM_TAGS) and not any(x in names for x in OLD_TAGS)):
        system = set(FORUM_TAGS + OLD_TAGS)
        custom = [x for x in existing if x.name not in system]
        await c.edit(available_tags=custom + [discord.ForumTag(name=x) for x in FORUM_TAGS])
    return c


async def ensure_structure(guild):
    categories = {}
    for target, old in CATEGORY_SPECS:
        categories[target] = await ensure_category(guild, target, old)
    for category, specs in TEXT_SPECS.items():
        for target, old in specs:
            await ensure_text(guild, categories[category], target, old)
    for category, specs in FORUM_SPECS.items():
        for target, old in specs:
            await ensure_forum(guild, categories[category], target, old)


def status_text(data):
    lines = []
    for item in data.get("projects", []):
        pid = item.get("project_id", "不明")
        icon, label = phase_display(item.get("phase", "UNKNOWN"))
        lines.append(f"{icon} **{PROJECTS.get(pid, pid)}** — {label}")
    f = data.get("freshness_counts", {})
    return clip_message("\n".join([
        STATUS_TITLE,
        f"最終更新: {data.get('generated_at', '不明')}",
        f"管理数: {data.get('project_count', len(lines))} ｜ 最新 {f.get('FRESH', 0)} ｜ 古い {f.get('STALE', 0)} ｜ 競合 {f.get('CONFLICT', 0)} ｜ 無効 {f.get('INVALID', 0)}",
        "",
        *lines,
    ]))

def project_text(data):
    pid = data.get("project_id", "不明")
    icon, label = phase_display(data.get("phase", "UNKNOWN"))
    work = data.get("work", {})
    resume = data.get("resume_contract", {})
    lines = [
        f"## 🎛️ {PROJECTS.get(pid, pid)}", f"{icon} 状態: **{label}**",
        f"鮮度: {data.get('freshness', 'UNKNOWN')}", "",
        "### 📊 作業",
        f"準備完了: {work.get('ready_count', 0)}",
        f"ブロック: {work.get('blocked_count', 0)}",
        f"人間確認: {work.get('human_gate_count', 0)}", "",
        "### ▶️ 再開判定",
        f"再開可能: {resume.get('can_resume', False)}",
        f"自動再開可能: {resume.get('can_autonomously_resume', False)}",
        f"推奨: {resume.get('recommended_action', '不明')}",
    ]
    deps = resume.get("blocked_dependencies", [])
    if deps:
        lines += ["", "### 🟡 未解決の依存"] + [f"• {x}" for x in deps[:8]]
    return clip_message("\n".join(lines))

def human_gate_text(data):
    pid = data.get("project_id", "不明")
    lines = [f"## 🔴 {PROJECTS.get(pid, pid)}｜人間確認ゲート", f"世代ID: {data.get('generation_id', '不明')}", ""]
    gates = data.get("human_gates", [])
    if not gates:
        return "\n".join(lines + ["✅ 現在、人間確認が必要なゲートはありません。"])
    for item in gates:
        source = item.get("source", "UNKNOWN")
        target = item.get("job_id") or item.get("track_id") or "不明"
        source_label = "研究ジョブ" if source == "RESEARCH_JOB" else "自動研究トラック"
        effect = "完了でContinuityへ反映" if source == "RESEARCH_JOB" else "決定記録のみ・自動再開なし"
        lines += [
            f"### {target}",
            f"種類: {source_label}",
            f"状態: {'🚨 ブロック中' if item.get('blocking') else '⏳ 将来ゲート'}",
            f"反映: {effect}",
        ]
        lines += [f"• {g}" for g in item.get("gates", [])]
        lines.append("")
    return clip_message("\n".join(lines))


async def upsert_message(channel, title, text):
    async with MESSAGE_LOCK:
        key = (channel.id, title)
        message = None
        if key in MESSAGE_IDS:
            try:
                candidate = await channel.fetch_message(MESSAGE_IDS[key])
                if candidate.author == bot.user and candidate.content.splitlines()[:1] == [title]:
                    message = candidate
            except discord.NotFound:
                MESSAGE_IDS.pop(key, None)
        if message is None:
            # Search all history, including a message buried by >30 later posts.
            # Permission/network errors must propagate: never send on failed lookup.
            async for candidate in channel.history(limit=None, oldest_first=True):
                if candidate.author == bot.user and candidate.content.splitlines()[:1] == [title]:
                    message = candidate
                    break
        if message is None:
            message = await channel.send(text, allowed_mentions=discord.AllowedMentions.none())
        elif message.content != text:
            await message.edit(content=text, allowed_mentions=discord.AllowedMentions.none())
        MESSAGE_IDS[key] = message.id


async def update_commands_channel():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        raise PublicError("設定されたDiscordサーバーを確認できません。")
    category = await ensure_category(guild, *CATEGORY_SPECS[0])
    channel = await ensure_text(guild, category, "コマンド", "command")
    await upsert_message(channel, COMMAND_TITLE, commands_text())

async def update_status_channel(data):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    channel = find_named(guild.text_channels, ["cipi状況", "cipi-status"])
    if not channel:
        return
    await upsert_message(channel, STATUS_TITLE, status_text(data))


async def update_alerts(data):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    channel = find_named(guild.text_channels, ["警告", "alerts"])
    if not channel:
        return
    old = load_alerts()
    for item in data.get("projects", []):
        pid = item.get("project_id", "不明")
        name = PROJECTS.get(pid, pid)
        phase = item.get("phase", "UNKNOWN")
        prev = old.get(pid)
        if phase == prev:
            continue
        if phase == "BLOCKED":
            await channel.send(f"🟡 **ブロック発生**\n{name} がブロック中になりました。")
        elif phase == "HUMAN_GATE":
            await channel.send(f"🔴 **人間の確認が必要です**\n{name} が人間の確認待ちになりました。")
        elif prev in {"BLOCKED", "HUMAN_GATE"}:
            await channel.send(f"✅ **警告解除**\n{name} の警告が解除されました。現在: {phase_display(phase)[1]}")
        # Persist each successful item so a later send failure cannot replay it.
        old[pid] = phase
        save_alerts(old)

async def sync_once(configure_guild=None):
    async with SYNC_LOCK:
        errors = []
        if configure_guild is not None:
            await ensure_structure(configure_guild)
        try:
            await update_commands_channel()
        except Exception as e:
            errors.append("コマンド一覧: " + error_text(e))
        try:
            data = await get_json(STATUS_URL)
            await update_status_channel(data)
            await update_alerts(data)
        except Exception as e:
            errors.append("CIPI状態: " + error_text(e))
        print("CIPI同期完了" if not errors else "CIPI同期エラー: " + " / ".join(errors))
        return errors


@tasks.loop(minutes=5)
async def monitor():
    await sync_once()


@monitor.before_loop
async def before_monitor():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"CIPI管理Bot オンライン: {bot.user}")
    # monitor performs the first sync after readiness, then every five minutes.


@catalog_command("ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 CIPI管理Botは正常に稼働しています", ephemeral=True)


@catalog_command("status")
async def status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(status_text(await get_json(STATUS_URL)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ CIPI接続エラー: {error_text(e)}", ephemeral=True)


@catalog_command("project")
@app_commands.choices(project=PROJECT_CHOICES)
async def project_command(interaction: discord.Interaction, project: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(project_text(await project_state(project.value)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ プロジェクト取得エラー: {error_text(e)}", ephemeral=True)


@catalog_command("human-gate")
@app_commands.choices(project=PROJECT_CHOICES)
async def human_gate_command(interaction: discord.Interaction, project: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(human_gate_text(await project_state(project.value)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Human Gate取得エラー: {error_text(e)}", ephemeral=True)


@catalog_command("gate-decision")
@app_commands.choices(project=PROJECT_CHOICES, target_type=TARGET_CHOICES, outcome=OUTCOME_CHOICES)
@app_commands.describe(
    target_id="human-gate に表示されたジョブまたはトラックID",
    gate="human-gate に表示されたゲート名",
    evidence_ref="公開してよいAB結果・ログ等の参照。秘密情報は禁止",
    rationale="判断理由。10文字以上",
)
async def gate_decision(
    interaction: discord.Interaction,
    project: app_commands.Choice[str],
    target_type: app_commands.Choice[str],
    target_id: str,
    gate: str,
    outcome: app_commands.Choice[str],
    evidence_ref: str,
    rationale: str,
):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        return await interaction.followup.send("❌ 管理者のみ実行できます。", ephemeral=True)
    if len(rationale.strip()) < 10 or len(evidence_ref.strip()) < 3:
        return await interaction.followup.send("❌ 判断理由は10文字以上、確認根拠も入力してください。", ephemeral=True)
    if not GITHUB_TOKEN:
        return await interaction.followup.send("❌ GitHubトークンが読み込まれていません。", ephemeral=True)
    try:
        for value in (target_id, gate, evidence_ref, rationale):
            validate_public_input(value)
        data = await project_state(project.value)
        if data.get("freshness") != "FRESH":
            return await interaction.followup.send("⚠️ Continuityが最新ではないため記録しません。", ephemeral=True)
        found = any(
            item.get("source") == target_type.value
            and str(item.get("job_id") or item.get("track_id") or "") == target_id
            and gate in [str(x) for x in item.get("gates", [])]
            for item in data.get("human_gates", [])
        )
        if not found:
            return await interaction.followup.send("❌ 現在のHuman Gateにその対象がありません。/human-gate を再確認してください。", ephemeral=True)
        await dispatch(HUMAN_GATE_WORKFLOW, {
            "project_id": project.value,
            "target_type": target_type.value,
            "target_id": target_id,
            "gate": gate,
            "outcome": outcome.value,
            "evidence_ref": evidence_ref.strip(),
            "rationale": rationale.strip(),
            "actor": "discord-human-reviewer",
            "source": "DISCORD",
            "source_generation_id": data["generation_id"],
            "source_state_digest": data["source_state_digest"],
        })
        if target_type.value == "RESEARCH_JOB" and outcome.value == "COMPLETE":
            effect = "完了後にContinuityとGlobal DAGを再評価します。"
        elif target_type.value == "AUTONOMOUS_TRACK":
            effect = "決定は記録しますが、自動研究トラックは自動再開しません。"
        else:
            effect = "決定記録を保存します。"
        await interaction.followup.send(
            clip_message(f"✅ Human Gate Decisionを送信しました。\n"
            f"対象: {target_id}\n"
            f"ゲート: {gate}\n"
            f"判断: {outcome.name}\n\n"
            f"{effect}"),
            ephemeral=True,
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Human Gate送信エラー: {error_text(e)}", ephemeral=True)


@catalog_command("continue")
@app_commands.choices(project=PROJECT_CHOICES)
async def continue_project(interaction: discord.Interaction, project: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        data = await project_state(project.value)
        name = PROJECTS.get(project.value, project.value)
        resume = data.get("resume_contract", {})
        if data.get("freshness") != "FRESH":
            return await interaction.followup.send(f"⚠️ {name} のContinuityが最新ではありません。", ephemeral=True)
        if data.get("phase") == "HUMAN_GATE" or resume.get("resume_mode") == "HUMAN_GATE":
            return await interaction.followup.send(f"🔴 {name} は人間確認待ちです。/human-gate を確認してください。", ephemeral=True)
        deps = resume.get("blocked_dependencies", [])
        if data.get("phase") == "BLOCKED" or (deps and not resume.get("can_autonomously_resume", False)):
            text = f"🟡 {name} は依存関係待ちです。"
            if deps:
                text += "\n" + "\n".join(f"• {x}" for x in deps[:8])
            return await interaction.followup.send(clip_message(text), ephemeral=True)
        if not resume.get("can_resume", False) or not resume.get("can_autonomously_resume", False):
            return await interaction.followup.send(f"⚠️ {name} は現在、自動再開条件を満たしていません。", ephemeral=True)
        if not GITHUB_TOKEN:
            return await interaction.followup.send("❌ GitHubトークンが読み込まれていません。", ephemeral=True)
        await dispatch(GLOBAL_DAG)
        await interaction.followup.send(f"🟢 {name} の再開要求をCIPIへ送りました。Global DAGが再評価します。", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 再開処理エラー: {error_text(e)}", ephemeral=True)


@catalog_command("setup")
async def setup(interaction: discord.Interaction):
    if interaction.guild is None or not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ 管理者のみ実行できます。", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    try:
        errors = await sync_once(configure_guild=interaction.guild)
        message = ("⚠️ 同期が一部未完了です。\n" + "\n".join(errors) if errors else
                   "✅ Discord構成・コマンド一覧・CIPI同期・警告監視を更新しました。")
        await interaction.followup.send(message, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ {error_text(e)}", ephemeral=True)


@catalog_command("commands")
async def commands_command(interaction: discord.Interaction):
    await interaction.response.send_message(commands_text(), ephemeral=True)


def main():
    global GUILD_ID
    if not TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN が設定されていません。環境変数を確認してください。")
    guild_value = os.environ.get("DISCORD_GUILD_ID", "")
    if not guild_value.isascii() or not guild_value.isdecimal() or not 0 < int(guild_value) < 2**64:
        raise SystemExit("DISCORD_GUILD_ID に有効なサーバーIDを設定してください。")
    GUILD_ID = int(guild_value)
    if not GITHUB_TOKEN:
        print("GitHubトークン未設定: 状態確認のみ利用可能です。")
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
