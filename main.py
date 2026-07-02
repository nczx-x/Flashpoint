import time
from datetime import datetime
from .chat.bot import ChatBot
from .scanner import scan_answer

def run():
    bot = ChatBot()
    bot.connect()
    bot.start_listener()
    last_check = int(time.time()) - 300
    while True:
        print(f"Checking for new answers since {datetime.fromtimestamp(last_check)}...")
        try:
            answers = bot.fetch_answers(last_check)
            bot.quota_remaining = answers.get("quota_remaining", 0)
            print(f"Current Quota: {bot.quota_remaining}")
            if answers.get("items"):
                for answer in answers["items"]:
                    if answer["creation_date"] <= last_check:
                        continue
                    ai_score, reasons = scan_answer(answer)
                    bot.scanned_count += 1
                    if ai_score >= bot.ai_threshold:
                        bot.alert_answer(answer, ai_score, reasons)
                last_check = answers["items"][0]["creation_date"]
        except Exception as error:
            print(f"Error fetching from API: {error}")
        time.sleep(60)

if __name__ == "__main__":
    run()
