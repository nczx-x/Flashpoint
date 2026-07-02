import re
from html import unescape


def strip_html(html_text):
    return unescape(re.sub(r"<[^>]+>", "", html_text or "")).strip()


def parse_answer_link(text):
    match = re.search(r"/a/(\d+)|/answers/(\d+)", text)
    return match.group(1) or match.group(2) if match else None
