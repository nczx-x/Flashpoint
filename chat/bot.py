import os
import re
import time
import requests
import threading
import chatexchange
from requests.exceptions import HTTPError
from ..settings import SE_EMAIL, SE_PASSWORD, ROOM_ID, CHAT_HOST, SITE, ADMIN_IDS
from ..scanner import AI_PHRASES, scan_answer

class ChatBot:
    def __init__(self):
        self.client = None
        self.room = None
        self.scanned_count = 0
        self.alert_count = 0
        self.quota_remaining = 0
        self.ai_threshold = 35
        self.last_alert_link = "None"
        self.start_time = time.time()
        # Do not include personal admin IDs in the public copy.
        # Use `ADMIN_IDS` from settings if provided, otherwise default to empty set.
        try:
            self.admin_ids = set(ADMIN_IDS) if ADMIN_IDS is not None else set()
        except Exception:
            self.admin_ids = set()
        self.chat_send_enabled = True

    def is_admin(self, user_id):
        try:
            return int(user_id) in self.admin_ids
        except Exception:
            return False

    def normalize_user_id(self, user_id):
        try:
            return int(user_id)
        except Exception:
            return user_id

    def connect(self):
        self.client = chatexchange.Client(CHAT_HOST)
        self.client.login(SE_EMAIL, SE_PASSWORD)
        self.room = self.client.get_room(ROOM_ID)
        try:
            self.room.join()
        except KeyError as e:
            if not (e.args and e.args[0] == 'time'):
                raise
        room_key = str(ROOM_ID)
        if room_key not in self.client._br.rooms:
            self.client._br.rooms[room_key] = {}
        if 'eventtime' not in self.client._br.rooms[room_key]:
            try:
                response = self.client._br.post_fkeyed(
                    f'chats/{ROOM_ID}/events',
                    {'since': 0, 'mode': 'Messages', 'msgCount': 100}
                )
                eventtime = response.json().get('time')
                if eventtime is None:
                    eventtime = int(time.time())
                self.client._br.rooms[room_key]['eventtime'] = eventtime
            except Exception:
                self.client._br.rooms[room_key]['eventtime'] = int(time.time())
        try:
            self.room.watch_polling(lambda activity, client: None, 60)
        except Exception:
            pass

    def send_message(self, text):
        if not self.chat_send_enabled:
            raise RuntimeError("Chat sending is disabled")
        if self.room is not None and hasattr(self.room, 'send_message'):
            try:
                self.room.send_message(text)
                return
            except Exception:
                pass
        if self.client is None:
            raise RuntimeError("Chat client is not initialized")
        try:
            response = self.client._br.send_message(ROOM_ID, text)
            response.raise_for_status()
        except HTTPError as ex:
            if ex.response is not None and ex.response.status_code == 401:
                response_text = ex.response.text or ""
                if "confirm that you" in response_text.lower() or "human verification" in response_text.lower():
                    self.chat_send_enabled = False
                    raise RuntimeError("Chat sending disabled because the account requires human verification.") from ex
                try:
                    self.client._br._update_chat_fkey_and_user()
                    response = self.client._br.send_message(ROOM_ID, text)
                    response.raise_for_status()
                except Exception as retry_ex:
                    raise RuntimeError(f"Failed to send chat message after refresh: {retry_ex}") from retry_ex
            else:
                raise

    def reply_to_chat(self, message, text):
        username = None
        if message is not None and getattr(message, 'user', None) is not None:
            username = getattr(message.user, 'name', None)
        if username:
            text = f"@{username} {text}"
        self.send_message(text)

    def start_listener(self):
        if self.room is None:
            raise RuntimeError("Room is not initialized")
        listener_thread = threading.Thread(
            target=lambda: self.room.watch(lambda event, client: self.on_message(event, self.room, client)),
            daemon=True
        )
        listener_thread.start()

    def on_message(self, message, room, client):
        if self.normalize_user_id(message.user.id) == self.normalize_user_id(client.get_me().id):
            return
        content = message.content
        if content.startswith("!!/ping"):
            self.reply_to_chat(message, "Flashpoint 🔥 is alive and guarding.")
        elif content.startswith("!!/help"):
            self.reply_to_chat(message, "Flashpoint 🔥 Commands: ping, status, stats, rules, scan <link>, whois <id>, test <text>, help")
        elif content.startswith("!!/status"):
            self.reply_to_chat(message, f"Flashpoint 🔥 Status: Active | Heuristics: SpaCy + Regex | Mode: Sandbox | Scanned: {self.scanned_count} | Alerts: {self.alert_count} | Quota: {self.quota_remaining}")
        elif content.startswith("!!/test ") and self.is_admin(message.user.id):
            test_text = content[8:]
            score, reasons = scan_answer({'body': test_text, 'owner': {'reputation': 1}})
            self.reply_to_chat(message, f"Test Results: Score {score} | Reasons: {', '.join(reasons)}")
        elif content.startswith("!!/rules"):
            rules_list = ", ".join(AI_PHRASES[:10])
            self.reply_to_chat(message, f"Active Heuristic Phrases: {rules_list} ... and structural SpaCy analysis.")
        elif content.startswith("!!/scan "):
            try:
                match = re.search(r'/a/(\d+)|/answers/(\d+)', content)
                if not match:
                    raise ValueError
                post_id = match.group(1) or match.group(2)
                ans = self.fetch_answers_by_id(post_id)
                if ans.get('items'):
                    score, reasons = scan_answer(ans['items'][0])
                    self.reply_to_chat(message, f"Manual Scan for /a/{post_id}: Score {score} | Reasons: {', '.join(reasons)}")
                else:
                    self.reply_to_chat(message, "Could not find that answer ID.")
            except Exception:
                self.reply_to_chat(message, "Invalid link. Use: !!/scan https://stackoverflow.com/a/12345")
        elif content.startswith("!!/whois "):
            user_id = content.split(" ")[1]
            try:
                u = self.fetch_user(user_id)
                if u['items']:
                    user = u['items'][0]
                    self.reply_to_chat(message, f"User {user_id}: {user['display_name']} | Rep: {user['reputation']} | Gold Badges: {user['badge_counts']['gold']}")
            except Exception:
                self.reply_to_chat(message, "Error fetching user data.")
        elif content.startswith("!!/threshold "):
            if self.is_admin(message.user.id):
                try:
                    new_val = int(content.split(" ")[1])
                    if 10 <= new_val <= 95:
                        self.ai_threshold = new_val
                        self.reply_to_chat(message, f"✅ AI Threshold updated to {self.ai_threshold} by authorized admin.")
                    else:
                        self.reply_to_chat(message, "❌ Threshold must be between 10 and 95.")
                except Exception:
                    self.reply_to_chat(message, "Usage: !!/threshold <number>")
            else:
                self.reply_to_chat(message, f"🚫 Access Denied. User {message.user.id} is not authorized to change Flashpoint settings.")
        elif content.startswith("!!/uptime"):
            delta = int(time.time() - self.start_time)
            hours, remainder = divmod(delta, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.reply_to_chat(message, f"Flashpoint 🔥 Uptime: {hours}h {minutes}m {seconds}s")
        elif content.startswith("!!/why "):
            try:
                post_id = re.search(r'/a/(\d+)', content).group(1)
                ans = self.fetch_answers_by_id(post_id)
                score, reasons = scan_answer(ans['items'][0])
                self.reply_to_chat(message, f"Diagnostic for /a/{post_id}: Total Score {score} | Breakdown: {', '.join(reasons)}")
            except Exception:
                self.reply_to_chat(message, "Could not analyze that link. Ensure it's a valid SO answer link.")
        elif content.startswith("!!/last"):
            self.reply_to_chat(message, f"Last Alerted Post: {self.last_alert_link}")
        elif content.startswith("!!/quota"):
            self.reply_to_chat(message, f"Stack Exchange API Quota Remaining: {self.quota_remaining}")
        elif content.startswith("!!/die"):
            if self.is_admin(message.user.id):
                self.reply_to_chat(message, "Flashpoint 🔥 is shutting down. Goodbye, Commander.")
                os._exit(0)
            else:
                self.reply_to_chat(message, "Access Denied. Only my creator can order a shutdown.")

    def fetch_answers(self, last_check):
        return SITE.fetch('answers', fromdate=last_check, sort='creation', order='desc', filter='withbody')

    def fetch_answers_by_id(self, post_id):
        return SITE.fetch('answers', ids=[post_id], filter='withbody')

    def fetch_user(self, user_id):
        return SITE.fetch('users', ids=[user_id])

    def alert_answer(self, answer, ai_score, reasons):
        self.alert_count += 1
        self.last_alert_link = f"https://stackoverflow.com/a/{answer['answer_id']}"
        message = f"⚠️ [Flashpoint | AI Fingerprint Detected (Score: {ai_score})] | Reasons: {', '.join(reasons)} | {self.last_alert_link}"
        print(message)
        try:
            self.send_message(message)
        except Exception as error:
            print(f"❌ ERROR: Could not send message to chat: {error}")
