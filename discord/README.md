# Discord bot scripts

Small standalone scripts for Discord tasks. Shared boilerplate (token
loading, client setup, DM logging, run-once helper) lives in
[bot_common.py](bot_common.py); server/channel/user ids in
[constants.py](constants.py); iCal parsing in
[calendar_parser.py](calendar_parser.py).

Run everything with the project venv: `../env/bin/python <script>`.

## Safety defaults

Every script defaults to `--bot NOTBANI` (test bot, posts only to
BANIVERSE/TMP) and dry-run where applicable. Production needs explicit
flags: `--bot CALENDAR` for the production token, `--apply` for anything
destructive. Bot tokens live in `.env` (not committed).

## Scripts

| Script | What it does |
|---|---|
| `schedule_post.py` | Daily calendar post. Long-running. |
| `event_update.py` | Post a one-off announcement embed, then exit. |
| `edit_events.py` | List (and optionally time-shift) a guild's scheduled events, then exit. |
| `clear_history.py` | Delete old messages from a channel, then exit. Dry run by default. |
| `clear.py` | Long-running bot with a `/clear` slash command (purge >7d old messages). |
| `chatgpt.py` | Long-running bot answering the TMP channel via OpenAI. |

Each script's docstring (`--help`) has the details. Common invocations:

```sh
# Calendar: testing (posts to TMP immediately, then every 24h)
python schedule_post.py --post

# Calendar: production (posts daily at 10am Eastern; DST handled automatically)
python schedule_post.py --post --at 10:00 --bot CALENDAR --channel ALTCAL

# Announcement to the real channel
python event_update.py --bot CALENDAR --channel ALTCAL

# Shift scheduled events for daylight saving (dry run first, then --apply)
python edit_events.py --guild MINDFULNESS
python edit_events.py --guild MINDFULNESS --apply --shift-hours 1 --skip <event id>

# Old clear_old.py / clear_birthday.py equivalents
python clear_history.py --bot CALENDAR --channel ALTCAL --days 7 --author SELF --apply
python clear_history.py --bot CALENDAR --channel BIRTH --days 1 --author BIRTH --apply
```
