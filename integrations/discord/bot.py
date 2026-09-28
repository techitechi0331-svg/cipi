import os
import json
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])
GITHUB_TOKEN = os.environ.get("CIPI_DISCORD_GITHUB_TOKEN", "")

OWNER = "techitechi0331-svg"
REPO = "cipi"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
STATUS_URL = f"{RAW}/research/continuity/global/current.json"
GLOBAL_DAG = "global-dag-orchestrator.yml"
HUMAN_GATE_WORKFLOW = "human-gate-decision.yml"
ALERT_STATE = Path(__file__).with_name("alert_state.json")

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
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        if not monitor.is_running():
            monitor.start()


bot = CIPIBot(command_prefix="!", intents=discord.Intents.default())


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
                raise RuntimeError(f"HTTP {r.status}: {(await r.text())[:200]}")
            return await r.json(content_type=None)


async def post_json(url, payload):
    if not GITHUB_TOKEN:
        raise RuntimeError("CIPI_DISCORD_GITHUB_TOKEN が設定されていません")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
        async with s.post(url, headers=gh_headers(), json=payload) as r:
            if r.status != 204:
                raise RuntimeError(f"HTTP {r.status}: {(await r.text())[:300]}")


async def project_state(project_id):
    if project_id not in PROJECTS:
        raise ValueError("不明なプロジェクトです")
    return await get_json(f"{RAW}/research/continuity/projects/{project_id}/current.json")


async def dispatch(workflow, inputs=None):
    payload = {"ref": "main"}
    if inputs:
        payload["inputs"] = inputs
    await post_json(f"{API}/actions/workflows/{workflow}/dispatches", payload)


async def workflow_running(workflow):
    if not GITHUB_TOKEN:
        return False
    data = await get_json(f"{API}/actions/workflows/{workflow}/runs?branch=main&per_page=10", gh_headers())
    return any(x.get("status") in {"queued", "in_progress"} for x in data.get("workflow_runs", []))


def phase_display(phase):
    return PHASES.get(phase, ("⚫", phase))


def load_alerts():
    try:
        return json.loads(ALERT_STATE.read_text(encoding="utf-8")) if ALERT_STATE.exists() else {}
    except Exception:
        return {}


def save_alerts(value):
    ALERT_STATE.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


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
    return "\n".join([
        "## 🧠 CIPI 開発状況",
        f"最終更新: {data.get('generated_at', '不明')}",
        f"管理数: {data.get('project_count', len(lines))} ｜ 最新 {f.get('FRESH', 0)} ｜ 古い {f.get('STALE', 0)} ｜ 競合 {f.get('CONFLICT', 0)} ｜ 無効 {f.get('INVALID', 0)}",
        "",
        *lines,
    ])

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
    return "\n".join(lines)[:1900]

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
    return "\n".join(lines)[:1900]

async def update_status_channel(data):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    channel = find_named(guild.text_channels, ["cipi状況", "cipi-status"])
    if not channel:
        return
    text = status_text(data)
    async for msg in channel.history(limit=30):
        if msg.author == bot.user and msg.content.startswith("## 🧠 CIPI"):
            if msg.content != text:
                await msg.edit(content=text)
            return
    await channel.send(text)


async def update_alerts(data):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    channel = find_named(guild.text_channels, ["警告", "alerts"])
    if not channel:
        return
    old = load_alerts()
    new = {}
    for item in data.get("projects", []):
        pid = item.get("project_id", "不明")
        name = PROJECTS.get(pid, pid)
        phase = item.get("phase", "UNKNOWN")
        prev = old.get(pid)
        new[pid] = phase
        if phase == prev:
            continue
        if phase == "BLOCKED":
            await channel.send(f"🟡 **ブロック発生**\n{name} がブロック中になりました。")
        elif phase == "HUMAN_GATE":
            await channel.send(f"🔴 **人間の確認が必要です**\n{name} が人間の確認待ちになりました。")
        elif prev in {"BLOCKED", "HUMAN_GATE"}:
            await channel.send(f"✅ **警告解除**\n{name} の警告が解除されました。現在: {phase_display(phase)[1]}")
    save_alerts(new)

async def sync_once():
    try:
        data = await get_json(STATUS_URL)
        await update_status_channel(data)
        await update_alerts(data)
        print("CIPI同期完了")
    except Exception as e:
        print(f"CIPI同期エラー: {e}")


@tasks.loop(minutes=5)
async def monitor():
    await sync_once()


@monitor.before_loop
async def before_monitor():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"CIPI管理Bot オンライン: {bot.user}")
    await sync_once()


@bot.tree.command(name="ping", description="CIPI管理Botの動作確認")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 CIPI管理Botは正常に稼働しています")


@bot.tree.command(name="status", description="CIPI全体の現在状況を表示")
async def status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(status_text(await get_json(STATUS_URL)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ CIPI接続エラー: {e}", ephemeral=True)


@bot.tree.command(name="project", description="指定プロジェクトの詳細状況を表示")
@app_commands.choices(project=PROJECT_CHOICES)
async def project_command(interaction: discord.Interaction, project: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(project_text(await project_state(project.value)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ プロジェクト取得エラー: {e}", ephemeral=True)


@bot.tree.command(name="human-gate", description="指定プロジェクトの人間確認ゲートを表示")
@app_commands.choices(project=PROJECT_CHOICES)
async def human_gate_command(interaction: discord.Interaction, project: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        await interaction.followup.send(human_gate_text(await project_state(project.value)), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Human Gate取得エラー: {e}", ephemeral=True)


@bot.tree.command(name="gate-decision", description="Human Gateの結果をCIPIへ正式記録")
@app_commands.choices(project=PROJECT_CHOICES, target_type=TARGET_CHOICES, outcome=OUTCOME_CHOICES)
@app_commands.describe(
    target_id="human-gate に表示されたジョブまたはトラックID",
    gate="human-gate に表示されたゲート名",
    evidence_ref="AB結果・ログ・ファイルなどの確認根拠",
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
            "actor": f"discord:{interaction.user.id}",
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
            f"✅ Human Gate Decisionを送信しました。\n"
            f"対象: {target_id}\n"
            f"ゲート: {gate}\n"
            f"判断: {outcome.name}\n\n"
            f"{effect}",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Human Gate送信エラー: {e}", ephemeral=True)


@bot.tree.command(name="continue", description="CIPIの安全条件を確認して再開を要求")
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
            return await interaction.followup.send(text[:1900], ephemeral=True)
        if not resume.get("can_resume", False) or not resume.get("can_autonomously_resume", False):
            return await interaction.followup.send(f"⚠️ {name} は現在、自動再開条件を満たしていません。", ephemeral=True)
        if not GITHUB_TOKEN:
            return await interaction.followup.send("❌ GitHubトークンが読み込まれていません。", ephemeral=True)
        if await workflow_running(GLOBAL_DAG):
            return await interaction.followup.send("🔵 CIPI Orchestratorはすでに実行中です。二重起動しません。", ephemeral=True)
        await dispatch(GLOBAL_DAG)
        await interaction.followup.send(f"🟢 {name} の再開要求をCIPIへ送りました。Global DAGが再評価します。", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 再開処理エラー: {e}", ephemeral=True)


@bot.tree.command(name="setup", description="CIPI開発用Discordを構成・日本語化")
async def setup(interaction: discord.Interaction):
    if interaction.guild is None or not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ 管理者のみ実行できます。", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    await ensure_structure(interaction.guild)
    await sync_once()
    await interaction.followup.send("✅ Discord構成・日本語化・CIPI同期・警告監視を更新しました。", ephemeral=True)


bot.run(TOKEN)
