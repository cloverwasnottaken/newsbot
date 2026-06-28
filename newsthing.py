import requests
import feedparser
import json
import os
import re

TOPIC = "3f2c9d6e-8a1b-4c3d-9f2a-91b7c5e2d0aa"
NTFY_URL = f"https://ntfy.sh/{TOPIC}"
SAVE_FILE = "news_multiple.json"

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+OR+artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=tech+automation&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=machine+learning+OR+robotics&hl=en-US&gl=US&ceid=US:en",
]

# ---------------- CLEAN HEADER (ntfy safe) ----------------
def clean_header(text: str) -> str:
    if not text:
        return ""
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:100]

# ---------------- LOAD SEEN URLS ----------------
def load_seen():
    if not os.path.exists(SAVE_FILE):
        return set()
    try:
        with open(SAVE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SAVE_FILE, "w") as f:
        json.dump(list(seen), f)

# ---------------- FETCH NEWS ----------------
def fetch_articles():
    articles = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "")
            url = entry.get("link", "")

            if title and url:
                articles.append({"title": title, "url": url})

    return articles

# ---------------- SEND NTFY ----------------
def send_ntfy(title, url):
    headers = {
        "Title": clean_header(title),
        "Click": url
    }

    message = f"{title}\n\nClick notification to open the URL"

    try:
        requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10
        )
    except Exception as e:
        print("ntfy error:", e)

# ---------------- GET 5 NEW ----------------
def get_five_new(seen):
    articles = fetch_articles()
    selected = []

    for a in articles:
        if a["url"] not in seen:
            selected.append(a)
            seen.add(a["url"])

        if len(selected) == 5:
            break

    return selected, seen

# ---------------- MAIN ----------------
def main():
    seen = load_seen()

    articles, seen = get_five_new(seen)

    if len(articles) < 5:
        print("Not enough new articles.")
    else:
        for a in articles:
            print("Sending:", a["title"])
            send_ntfy(a["title"], a["url"])

    save_seen(seen)

if __name__ == "__main__":
    main()
