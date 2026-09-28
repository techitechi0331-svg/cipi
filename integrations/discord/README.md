# CIPI Discord Bot

CIPIの状態表示・警告・再開要求・Human Gate確認/決定をDiscordから扱う管理Botです。

## Windows更新

実行中のBotをそのコンソールで `Ctrl+C` で停止してから、一度だけ実行する。
既存の環境変数と Python 3.13 / discord.py 2.7.1 をそのまま利用できる。

```powershell
$ErrorActionPreference = "Stop"
cd "$HOME\CIPI-Discord-Bot"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/techitechi0331-svg/cipi/main/integrations/discord/bot.py" -OutFile ".\bot.py.new"
py -3.13 -m py_compile ".\bot.py.new"
if ($LASTEXITCODE -ne 0) { throw "Botの検証に失敗しました。既存bot.pyは維持されています。" }
Move-Item -LiteralPath ".\bot.py.new" -Destination ".\bot.py" -Force
py -3.13 bot.py
```

必要な環境変数:

- DISCORD_BOT_TOKEN
- DISCORD_GUILD_ID
- CIPI_DISCORD_GITHUB_TOKEN（再開要求・Human Gate決定に必要。未設定でも閲覧可能）

GitHub Fine-grained tokenはCIPIリポジトリのActions: Read and writeのみで運用する。

## コマンドの見つけ方

Discordで `/commands` を実行するか、`🧠 00｜管理 > コマンド` を開く。
全コマンドの日本語説明と「閲覧のみ／変更・実行あり／管理者限定」を表示する。
まず `/status` で全体、`/project` で詳細を確認する。

一覧・Slash Commandの説明・権限制限の正式定義は `bot.py` の `COMMAND_CATALOG`。
コマンド追加時はこの定義を追加し、`@catalog_command("名前")` で登録する。
一覧と登録済みコマンドの不一致・2000文字超過は起動時とテストで検出する。
将来のREADME生成にも `commands_text()` を利用でき、importでBotは起動しない。

### 同期と権限

- 起動後すぐに1回、以降5分ごと、および `/setup` 時にコマンド一覧を同期する。
- 管理カテゴリとコマンドチャンネルがなければ作成し、旧英語名からも移行する。
- 同じBotが投稿した `CIPI Bot コマンド一覧` を履歴から探して編集する。
  状態投稿も同方式で、古い投稿が直近30件の外にあっても再利用する。
  履歴の読み取りに失敗した場合は新規投稿せず、次回同期で再試行する。
- Botにはチャンネルの閲覧・メッセージ履歴の閲覧・送信が必要。
  カテゴリやチャンネルの新規作成・移動、および `/setup` にはチャンネル管理権限も必要。
  `/setup` でフォーラムを作成するサーバーはコミュニティ機能を有効にする。
- `/setup`・`/continue`・`/gate-decision` は管理者限定。全コマンドを設定したサーバー内に限定する。
- Slash Commandの応答は実行者だけに表示し、一覧・状態・警告の自動投稿はチャンネルに表示する。
- 同期を直列化し、起動と再接続による二重処理を防ぐ。Botは1プロセスで運用する。
  警告の既読状態はローカル `alert_state.json` に保持する。研究状態は保存しない。
  このファイルの削除・破損や、Discord送信直後の強制終了では警告が再通知される場合がある。
- Workflow送信は同時実行チェックと60秒の連打抑制を行う。
  POSTのタイムアウトでは自動再送しない。受付済みの可能性があるためGitHub Actionsを確認する。
  連打抑制はプロセス内の一時情報で、再起動後の実行状態はGitHubへ照会する。
  Botを複数起動した場合の厳密な一度だけの送信は保証しない。CIPI側のconcurrencyと検証を維持する。
- GitHubのレスポンス本文・例外詳細・秘密情報はDiscordやログに出さない。
  Human Gate入力も送信前に秘密情報らしい内容を拒否する。Tokenはチャットへ貼らない。

## 検証

```text
python -m pip install -r integrations/discord/requirements.txt PyYAML==6.0.2
python -m py_compile integrations/discord/bot.py
python -m unittest tests.test_discord_bot tests.test_human_gate -v
```

Human Gate ValidationはPython 3.12 / 3.13でBotの登録・権限・同期・障害・決定送信を検証する。
Discord変更時にはContinuity Layer Validation、Auto Research Gate、Research Gateも実行する。
自動テストはDiscord/GitHubへの通信を模擬するため、実サーバーの権限・接続確認は更新後に行う。

## Human Gate安全境界

- Discordから送信した決定はGitHub ActionsのHuman Gate Decision workflow経由でappend-only記録する。
- Continuityのgeneration_idとsource_state_digestを照合し、古い画面からの決定はfail closedする。
- RESEARCH_JOBのCOMPLETEだけが当該ゲートをContinuity上で解決済みにする。
- AUTONOMOUS_TRACKの決定は監査記録のみ。停止済み研究トラックを自動再開しない。
- Human Gate決定だけで製品書き込み、知識PROMOTE、リリース承認を行わない。
