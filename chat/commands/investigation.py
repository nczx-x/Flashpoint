import re
from ..bot import ChatBot


def handle_investigation_command(message, bot: ChatBot):
    text = message.content.strip()
    if text.startswith("!!/scan "):
        try:
            match = re.search(r"/a/(\d+)|/answers/(\d+)", text)
            post_id = match.group(1) or match.group(2)
            ans = bot.fetch_answers_by_id(post_id)
            if ans.get("items"):
                score, reasons = bot.scan_answer(ans["items"][0])
                bot.reply_to_chat(message, f"Manual scan /a/{post_id}: {score} | {', '.join(reasons)}")
            else:
                bot.reply_to_chat(message, "Answer not found.")
        except Exception:
            bot.reply_to_chat(message, "Invalid scan link.")
    elif text.startswith("!!/why "):
        try:
            match = re.search(r"/a/(\d+)", text)
            post_id = match.group(1)
            ans = bot.fetch_answers_by_id(post_id)
            if ans.get("items"):
                score, reasons = bot.scan_answer(ans["items"][0])
                bot.reply_to_chat(message, f"Diagnostic /a/{post_id}: {score} | {', '.join(reasons)}")
            else:
                bot.reply_to_chat(message, "Could not analyze that answer.")
        except Exception:
            bot.reply_to_chat(message, "Usage: !!/why https://stackoverflow.com/a/<id>")
    elif text.startswith("!!/whois "):
        user_id = text.split()[1]
        try:
            u = bot.fetch_user(user_id)
            if u.get("items"):
                user = u["items"][0]
                bot.reply_to_chat(message, f"User {user_id}: {user['display_name']} | Rep {user['reputation']}")
        except Exception:
            bot.reply_to_chat(message, "Could not fetch user.")
    elif text.startswith("!!/test "):
        if bot.is_admin(message.user.id):
            test_text = text[8:]
            score, reasons = bot.scan_answer({"body": test_text, "owner": {"reputation": 1}})
            bot.reply_to_chat(message, f"Test score: {score} | {', '.join(reasons)}")
        else:
            bot.reply_to_chat(message, "Admin-only command.")
