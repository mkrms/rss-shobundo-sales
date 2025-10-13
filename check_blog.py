import feedparser
import requests
import os
from datetime import datetime

# 設定
RSS_URL = "https://shobundo.biz/blog/feed"
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['セール', 'SALE', 'sale', 'Sale']

def check_feed():
    # RSSフィードを取得
    feed = feedparser.parse(RSS_URL)
    
    # 最新の投稿をチェック
    for entry in feed.entries[:5]:  # 最新5件をチェック
        title = entry.title
        link = entry.link
        
        # キーワードチェック
        if any(keyword in title for keyword in KEYWORDS):
            # Discord に通知
            send_discord_notification(title, link)
            print(f"通知送信: {title}")
        else:
            print(f"スキップ: {title}")

def send_discord_notification(title, link):
    data = {
        "content": f"🔔 **新しいセール情報** 🔔\n**{title}**\n{link}"
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code == 204:
        print("Discord通知成功")
    else:
        print(f"Discord通知失敗: {response.status_code}")

if __name__ == "__main__":
    check_feed()
