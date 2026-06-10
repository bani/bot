"""List a guild's scheduled events; optionally shift their start times.

By default this is a dry run that only lists the events. To actually shift
them (e.g. for daylight saving time):
    python edit_events.py --apply --shift-hours 1 --skip 1436460393546514615
"""

import argparse
import logging
from datetime import timedelta

import discord
import pytz

import bot_common
from constants import Server

log = logging.getLogger("bot.edit_events")

EASTERN = pytz.timezone("US/Eastern")


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bot", default="NOTBANI",
                        help="env var holding the bot token (default: %(default)s)")
    parser.add_argument("--guild", default="MINDFULNESS",
                        help="constants.Server name (default: %(default)s)")
    parser.add_argument("--shift-hours", type=int, default=1,
                        help="hours to shift event start times by (default: %(default)s)")
    parser.add_argument("--skip", type=int, nargs="*", default=[], metavar="EVENT_ID",
                        help="event ids to leave untouched")
    parser.add_argument("--apply", action="store_true",
                        help="actually edit the events (default: list only)")
    return parser.parse_args()


def main():
    args = parse_args()
    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_scheduled_events = True
    client = discord.Client(intents=intents)
    guild_id = bot_common.constant(Server, args.guild)

    async def edit_events():
        guild = client.get_guild(guild_id)
        if guild is None:
            log.error("Guild %s not found", args.guild)
            return

        for event in guild.scheduled_events:
            local_start = event.start_time.astimezone(EASTERN)
            log.info("- %s: %s - %s", event.name,
                     local_start.strftime('%A, %I %p %Z'), event.id)

        if not args.apply:
            log.info("Dry run; pass --apply to shift events by %d hour(s).",
                     args.shift_hours)
            return

        for event in guild.scheduled_events:
            if event.id in args.skip:
                log.info("Skipping %s", event.name)
                continue
            new_start_time = event.start_time + timedelta(hours=args.shift_hours)
            await event.edit(start_time=new_start_time,
                             end_time=new_start_time + timedelta(hours=1))
            log.info("Shifted %s to %s", event.name,
                     new_start_time.astimezone(EASTERN).strftime('%A, %I %p %Z'))

    bot_common.run_once(client, args.bot, edit_events)


if __name__ == "__main__":
    main()
