from ..bot import ChatBot


def handle_public_command(message, bot: ChatBot):
    text = message.content.strip()
    if text.startswith("!!/ping"):
        bot.reply_to_chat(message, "Flashpoint 🔥 is alive and guarding.")
    elif text.startswith("!!/help"):
        bot.reply_to_chat(message, "Commands: ping, help, status, quota, uptime, last, scan, why, whois, test")
    elif text.startswith("!!/status"):
        bot.reply_to_chat(message, f"Status: Active | Scanned: {bot.scanned_count} | Alerts: {bot.alert_count} | Quota: {bot.quota_remaining}")
    elif text.startswith("!!/quota"):
        bot.reply_to_chat(message, f"Quota remaining: {bot.quota_remaining}")
    elif text.startswith("!!/uptime"):
        hours, minutes, seconds = bot.get_uptime()
        bot.reply_to_chat(message, f"Uptime: {hours}h {minutes}m {seconds}s")
    elif text.startswith("!!/last"):
        bot.reply_to_chat(message, f"Last alert: {bot.last_alert_link}")
