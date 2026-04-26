import streamlit as st
import os
import time
import json
import pandas as pd
from atproto import Client, models
from openai import OpenAI
from dotenv import load_dotenv, set_key

# --- Initialization ---
load_dotenv(override=True)

# OpenAI / Gemini API Settings
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash")

DB_FILE = "managed_data.json"
NOTIF_DB = "handled_notifications.json"

st.set_page_config(page_title="AI SNS Strategic Agent", layout="wide", page_icon="🔥")

# --- Language Settings ---
if "lang" not in st.session_state:
    st.session_state.lang = "ja"

def L(ja, en):
    return ja if st.session_state.lang == "ja" else en

def toggle_lang():
    st.session_state.lang = "en" if st.session_state.lang == "ja" else "ja"

# CSS
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stAlert { margin-top: 10px; margin-bottom: 10px; }
    .log-container {
        background-color: #0e1117;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #333;
        font-family: monospace;
        margin: 10px 0;
        line-height: 1.4;
        max-height: 500px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- Persistence ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {"removed": {}}
    return {"removed": {}}

def load_handled_notifs():
    if os.path.exists(NOTIF_DB):
        try:
            with open(NOTIF_DB, "r") as f: return set(json.load(f))
        except: return set()
    return set()

def save_handled_notifs(handled_set):
    with open(NOTIF_DB, "w") as f:
        json.dump(list(handled_set), f)

# --- Bluesky Helpers ---
def fetch_all_items(fetch_func, actor_did, item_type="follows", max_count=50000):
    results = []
    cursor = None
    progress_placeholder = st.empty()
    while len(results) < max_count:
        try:
            res = fetch_func(actor=actor_did, limit=100, cursor=cursor)
            batch = getattr(res, item_type, [])
            if not batch: break
            results.extend(batch)
            progress_placeholder.caption(f"[{item_type}] Fetching: {len(results)}...")
            cursor = res.cursor
            if not cursor: break
            time.sleep(0.5)
        except: break
    progress_placeholder.empty()
    return results

# --- Simple AI Client (OpenAI SDK based) ---
class AIClient:
    def __init__(self, api_key, model_name):
        self.model_name = model_name
        # Automatically detect provider by model name
        if "gemini" in model_name.lower():
            # Google's OpenAI-compatible endpoint
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        else:
            base_url = None # Default OpenAI
            
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate_content(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return type('Response', (object,), {'text': response.choices[0].message.content})
        except Exception as e:
            return type('Response', (object,), {'text': f"AI Error: {e}"})

# --- UI Header ---
st.title(L("🔥 AI SNS 戦略エージェント", "🔥 AI SNS Strategic Agent"))
st.caption(f"Strategy Automation | Model: {AI_MODEL_NAME}")

# --- Sidebar ---
with st.sidebar:
    st.button("🇯🇵 日本語 / 🇺🇸 English", on_click=toggle_lang)
    st.divider()
    st.header(L("🔌 接続設定", "🔌 Connection"))
    bs_handle = st.text_input(L("ハンドル名", "Handle"), value=os.getenv("BLUESKY_HANDLE", ""))
    bs_pwd = st.text_input(L("パスワード", "Password"), type="password", value=os.getenv("BLUESKY_PASSWORD", ""))
    
    st.divider()
    st.header("AI Settings")
    v_key = st.text_input(L("AI APIキー", "AI API Key"), type="password", value=AI_API_KEY)
    v_model = st.text_input(L("モデル名", "Model Name"), value=AI_MODEL_NAME, placeholder="gemini-1.5-flash or gpt-4o")

    if st.button(L("設定を保存", "Save Config")):
        set_key(".env", "BLUESKY_HANDLE", bs_handle)
        set_key(".env", "BLUESKY_PASSWORD", bs_pwd)
        set_key(".env", "AI_API_KEY", v_key)
        set_key(".env", "AI_MODEL_NAME", v_model)
        st.success(L("更新しました！", "Updated!"))

    st.divider()
    st.header(L("🎯 戦略設定", "🎯 Strategy"))
    kw_input = st.text_area(L("ターゲットキーワード (カンマ区切り)", "Target Keywords (Comma sep)"), value="エンジニア, AI, Python")
    target_kws = [k.strip() for k in kw_input.split(",") if k.strip()]

# AI/Client Init
client = None
ai = None
if v_key and bs_handle and bs_pwd:
    try:
        ai = AIClient(api_key=v_key, model_name=v_model)
        client = Client()
        client.login(bs_handle, bs_pwd)
    except Exception as e:
        st.sidebar.error(f"Login Error: {e}")

# --- Main Tabs ---
tab_growth, tab_manage, tab_engage, tab_research, tab_stats, tab_notify = st.tabs([
    L("🚀 成長", "🚀 Growth"), 
    L("👥 フォロワー", "👥 Followers"), 
    L("💬 交流", "💬 Engagement"), 
    L("📈 分析", "📈 Analysis"), 
    L("📊 統計", "📊 Stats"), 
    L("🔔 通知", "🔔 Notifications")
])

if not client:
    st.warning(L("サイドバーで接続設定を完了してください。", "Please complete connection settings in the sidebar."))
else:
    # --- TAB 1: Growth ---
    with tab_growth:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(L("🧹 片思い解除", "🧹 Unfollow"))
            if st.button(L("💔 実行開始", "💔 Start Unfollow"), key="unfol_btn"):
                log_p = st.empty()
                logs = []
                cursor = None
                my_did = client.me.did
                done_count = 0
                checked_count = 0
                try:
                    while True:
                        res = client.get_follows(actor=my_did, limit=1, cursor=cursor)
                        if not res.follows: break
                        user = res.follows[0]
                        checked_count += 1
                        try:
                            profile = client.get_profile(user.did)
                            if profile.viewer and profile.viewer.following and not profile.viewer.followed_by:
                                rkey = profile.viewer.following.split('/')[-1]
                                client.app.bsky.graph.follow.delete(my_did, rkey)
                                logs.append(f"[{checked_count}] ✅ {L('解除完了', 'Unfollowed')}: @{user.handle}")
                                done_count += 1
                            else:
                                logs.append(f"[{checked_count}] 🤝 {L('相互フォロー', 'Mutual')}: @{user.handle}")
                        except: pass
                        log_p.markdown(f'<div class="log-container">{"<br>".join(logs[-20:])}</div>', unsafe_allow_html=True)
                        time.sleep(1.0)
                        cursor = res.cursor
                        if not cursor: break
                except: pass
                st.success(L(f"完了。合計 {done_count} 人を解除しました。", f"Done. Total {done_count} users unfollowed."))

        with col2:
            st.subheader(L("➕ ターゲットフォロー", "➕ Target Follow"))
            f_limit = st.number_input(L("フォロー上限", "Follow limit"), 1, 5000, 100)
            t_likes = st.slider(L("フォロー後のいいね数", "Likes after follow"), 0, 5, 1)
            t_comments = st.slider(L("フォロー後のAIコメント数", "AI Comments after follow"), 0, 5, 0)
            if st.button(L("⚡ 実行", "⚡ Execute"), key="fol_btn"):
                total = 0
                log_p = st.empty()
                logs = []
                for kw in target_kws:
                    if total >= f_limit: break
                    try:
                        res = client.app.bsky.actor.search_actors({'term': kw, 'limit': 40})
                        for a in res.actors:
                            if total >= f_limit: break
                            try:
                                client.follow(a.did)
                                logs.append(f"✅ Followed: @{a.handle}")
                                if (t_likes > 0 or t_comments > 0):
                                    feed_res = client.app.bsky.feed.get_author_feed({'actor': a.did, 'limit': max(t_likes, t_comments)})
                                    for i, item in enumerate(feed_res.feed):
                                        if i < t_likes: client.like(item.post.uri, item.post.cid)
                                        if i < t_comments and ai:
                                            rep = ai.generate_content(f"Reply shortly: {item.post.record.text}").text
                                            client.send_post(text=rep, reply_to=models.AppBskyFeedPost.ReplyRef(
                                                parent=models.create_strong_ref(item.post), root=models.create_strong_ref(item.post)))
                                total += 1
                                log_p.markdown(f'<div class="log-container">{"<br>".join(logs[-15:])}</div>', unsafe_allow_html=True)
                                time.sleep(5.0)
                            except: continue
                    except: continue
                st.success(L("完了", "Completed"))

    # --- TAB 2: Follower Manager ---
    with tab_manage:
        st.subheader(L("👥 フォロワー分類・分析", "👥 Follower Analysis"))
        m_count = st.number_input(L("分析人数", "Scan limit"), 1, 10000, 500)
        if st.button(L("AI分析を開始", "Start AI Analysis")):
            with st.spinner(L("分析中...", "Analyzing...")):
                followers = fetch_all_items(client.get_followers, client.me.did, "followers", max_count=m_count)
                data = []
                for f in followers:
                    try:
                        p_prompt = f"User Bio: {f.description}. Reply 'Category: [Name]'"
                        cat = ai.generate_content(p_prompt).text.split(":")[-1].strip()
                        rkey = f.viewer.following.split('/')[-1] if hasattr(f, 'viewer') and f.viewer and f.viewer.following else None
                        data.append({"handle": f.handle, "did": f.did, "category": cat, "bio": f.description, "rkey": rkey})
                    except: continue
                st.session_state.categorized = data
        if "categorized" in st.session_state:
            for item in st.session_state.categorized:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**@{item['handle']}** | `{item['category']}`")
                    c1.caption(item['bio'][:150] if item['bio'] else "No bio")
                    if c2.button(L("🚫 解除", "🚫 Unfollow"), key=f"un_{item['did']}"):
                        if item['rkey']:
                            client.app.bsky.graph.follow.delete(client.me.did, item['rkey'])
                            st.toast(f"Removed @{item['handle']}")

    # --- TAB 3: Community Engage ---
    with tab_engage:
        st.subheader(L("💬 フォロワーと交流", "💬 Community Engagement"))
        e_num = st.number_input(L("対象人数", "Target count"), 1, 10000, 100, key="e_num")
        num_l = st.slider(L("1人あたりのいいね数", "Likes per user"), 0, 10, 1)
        num_c = st.slider(L("1人あたりのコメント数", "Comments per user"), 0, 10, 1)
        if st.button(L("交流を開始", "Start Engagement"), key="eng_btn"):
            fols = fetch_all_items(client.get_followers, client.me.did, "followers", max_count=e_num)
            for f in fols:
                try:
                    feed = client.app.bsky.feed.get_author_feed({'actor': f.did, 'limit': max(num_l, num_c)}).feed
                    for i, item in enumerate(feed):
                        if i < num_l: client.like(item.post.uri, item.post.cid)
                        if i < num_c and ai:
                            rep = ai.generate_content(f"Reply shortly: {item.post.record.text}").text
                            client.send_post(text=rep, reply_to=models.AppBskyFeedPost.ReplyRef(parent=models.create_strong_ref(item.post), root=models.create_strong_ref(item.post)))
                    st.write(f"💬 Interaction with @{f.handle}")
                    time.sleep(3.0)
                except: continue
            st.success(L("完了", "Completed"))

    # --- TAB 4: Analysis ---
    with tab_research:
        st.subheader(L("📈 バズり分析", "📈 Viral Analysis"))
        r_kw = st.text_input(L("分析ワード", "Search word"), "Python")
        if st.button(L("調査開始", "Start Analysis"), key="res_btn"):
            try:
                search = client.app.bsky.feed.search_posts({'q': r_kw, 'limit': 100})
                for p in search.posts:
                    if (p.like_count or 0) > 10:
                        with st.expander(f"🔥 @{p.author.handle} ({p.like_count} Likes)"):
                            st.write(p.record.text)
                            if ai:
                                analysis = ai.generate_content(f"Analyze success: {p.record.text}")
                                st.info(analysis.text)
            except Exception as e: st.error(e)

    # --- TAB 5: Stats ---
    with tab_stats:
        st.subheader(L("📊 統計", "📊 Stats"))
        if st.button(L("適合率を計算", "Calculate Stats")):
            fols = fetch_all_items(client.get_followers, client.me.did, "followers", max_count=100)
            hit = 0
            for f in fols:
                try:
                    if ai and "YES" in ai.generate_content(f"Match keywords? {f.description}").text.upper(): hit += 1
                except: continue
            if fols: st.metric(L("ターゲット適合率", "Target Fit Rate"), f"{(hit/len(fols))*100:.1f}%")

    # --- TAB 6: Notifications ---
    with tab_notify:
        st.subheader(L("🔔 AI通知自動マネージャー", "🔔 AI Notification Manager"))
        handled_notifs = load_handled_notifs()
        
        with st.expander(L("👤 フォローへの対応", "👤 Follow Settings")):
            do_follow_back = st.checkbox(L("自動フォローバックを有効にする", "Enable Auto Follow-back"))
            follow_policy = st.text_area(L("フォロー条件", "Follow conditions"), value=L(f"プロフィールの内容を見て、{target_kws}に関連する人であればフォローしてください。", f"Follow back if the profile matches {target_kws}."))
        with st.expander(L("💬 反答対応", "💬 Reply/Mention Settings")):
            do_reply = st.checkbox(L("自動返信を有効にする", "Enable Auto Reply"))
            reply_policy = st.text_area(L("返信トーン", "Reply tone"), value=L("親しみやすく、短く丁寧に返信してください。", "Reply kindly and briefly."))
        with st.expander(L("👍 反応対応", "👍 Interaction Settings")):
            do_like_back = st.checkbox(L("いいね返しを有効にする", "Enable Auto Like-back"))
        
        n_limit = st.number_input(L("通知チェック数", "Notifications count"), 1, 100, 20)
        if st.button(L("⚡ AI自動対応を実行", "⚡ Run AI Manager"), key="notif_btn"):
            log_p = st.empty()
            logs = []
            try:
                notifs = client.app.bsky.notification.list_notifications({'limit': n_limit}).notifications
                new_handled = 0
                for n in notifs:
                    if n.uri in handled_notifs or n.is_read:
                        handled_notifs.add(n.uri)
                        continue
                    
                    # AI Processing logic
                    if n.reason == 'follow' and do_follow_back:
                        p_data = client.get_profile(n.author.did)
                        if "YES" in ai.generate_content(f"Does this profile match the interest? {p_data.description}").text.upper():
                            client.follow(n.author.did)
                            logs.append(f"👤 Followed back @{n.author.handle}")
                    elif n.reason in ['reply', 'mention', 'quote'] and do_reply:
                        prompt = f"Policy: {reply_policy}\nPost: {n.record.text}\nFrom: @{n.author.handle}\nReply shortly:"
                        rep = ai.generate_content(prompt).text
                        # Get strong ref for reply
                        ref = models.create_strong_ref(n)
                        client.send_post(text=rep, reply_to=models.AppBskyFeedPost.ReplyRef(parent=ref, root=ref))
                        logs.append(f"💬 Replied to @{n.author.handle}")
                    elif n.reason in ['like', 'repost'] and do_like_back:
                        feed = client.app.bsky.feed.get_author_feed({'actor': n.author.did, 'limit': 1}).feed
                        if feed:
                            client.like(feed[0].post.uri, feed[0].post.cid)
                            logs.append(f"👍 Like-back to @{n.author.handle}")
                    
                    handled_notifs.add(n.uri)
                    new_handled += 1
                    log_p.markdown(f'<div class="log-container">{"<br>".join(logs[-15:])}</div>', unsafe_allow_html=True)
                    time.sleep(2.0)
                
                save_handled_notifs(handled_notifs)
                client.app.bsky.notification.update_seen({'seen_at': client.get_current_time_iso()})
                st.success(L(f"新たに {new_handled} 件処理しました。", f"Processed {new_handled} new notifications."))
            except Exception as e: st.error(f"Error: {e}")
