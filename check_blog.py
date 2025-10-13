import feedparser
import requests
import os
import json
from datetime import datetime
from dateutil import parser as date_parser

# 設定
RSS_URL = "https://shobundo.biz/blog/feed"
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['セール', 'SALE', 'sale', 'Sale']
STATE_FILE = 'last_check_state.json'

def load_state():
    """前回のチェック状態を読み込む"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'last_check_time': None, 'notified_urls': []}

def save_state(state):
    """チェック状態を保存"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_feed():
    # 前回の状態を読み込む
    state = load_state()
    notified_urls = set(state.get('notified_urls', []))
    new_notified_urls = []
    
    # RSSフィードを取得
    feed = feedparser.parse(RSS_URL)
    
    print(f"フィード取得: {len(feed.entries)}件の記事")
    
    # 最新の投稿をチェック
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        
        # 既に通知済みならスキップ
        if link in notified_urls:
            print(f"通知済みスキップ: {title}")
            continue
        
        # キーワードチェック
        if any(keyword in title for keyword in KEYWORDS):
            # Discord に通知
            send_discord_notification(title, link)
            print(f"✅ 通知送信: {title}")
            new_notified_urls.append(link)
        else:
            print(f"キーワード不一致: {title}")
    
    # 状態を更新（新しく通知したURLを追加、最大100件まで保持）
    all_notified = list(notified_urls) + new_notified_urls
    state['notified_urls'] = all_notified[-100:]  # 最新100件のみ保持
    state['last_check_time'] = datetime.now().isoformat()
    save_state(state)
    
    print(f"\n通知数: {len(new_notified_urls)}件")

def send_discord_notification(title, link):
    data = {
        "content": f"🔔 **新しいセール情報** 🔔\n**{title}**\n{link}"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        
        if response.status_code == 204:
            print("  → Discord通知成功")
        else:
            print(f"  → Discord通知失敗: {response.status_code}")
    except Exception as e:
        print(f"  → Discord通知エラー: {e}")

if __name__ == "__main__":
    check_feed()
