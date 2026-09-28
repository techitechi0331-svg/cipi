# CIPI Discord Bot

CIPIの状態表示・警告・再開要求・Human Gate確認/決定をDiscordから扱う管理Botです。

## Windows更新

既存のローカルBotを最新版へ置き換える:

    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/techitechi0331-svg/cipi/main/integrations/discord/bot.py" -OutFile "$HOME\CIPI-Discord-Bot\bot.py"

起動:

    cd $HOME\CIPI-Discord-Bot
    py -3.13 bot.py

必要な環境変数:

- DISCORD_BOT_TOKEN
- DISCORD_GUILD_ID
- CIPI_DISCORD_GITHUB_TOKEN

GitHub Fine-grained tokenはCIPIリポジトリのActions: Read and writeのみで運用する。

## 主なコマンド

- /ping
- /setup
- /status
- /project
- /continue
- /human-gate
- /gate-decision

## Human Gate安全境界

- Discordから送信した決定はGitHub ActionsのHuman Gate Decision workflow経由でappend-only記録する。
- Continuityのgeneration_idとsource_state_digestを照合し、古い画面からの決定はfail closedする。
- RESEARCH_JOBのCOMPLETEだけが当該ゲートをContinuity上で解決済みにする。
- AUTONOMOUS_TRACKの決定は監査記録のみ。停止済み研究トラックを自動再開しない。
- Human Gate決定だけで製品書き込み、知識PROMOTE、リリース承認を行わない。
