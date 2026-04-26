# 🔥 AI SNS Strategic Agent

The next-generation Bluesky automation and strategy tool powered by AI. Seamlessly integrating Gemini AI with the Bluesky API to help you grow your audience and build your community with intelligent, human-like interactions.

---

## 🚀 Key Features

### 🧹 Smart Unfollow (One-by-One)
- **Precise Verification**: Checks your following list one by one to ensure accurate identification of those not following you back.
- **Reliable Execution**: Safely performs unfollowing with built-in rate-limit handling and real-time logging.

### ➕ Strategic Target Follow
- **Keyword-Based Search**: Finds potential followers based on your specific target keywords.
- **Engagement After Follow**: Automatically likes and posts AI-generated comments on the user's latest posts immediately after following them to maximize follow-back rates.

### 👥 Follower Analysis
- **AI Profile Diagnosis**: Reads follower bios and automatically categorizes them (e.g., Engineer, AI Enthusiast) to help you understand your audience.

### 🔔 AI Notification Manager
- **Smart Auto-Reply**: Automatically generates and posts natural replies to mentions, quotes, and replies based on your custom persona and policy.
- **Intelligent Follow-back**: Analyzes new followers' profiles and follows them back only if they match your defined strategy.
- **History Tracking**: Keeps a record of handled notifications to ensure no duplicate actions are taken.

### 🌍 Multilingual Interface
- Switch between Japanese and English UI instantly with a single click.

---

## 🛠 Setup

### Requirements
- Python 3.10+
- Bluesky Account
- Google Gemini API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thp-hoikujouhou-jpg/AI-SNS-Strategic-Agent.git
   cd AI-SNS-Strategic-Agent
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```env
   BLUESKY_HANDLE=your-handle.bsky.social
   BLUESKY_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_API_MODEL=gemini-1.5-flash
   ```

---

## 🚀 Usage

Start the Streamlit dashboard:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser, configure your strategy in the sidebar, and start managing your SNS growth.

---

## 📜 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

## ⚠️ Disclaimer
This tool is for educational and productivity purposes. Overuse of automation features may violate social media platforms' terms of service. Use it responsibly and at your own risk.
