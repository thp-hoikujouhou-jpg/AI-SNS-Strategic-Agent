import os
import time
from dotenv import load_dotenv
from atproto import Client, models
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# 環境変数の読み込み
load_dotenv()

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
TARGET_PROFESSION = os.getenv("TARGET_PROFESSION", "エンジニア")
LIKE_POSTS = os.getenv("LIKE_POSTS", "True").lower() == "true"
COMMENT_POSTS = os.getenv("COMMENT_POSTS", "True").lower() == "true"

def is_target_profession(model, bio: str, target: str) -> bool:
    if not bio:
        return False
    
    prompt = f"以下のプロフィール文から、この人が「{target}」という職業・属性に該当するか判定してください。該当する場合は「Yes」、そうでない場合は「No」とだけ答えてください。\n\nプロフィール: {bio}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(temperature=0.0, max_output_tokens=10)
        )
        answer = response.text.strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"  [AIエラー(判定)]: {e}")
        return False

def generate_reply(model, post_text: str) -> str:
    prompt = f"以下のSNSの投稿に対して、親しみやすく、自然で短い共感のコメント（リプライ）を生成してください。\n\n投稿: {post_text}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(temperature=0.7, max_output_tokens=50)
        )
        return response.text.strip()
    except Exception as e:
        print(f"  [AIエラー(コメント生成)]: {e}")
        return "素敵ですね！" # エラー時のフォールバック

def main():
    if not BLUESKY_HANDLE or not BLUESKY_PASSWORD or not GEMINI_API_KEY:
        print("エラー: .env ファイルを作成し、必要な環境変数を設定してください。")
        return

    # Geminiの初期化
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel(GEMINI_MODEL)

    client = Client()

    print(f"[{BLUESKY_HANDLE}] にログイン中...")
    try:
        client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)
    except Exception as e:
        print(f"ログインエラー: {e}")
        return
    print("ログイン完了。\n")

    print(f"モデル [{GEMINI_MODEL}] を使用してフォロワーを取得中...")
    try:
        # ※デモ用のため、最初の1ページ分のみ取得しています。
        followers = client.get_followers(client.me.did)
    except Exception as e:
        print(f"フォロワー取得エラー: {e}")
        return
    
    for follower in followers.followers:
        handle = follower.handle
        bio = follower.description

        # AIでプロフィール文から職業を判定
        if is_target_profession(ai_model, bio, TARGET_PROFESSION):
            print(f"🎯 ターゲット発見: @{handle} (職業: {TARGET_PROFESSION})")
            
            try:
                # 対象者の最新の投稿を1件取得
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

            # いいねを実行
            if LIKE_POSTS:
                print("  👍 いいねをします...")
                try:
                    client.like(post_item.uri, post_item.cid)
                except Exception as e:
                    print(f"  いいね失敗: {e}")
                
            # コメント（リプライ）を生成して投稿
            if COMMENT_POSTS:
                reply_text = generate_reply(ai_model, post_text)
                print(f"  💬 コメントします: {reply_text}")
                
                try:
                    # リプライ先の参照を作成
                    root_ref = models.create_strong_ref(post_item)
                    parent_ref = models.create_strong_ref(post_item)
                    reply_ref = models.AppBskyFeedPost.ReplyRef(parent=parent_ref, root=root_ref)
                    
                    client.send_post(text=reply_text, reply_to=reply_ref)
                except Exception as e:
                    print(f"  コメント送信エラー: {e}")
            
            print("-" * 30)
            # API制限を避けるために少し待機
            time.sleep(2)
        else:
            print(f"スキップ: @{handle}")

if __name__ == "__main__":
    main()
