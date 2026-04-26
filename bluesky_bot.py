import os
import time
from dotenv import load_dotenv
from atproto import Client, models
from openai import OpenAI

# 環境変数の読み込み
load_dotenv()

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Vercel AI Gateway Settings
GATEWAY_API_KEY = os.getenv("VERCEL_GATEWAY_API_KEY")
GATEWAY_URL = os.getenv("VERCEL_GATEWAY_URL")
AI_MODEL_NAME = os.getenv("VERCEL_GATEWAY_MODEL", "google/gemini-1.5-flash")

TARGET_PROFESSION = os.getenv("TARGET_PROFESSION", "エンジニア")
LIKE_POSTS = os.getenv("LIKE_POSTS", "True").lower() == "true"
COMMENT_POSTS = os.getenv("COMMENT_POSTS", "True").lower() == "true"

class AIClient:
    def __init__(self, api_key, base_url):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate_content(self, prompt, temperature=0.7, max_tokens=100):
        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return type('Response', (object,), {'text': response.choices[0].message.content})
        except Exception as e:
            print(f"  [AIエラー]: {e}")
            return type('Response', (object,), {'text': ""})

def is_target_profession(ai, bio: str, target: str) -> bool:
    if not bio:
        return False
    
    prompt = f"以下のプロフィール文から、この人が「{target}」という職業・属性に該当するか判定してください。該当する場合は「Yes」、そうでない場合は「No」とだけ答えてください。\n\nプロフィール: {bio}"
    
    res = ai.generate_content(prompt, temperature=0.0, max_tokens=10)
    answer = res.text.strip().lower()
    return "yes" in answer

def generate_reply(ai, post_text: str) -> str:
    prompt = f"以下のSNSの投稿に対して、親しみやすく、自然で短い共感のコメント（リプライ）を生成してください。\n\n投稿: {post_text}"
    
    res = ai.generate_content(prompt, temperature=0.7, max_tokens=50)
    return res.text.strip() or "素敵ですね！"

def main():
    if not BLUESKY_HANDLE or not BLUESKY_PASSWORD or not GATEWAY_API_KEY or not GATEWAY_URL:
        print("エラー: .env ファイルを作成し、必要な環境変数を設定してください（Vercel Gatewayの設定が必要です）。")
        return

    # AI Client (Vercel Gateway) の初期化
    ai = AIClient(api_key=GATEWAY_API_KEY, base_url=GATEWAY_URL)

    client = Client()

    print(f"[{BLUESKY_HANDLE}] にログイン中...")
    try:
        client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)
    except Exception as e:
        print(f"ログインエラー: {e}")
        return
    print("ログイン完了。\n")

    print(f"モデル [{AI_MODEL_NAME}] を使用してフォロワーを取得中...")
    try:
        followers = client.get_followers(client.me.did)
    except Exception as e:
        print(f"フォロワー取得エラー: {e}")
        return
    
    for follower in followers.followers:
        handle = follower.handle
        bio = follower.description

        # AIでプロフィール文から職業を判定
        if is_target_profession(ai, bio, TARGET_PROFESSION):
            print(f"🎯 ターゲット発見: @{handle} (職業: {TARGET_PROFESSION})")
            
            try:
                feed = client.app.bsky.feed.get_author_feed({'actor': handle, 'limit': 1})
            except Exception as e:
                print(f"  投稿の取得に失敗しました: {e}")
                continue
            
            if not feed.feed:
                print(f"  @{handle} の投稿が見つかりませんでした。\n")
                continue
                
            post_item = feed.feed[0].post
            post_text = post_item.record.text
            print(f"  📝 投稿内容: {post_text}")

            if LIKE_POSTS:
                print("  👍 いいねをします...")
                try:
                    client.like(post_item.uri, post_item.cid)
                except Exception as e:
                    print(f"  いいね失敗: {e}")
                
            if COMMENT_POSTS:
                reply_text = generate_reply(ai, post_text)
                print(f"  💬 コメントします: {reply_text}")
                
                try:
                    root_ref = models.create_strong_ref(post_item)
                    parent_ref = models.create_strong_ref(post_item)
                    reply_ref = models.AppBskyFeedPost.ReplyRef(parent=parent_ref, root=root_ref)
                    client.send_post(text=reply_text, reply_to=reply_ref)
                except Exception as e:
                    print(f"  コメント送信エラー: {e}")
            
            print("-" * 30)
            time.sleep(2)
        else:
            print(f"スキップ: @{handle}")

if __name__ == "__main__":
    main()
