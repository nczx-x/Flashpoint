import re
from .admin import handle_admin_command
from .public import handle_public_command
from .investigation import handle_investigation_command


def handle_message(message, bot):
    text = message.content.strip()
    if text.startswith("!!/"):
        if any(text.startswith(cmd) for cmd in ("!!/threshold", "!!/die")):
            return handle_admin_command(message, bot)
        if any(text.startswith(cmd) for cmd in ("!!/ping", "!!/help", "!!/status", "!!/quota", "!!/uptime", "!!/last")):
            return handle_public_command(message, bot)
        if any(text.startswith(cmd) for cmd in ("!!/scan", "!!/why", "!!/whois", "!!/test")):
            return handle_investigation_command(message, bot)
    return None
