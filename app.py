import streamlit as st
import os
import time
from atproto import Client, models
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv, set_key

# 環境変数の読み込み
load_dotenv()

st.set_page_config(page_title="Bluesky AI Bot", layout="wide")

st.title("🦋 Bluesky AI 自動いいね＆コメントBot")
st.markdown("プレビュー画面から設定を行って、Botを実際に動かすことができます。")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ アカウント＆API設定")
    handle = st.text_input("Bluesky ハンドル名 (例: yourname.bsky.social)", value=os.getenv("BLUESKY_HANDLE", ""))
    password = st.text_input("Bluesky パスワード (アプリパスワード推奨)", type="password", value=os.getenv("BLUESKY_PASSWORD", ""))
    api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    
    st.markdown("---")
    st.header("🎯 ターゲット＆アクション設定")
    target_prof = st.text_input("ターゲット（職業・属性など）", value=os.getenv("TARGET_PROFESSION", "エンジニア"))
    like_posts = st.checkbox("最新の投稿に「いいね」する", value=os.getenv("LIKE_POSTS", "True").lower() == "true")
    comment_posts = st.checkbox("AIで自然なコメントを生成して投稿する", value=os.getenv("COMMENT_POSTS", "True").lower() == "true")
    
    save_btn = st.button("設定を保存", use_container_width=True)
    if save_btn:
        if not os.path.exists(".env"):
            open(".env", "w").close()
        set_key(".env", "BLUESKY_HANDLE", handle)
        set_key(".env", "BLUESKY_PASSWORD", password)
        set_key(".env", "GEMINI_API_KEY", api_key)
        set_key(".env", "TARGET_PROFESSION", target_prof)
        set_key(".env", "LIKE_POSTS", str(like_posts))
        set_key(".env", "COMMENT_POSTS", str(comment_posts))
        st.success("設定を `.env` ファイルに保存しました！")

# --- AI ロジック ---
def is_target_profession(model, bio: str, target: str) -> bool:
    if not bio: return False
    prompt = f"以下のプロフィール文から、この人が「{target}」という職業・属性に該当するか判定してください。該当する場合は「Yes」、そうでない場合は「No」とだけ答えてください。\n\nプロフィール: {bio}"
    try:
        response = model.generate_content(prompt, generation_config=GenerationConfig(temperature=0.0, max_output_tokens=10))
        return "yes" in response.text.strip().lower()
    except Exception as e:
        return False

def generate_reply(model, post_text: str) -> str:
    prompt = f"以下のSNSの投稿に対して、親しみやすく、自然で短い共感のコメント（リプライ）を生成してください。\n\n投稿: {post_text}"
    try:
        response = model.generate_content(prompt, generation_config=GenerationConfig(temperature=0.7, max_output_tokens=50))
        return response.text.strip()
    except Exception as e:
        return "素敵ですね！" 

# --- 実行セクション ---
st.markdown("---")
run_btn = st.button("🚀 Botを実行する", type="primary", use_container_width=True)

if run_btn:
    if not handle or not password or not api_key:
        st.error("⚠️ 左のサイドバーから Bluesky のログイン情報と Gemini API Key を設定してください。")
    else:
        st.subheader("📝 実行ログ")
        # ログ表示用のプレースホルダー
        log_placeholder = st.empty()
        logs = []
        
        def log(msg):
            logs.append(msg)
            # Markdownとして改行をつけて表示
            log_placeholder.markdown("  \n".join([f"`{m}`" for m in logs]))

        log("🚀 Botの実行を開始します...")
        try:
            # Geminiの初期化
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel("gemini-1.5-flash")
            
            client = Client()
            log(f"🔑 [{handle}] にログイン中...")
            client.login(handle, password)
            log("✅ ログイン完了。")
            
            log("👥 フォロワーを取得中...")
            # ※デモ用のため最初のページのみ取得
            followers = client.get_followers(client.me.did)
            
            for follower in followers.followers:
                f_handle = follower.handle
                bio = follower.description
                
                # AIで判定
                if is_target_profession(ai_model, bio, target_prof):
                    log(f"🎯 ターゲット発見: @{f_handle} (職業: {target_prof})")
                    try:
                        feed = client.app.bsky.feed.get_author_feed({'actor': f_handle, 'limit': 1})
                        if not feed.feed:
                            log(f"  ⚠️ @{f_handle} の投稿が見つかりませんでした。")
                            continue
                        
                        post_item = feed.feed[0].post
                        post_text = post_item.record.text
                        log(f"  📝 投稿内容: {post_text}")
                        
                        # いいね
                        if like_posts:
                            client.like(post_item.uri, post_item.cid)
                            log("  👍 いいねを実行しました。")
                            
                        # コメント
                        if comment_posts:
                            reply_text = generate_reply(ai_model, post_text)
                            log(f"  💬 コメントを生成しました: {reply_text}")
                            
                            root_ref = models.create_strong_ref(post_item)
                            parent_ref = models.create_strong_ref(post_item)
                            reply_ref = models.AppBskyFeedPost.ReplyRef(parent=parent_ref, root=root_ref)
                            client.send_post(text=reply_text, reply_to=reply_ref)
                            log("  📩 コメントを投稿しました。")
                        
                        log("-" * 40)
                        # API制限を避けるために待機
                        time.sleep(2)
                    except Exception as e:
                        log(f"  ❌ 処理中にエラー発生: {e}")
                else:
                    log(f"⏭️ スキップ: @{f_handle} (ターゲットに合致しません)")
            
            log("🎉 すべての処理が完了しました！")
            st.success("処理が正常に完了しました！")
            
        except Exception as e:
            st.error(f"処理全体でエラーが発生しました: {e}")
