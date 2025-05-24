#!/usr/bin/env python3
"""
ChatGPT AIニュース自動取得スクリプト
"""
import os
import json
import requests
from datetime import datetime
from markdownify import markdownify as md
import html

# 設定
CHATGPT_TOKEN = os.environ.get('CHATGPT_TOKEN')
CONVERSATION_ID = '681f62a1-ab00-8004-9ddc-0597eaf07ee5'
API_URL = f'https://chatgpt.com/backend-api/conversation/{CONVERSATION_ID}'

def fetch_latest_ai_news():
    """ChatGPTから最新のAIニュースを取得"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Cookie': f'__Secure-next-auth.session-token={CHATGPT_TOKEN}',
        'Referer': 'https://chatgpt.com/',
    }
    
    try:
        print("🔍 ChatGPTからAIニュースを取得中...")
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        messages = data.get('mapping', {}).values()
        
        # Assistant（ChatGPT）のメッセージのみ抽出
        assistant_messages = []
        for msg in messages:
            if (msg.get('message') and 
                msg['message'].get('author', {}).get('role') == 'assistant' and
                msg['message'].get('content', {}).get('parts')):
                assistant_messages.append(msg)
        
        if not assistant_messages:
            print("❌ AIニュースが見つかりませんでした")
            return None
            
        # 最新のメッセージを取得
        latest = max(assistant_messages, key=lambda x: x['message']['create_time'])
        content = latest['message']['content']['parts'][0]
        
        # HTMLをMarkdownに変換
        clean_content = html.unescape(content)
        markdown_content = md(clean_content, heading_style="ATX").strip()
        
        print("✅ AIニュース取得完了")
        return markdown_content
        
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

def update_readme(content):
    """README.mdを更新"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    readme_content = f"""# 🤖 AI ニュースダイジェスト

## 📅 最新更新: {today}

{content}

---

### 📖 このページについて
- 毎日朝8時に自動更新
- ChatGPTが厳選したAI業界の最新ニュース10件
- [元の会話を見る](https://chatgpt.com/c/681f62a1-ab00-8004-9ddc-0597eaf07ee5)

### 🔄 更新履歴
このページは GitHub Actions により自動更新されています。

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} JST*
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md更新完了")

def main():
    print("🚀 AI ニュース自動更新を開始...")
    
    if not CHATGPT_TOKEN:
        print("❌ CHATGPT_TOKENが設定されていません")
        return
    
    # AIニュースを取得
    news_content = fetch_latest_ai_news()
    if not news_content:
        print("❌ ニュースの取得に失敗しました")
        return
    
    # README.mdを更新
    update_readme(news_content)
    
    print("🎉 更新完了！")

if __name__ == '__main__':
    main()
