"""Post the day's calendar events to a Discord channel on a daily loop.

Testing (defaults: NOTBANI bot, TMP channel, posts immediately on startup
and then every 24h):
    python schedule_post.py --post

Production (posts daily at 10am Eastern; DST is handled automatically):
    python schedule_post.py --post --at 10:00 --bot CALENDAR --channel ALTCAL

Without --post the bot only logs in and handles `$del CHANNEL message_id`
DMs from Bani.
"""

import argparse
import datetime
import logging
import os
import re
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

import bot_common
import calendar_parser
from constants import Channel, User

log = logging.getLogger("bot.schedule_post")

DELETE_RE = re.compile(r'\$del ([A-Z]+) (.*)')


EASTERN = ZoneInfo("America/Toronto")


def eastern_time(value):
    """Parse 'HH:MM' into an Eastern-time datetime.time, for argparse."""
    try:
        hour, minute = (int(part) for part in value.split(":"))
        return datetime.time(hour=hour, minute=minute, tzinfo=EASTERN)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected HH:MM, got {value!r}")


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bot", default="NOTBANI",
                        help="env var holding the bot token (default: %(default)s)")
    parser.add_argument("--channel", default="TMP",
                        help="constants.Channel name to post to (default: %(default)s)")
    parser.add_argument("--offset", type=int, default=0,
                        help="day offset from today (default: %(default)s)")
    parser.add_argument("--calendar", default="CALENDAR_URL",
                        help="env var holding the iCal URL (default: %(default)s)")
    parser.add_argument("--post", action="store_true",
                        help="start the daily posting loop")
    parser.add_argument("--at", type=eastern_time, metavar="HH:MM",
                        help="post daily at this Eastern time, e.g. 10:00 (production; "
                             "DST handled automatically); without it, post immediately "
                             "and then every 24h (testing)")
    return parser.parse_args()


def main():
    args = parse_args()
    client = bot_common.make_client()
    channel_id = bot_common.constant(Channel, args.channel)

    async def post_calendar():
        try:
            calendar_url = os.environ.get(args.calendar)
            if not calendar_url:
                log.error("No calendar URL named %s in the environment", args.calendar)
                return
            events, events_date = calendar_parser.get_events(
                calendar_url=calendar_url, offset=args.offset)

            channel = client.get_channel(channel_id)
            if channel is None:
                log.error("Channel %s not found", args.channel)
                return

            if events:
                # %-d (unpadded day) is not portable to Windows, so format manually
                embed = discord.Embed(
                    color=0xFF7D7D,
                    title=f"{events_date.strftime('%B')} {events_date.day}")
                embed.set_thumbnail(
                    url=f"http://baniverso.com/images/bot/wd{events_date.weekday()}.jpeg")
                embed.set_footer(text="Location: VRChat\nTimes displayed in your local timezone")
                for timestamp, title, location in events:
                    embed.add_field(name="\u200B\n" + title,
                                    value=f"<t:{timestamp}:t> in {location}", inline=False)
                await channel.send(embed=embed)
            else:
                await channel.send(f"No events found on {events_date}.")

            log.info("Calendar posted for %s", events_date.strftime('%A, %B %d'))
        except Exception:
            log.exception("Failed to post calendar")

    if args.at:
        calendar_loop = tasks.loop(time=args.at)(post_calendar)
    else:
        calendar_loop = tasks.loop(hours=24)(post_calendar)

    @client.event
    async def on_ready():
        log.info("Logged in as %s", client.user)
        if args.post and not calendar_loop.is_running():
            calendar_loop.start()

    @client.event
    async def on_message(message):
        if message.author == client.user or not bot_common.is_dm(message):
            return
        if message.author.id == User.BANI:
            if message.content.startswith('$del'):
                await delete_message(client, message)
        else:
            bot_common.log_dm(message)

    bot_common.run(client, args.bot)


async def delete_message(client, message):
    try:
        match = DELETE_RE.search(message.content)
        channel = client.get_channel(bot_common.constant(Channel, match[1]))
        msg = await channel.fetch_message(int(match[2]))
        await msg.delete()
    except Exception:
        log.exception("Could not handle %r", message.content)


if __name__ == "__main__":
    main()
