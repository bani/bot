"""Post a one-off announcement embed to a channel, then exit.

Defaults are safe for testing (NOTBANI bot, TMP channel). To post the real
announcement:
    python event_update.py --channel ALTCAL
"""

import argparse
import logging

import discord

import bot_common
from constants import Channel

log = logging.getLogger("bot.event_update")

DEFAULT_MESSAGE = ("The Artificial Buddha with <#1469030252402708654> has concluded. "
                   "New events coming in June.")


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bot", default="NOTBANI",
                        help="env var holding the bot token (default: %(default)s)")
    parser.add_argument("--channel", default="TMP",
                        help="constants.Channel name to post to (default: %(default)s)")
    parser.add_argument("--message", default=DEFAULT_MESSAGE,
                        help="announcement text (default: the message in this script)")
    return parser.parse_args()


def main():
    args = parse_args()
    client = bot_common.make_client()
    channel_id = bot_common.constant(Channel, args.channel)

    async def send_update():
        channel = client.get_channel(channel_id)
        if channel is None:
            raise RuntimeError(f"Channel {args.channel} not found "
                               "(is this bot in that server?)")
        embed = discord.Embed(color=0xFFC107, title="")
        embed.set_author(name="Event Update", url="",
                         icon_url="https://www.emoji.family/api/emojis/1f514/noto/png/128")
        embed.add_field(name="", value=args.message, inline=False)
        await channel.send(embed=embed)
        log.info("Posted update to %s", args.channel)

    bot_common.run_once(client, args.bot, send_update)


if __name__ == "__main__":
    main()
