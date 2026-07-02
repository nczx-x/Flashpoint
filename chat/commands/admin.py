from ..bot import ChatBot


def handle_admin_command(message, bot: ChatBot):
    text = message.content.strip()
    if text.startswith("!!/threshold "):
        try:
            new_val = int(text.split()[1])
            if 10 <= new_val <= 95:
                bot.ai_threshold = new_val
                bot.reply_to_chat(message, f"✅ AI Threshold updated to {bot.ai_threshold}.")
            else:
                bot.reply_to_chat(message, "❌ Threshold must be between 10 and 95.")
        except Exception:
            bot.reply_to_chat(message, "Usage: !!/threshold <number>")
    elif text.startswith("!!/die"):
        if bot.is_admin(message.user.id):
            bot.reply_to_chat(message, "Flashpoint 🔥 is shutting down.")
            raise SystemExit("Shutdown requested by admin")
        bot.reply_to_chat(message, "Access Denied.")
