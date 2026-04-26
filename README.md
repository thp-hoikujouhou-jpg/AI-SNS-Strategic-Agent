# 🔥 AI SNS Strategic Agent

AIを活用した次世代のBluesky運用自動化・戦略ツールです。Gemini AIとBluesky APIを統合し、効率的なフォロワー獲得とコミュニティ構築を支援します。

An AI-driven strategic automation tool for Bluesky. Integrating Gemini AI and Bluesky API to help you grow your audience and manage your community efficiently.

---

## 🚀 主な機能 / Key Features

### 🧹 片思い解除 (Unfollow)
- **1人ずつ確実に判定**: 自分がフォローしていて、フォローバックされていないユーザーを確実に特定。
- **低速・確実実行**: API制限を考慮し、一人ずつ丁寧に解除を実行します。

### ➕ ターゲットフォロー (Target Follow)
- **キーワード検索**: 指定したキーワードに基づき、ターゲットとなるユーザーを検索。
- **自動いいね＆コメント**: フォローした直後に、相手の最新投稿に対して指定した数だけ自動でいいねやAIによる自然なコメントを行います。

### 👥 フォロワー分類・分析 (Follower Analysis)
- **AIプロフィール診断**: フォロワーのプロフィールをAIが読み取り、カテゴリー（エンジニア、AI愛好家など）に自動分類します。

### 🔔 通知自動マネージャー (AI Notification Manager)
- **賢い返信**: リプライやメンションに対し、あらかじめ設定した方針に基づいてAIが自動で適切な返答を生成。
- **自動フォローバック**: あなたのターゲット戦略に合うユーザーからのフォローを検出し、自動でフォローを返します。
- **既読・重複防止**: 一度対応した通知は記録され、二重に対応することはありません。

### 🌍 多言語対応 (Multilingual Support)
- ボタン一つで日本語と英語のUIを切り替え可能です。

---

## 🛠 セットアップ / Setup

### 必要条件 / Requirements
- Python 3.10+
- Bluesky アカウント
- Google Gemini API Key

### インストール / Installation

1. リポジトリをクローンします:
   ```bash
   git clone https://github.com/thp-hoikujouhou-jpg/AI-SNS-Strategic-Agent.git
   cd AI-SNS-Strategic-Agent
   ```

2. 必要なパッケージをインストールします:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` ファイルを作成し、設定を記入します:
   ```env
   BLUESKY_HANDLE=your-handle.bsky.social
   BLUESKY_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_API_MODEL=gemini-1.5-flash
   ```

---

## 🚀 実行方法 / Usage

Streamlitサーバーを起動します:
```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開き、サイドバーで設定を確認してから各種機能を実行してください。

---

## 📜 ライセンス / License
MIT License - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

---

## ⚠️ 免責事項 / Disclaimer
このツールは自動化を目的としていますが、過度な利用はSNSプラットフォームの利用規約に抵触する可能性があります。ご利用は自己責任でお願いいたします。
While this tool is designed for automation, excessive use may violate SNS platform terms of service. Use it at your own risk.
