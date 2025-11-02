import feedparser
import requests
import os
import json
from datetime import datetime

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
    return {'notified_entries': []}

def save_state(state):
    """チェック状態を保存"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_entry_id(entry):
    """記事の一意なIDを生成（タイトル + 更新日時）"""
    title = entry.title
    # 更新日時を取得（published or updated）
    pub_date = entry.get('published', entry.get('updated', ''))
    return f"{title}|{pub_date}"

def check_feed():
    # 前回の状態を読み込む
    state = load_state()
    notified_entries = set(state.get('notified_entries', []))
    new_notified_entries = []
    
    # RSSフィードを取得
    feed = feedparser.parse(RSS_URL)
    
    print(f"フィード取得: {len(feed.entries)}件の記事")
    
    # 最新の投稿をチェック
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        entry_id = get_entry_id(entry)
        
        # 既に通知済みならスキップ
        if entry_id in notified_entries:
            print(f"通知済みスキップ: {title}")
            continue
        
        # キーワードチェック
        if any(keyword in title for keyword in KEYWORDS):
            # Discord に通知
            send_discord_notification(title, link, entry)
            print(f"✅ 通知送信: {title}")
            new_notified_entries.append(entry_id)
        else:
            print(f"キーワード不一致: {title}")
    
    # 状態を更新（新しく通知したエントリーを追加、最大100件まで保持）
    all_notified = list(notified_entries) + new_notified_entries
    state['notified_entries'] = all_notified[-100:]  # 最新100件のみ保持
    state['last_check_time'] = datetime.now().isoformat()
    save_state(state)
    
    print(f"\n通知数: {len(new_notified_entries)}件")

def send_discord_notification(title, link, entry):
    # 更新日時を取得
    pub_date = entry.get('published', entry.get('updated', '不明'))
    
    data = {
        "content": f"🔔 **新しいセール情報** 🔔\n**{title}**\n{link}\n📅 {pub_date}"
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
