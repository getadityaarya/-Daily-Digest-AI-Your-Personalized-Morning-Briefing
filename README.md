🌅 Daily-Digest-AI - Your Personalized Morning Briefing
An AI-powered application that delivers your personalized daily updates including live news, weather, upcoming calendar events, and a motivational quote in one clean, instant summary. Built with Streamlit and Python, it integrates multiple APIs to fetch real-time information and can even send the digest via email.

🔍 Features
📰 Live News Updates - Latest headlines from trusted sources

🌤 Real-time Weather - Accurate forecasts for your city

📅 Google Calendar Integration - Never miss important events

💡 Motivational Quote - Start the day with positivity

🤖 AI Summary Generation - Concise, friendly daily briefing

📧 Email Delivery - Optional automatic delivery via Gmail API

📦 Tech Stack
Python & Streamlit - Web app & UI

OpenAI API / Together AI / Groq - Natural language summarization

NewsAPI - Live headlines

OpenWeather API - Weather data

Google Calendar API - Event integration

Gmail API - Email sending

python-dotenv - Secure API key management

📁 Project Structure
bash
Copy
Edit
Daily-Digest-AI/
│
├── app.py            # Streamlit app for interactive use
├── send_digest.py    # Core logic: data fetching, summarization, email sending
├── requirements.txt  # Dependencies
├── .env              # API keys & config (not in repo)
└── README.md         # Project documentation
🚀 How to Run
Clone the repository

bash
Copy
Edit
git clone https://github.com/your-username/Daily-Digest-AI.git
cd Daily-Digest-AI
Create virtual environment & install dependencies

bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
Set up .env file with your API keys:

ini
Copy
Edit
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key
RECIPIENT_EMAIL=your_email@example.com
Run the Streamlit app

bash
Copy
Edit
streamlit run app.py
(Optional) Send daily email

bash
Copy
Edit
python send_digest.py
🧪 Example
Enter your name and city → The app fetches all updates → AI generates your morning briefing in seconds → View on-screen or receive via email.

🛡 Disclaimer
For personal use and educational purposes only. Respect API usage limits and terms.

📬 **Contact:** [getadityaarya@gmail.com](mailto:getadityaarya@gmail.com)
