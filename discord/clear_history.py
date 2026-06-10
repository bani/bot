"""Delete old messages from a channel, then exit. Dry run by default.

Replaces the old clear_old.py and clear_birthday.py scripts:
    clear_old.py:      python clear_history.py --bot CALENDAR --channel ALTCAL --days 7 --author SELF --apply
    clear_birthday.py: python clear_history.py --bot CALENDAR --channel BIRTH --days 1 --author BIRTH

Pinned messages are always kept.
"""

import argparse
import asyncio
import logging
from datetime import timedelta

from discord.utils import utcnow

import bot_common
from constants import Channel, User

log = logging.getLogger("bot.clear_history")


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bot", default="NOTBANI",
                        help="env var holding the bot token (default: %(default)s)")
    parser.add_argument("--channel", default="TMP",
                        help="constants.Channel name to clear (default: %(default)s)")
    parser.add_argument("--days", type=float, default=7,
                        help="only touch messages older than this many days "
                             "(default: %(default)s)")
    parser.add_argument("--author", default="SELF",
                        help="only delete messages by this author: SELF (this bot), "
                             "ANY, or a constants.User name (default: %(default)s)")
    parser.add_argument("--limit", type=int, default=100,
                        help="maximum number of history messages to scan "
                             "(default: %(default)s)")
    parser.add_argument("--apply", action="store_true",
                        help="actually delete (default: dry run, list only)")
    return parser.parse_args()


def main():
    args = parse_args()
    client = bot_common.make_client()
    channel_id = bot_common.constant(Channel, args.channel)
    author_id = None
    if args.author not in ("SELF", "ANY"):
        author_id = bot_common.constant(User, args.author)

    def author_matches(message):
        if args.author == "SELF":
            return message.author == client.user
        if args.author == "ANY":
            return True
        return message.author.id == author_id

    async def clear():
        channel = client.get_channel(channel_id)
        if channel is None:
            log.error("Channel %s not found", args.channel)
            return

        cutoff = utcnow() - timedelta(days=args.days)
        matched = 0
        async for message in channel.history(before=cutoff, limit=args.limit):
            if message.pinned or not author_matches(message):
                continue
            matched += 1
            if args.apply:
                log.info("Deleting: %s %s", message.author.name, message.content)
                await message.delete()
                await asyncio.sleep(1)
            else:
                log.info("Would delete: %s %s", message.author.name, message.content)

        log.info("%d message(s) %s.", matched,
                 "deleted" if args.apply else "matched (dry run)")

    bot_common.run_once(client, args.bot, clear)


if __name__ == "__main__":
    main()
