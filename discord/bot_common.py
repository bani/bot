"""Shared helpers for the Discord task scripts.

Every script follows the same pattern: load a token from .env, create a
client, do some work, and log incoming DMs. This module centralizes that
boilerplate.

Scripts that perform a single action and exit should use run_once();
long-running bots register their own event handlers and call run().
"""

import logging
import os

import discord
from dotenv import load_dotenv

from constants import User

log = logging.getLogger("bot")

# Tokens with access to production channels. Scripts default to NOTBANI,
# which can only post to BANIVERSE/TMP; production requires passing these
# explicitly on the command line.
PROD_BOTS = {"CALENDAR"}


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


def get_token(bot_name):
    """Read the bot token named `bot_name` from the environment/.env."""
    load_dotenv()
    token = os.environ.get(bot_name)
    if not token:
        raise SystemExit(f"No token named {bot_name!r} found in the environment.")
    if bot_name in PROD_BOTS:
        log.warning("Using PRODUCTION bot %s", bot_name)
    return token


def make_client(message_content=True):
    """A discord.Client with the default intents used by these scripts."""
    intents = discord.Intents.default()
    intents.message_content = message_content
    return discord.Client(intents=intents)


def constant(cls, name):
    """Resolve a name like 'TMP' against a constants class, with a clear error."""
    value = getattr(cls, name, None)
    if value is None:
        options = ", ".join(k for k in vars(cls) if not k.startswith("_"))
        raise SystemExit(f"Unknown {cls.__name__} {name!r}; options: {options}")
    return value


def is_dm(message):
    return isinstance(message.channel, discord.DMChannel)


def log_dm(message):
    """Log a DM from anyone who isn't Bani."""
    if message.author.id != User.BANI:
        log.info("DM from %s: %s", message.author.name, message.content)


def run(client, bot_name):
    """Configure logging and run the client with the named bot's token."""
    setup_logging()
    client.run(get_token(bot_name), log_handler=None)


def run_once(client, bot_name, work):
    """Log in, await `work()` once, then disconnect.

    Exits with a nonzero status if `work()` raised, so failures are
    visible to shell scripts and schedulers.
    """
    failed = False

    @client.event
    async def on_ready():
        nonlocal failed
        log.info("Logged in as %s", client.user)
        try:
            await work()
        except Exception:
            failed = True
            log.exception("Task failed")
        finally:
            await client.close()

    run(client, bot_name)
    if failed:
        raise SystemExit(1)
