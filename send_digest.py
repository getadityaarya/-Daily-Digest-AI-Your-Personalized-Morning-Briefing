import os
import requests
import base64
import datetime
import pickle
import logging
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --------------------
# Load env + logging
# --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("daily_digest")

# --------------------
# Config
# --------------------
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.pkl")
DEFAULT_CITY = os.getenv("WEATHER_LOCATION", "Pune")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

# --------------------
# Google Auth
# --------------------
def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Missing Google credentials: {CREDENTIALS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds

# --------------------
# Fetch News
# --------------------
def get_news(country="in", max_headlines=3):
    if not NEWS_API_KEY:
        return ["News API key not configured."]
    try:
        url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])[:max_headlines]
        return [f"• {a['title']}" for a in articles if a.get("title")]
    except Exception as e:
        logger.exception("News fetch failed")
        return [f"News unavailable: {e}"]

# --------------------
# Fetch Weather
# --------------------
def get_weather(city=DEFAULT_CITY):
    if not WEATHER_API_KEY:
        return "Weather API key not configured."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if str(data.get("cod")) != "200":
            return "Weather data unavailable."
        desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        return f"{desc}, {temp}°C"
    except Exception as e:
        logger.exception("Weather fetch failed")
        return f"Weather unavailable: {e}"

# --------------------
# Fetch Calendar
# --------------------
def get_calendar_events(max_results=5):
    try:
        creds = authenticate_google()
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return ["No events today."]
        out = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            out.append(f"{start} — {e.get('summary', 'No title')}")
        return out
    except Exception as e:
        logger.exception("Calendar fetch failed")
        return [f"Calendar unavailable: {e}"]

# --------------------
# Quote
# --------------------
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=8)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            return f"“{data[0]['q']}” — {data[0]['a']}"
        return "Stay positive and keep moving forward!"
    except Exception:
        return "Stay positive and keep moving forward!"

# --------------------
# AI Summary (multi-provider)
# --------------------
def generate_summary(news, weather, calendar, quote, name="Friend"):
    news_text = "\n".join(news) if isinstance(news, (list, tuple)) else str(news)
    cal_text = "\n".join(calendar) if isinstance(calendar, (list, tuple)) else str(calendar)

    prompt = (
        f"Create a short, friendly daily digest for {name}.\n\n"
        f"News Headlines:\n{news_text}\n\n"
        f"Weather:\n{weather}\n\n"
        f"Calendar Events:\n{cal_text}\n\n"
        f"Motivational Quote:\n{quote}\n\n"
        "Keep it concise, warm, and easy to read (3-6 short sentences)."
    )

    # Try Together AI
    if TOGETHER_API_KEY:
        try:
            resp = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
                json={
                    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 250
                },
                timeout=15
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Together AI failed: {e}")

    # Try Groq
    if GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 250
                },
                timeout=15
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Groq AI failed: {e}")

    # Try OpenAI
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI failed: {e}")

    # Fallback plain text
    return (
        f"Hello {name}, here's your quick digest:\n\n"
        f"News:\n{news_text}\n\n"
        f"Weather:\n{weather}\n\n"
        f"Events:\n{cal_text}\n\n"
        f"Quote:\n{quote}"
    )

# --------------------
# Email helpers
# --------------------
def create_message(sender, to, subject, body_text):
    body_html = body_text.replace("\n", "<br>")
    html_template = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f8f9fa; padding: 20px;">
        <div style="max-width: 600px; margin: auto;">
          <div style="background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <h2 style="color: #4CAF50; text-align:center;">🌅 Your Daily Digest</h2>
            <div style="margin-top: 12px;">{body_html}</div>
            <hr style="margin-top: 20px;">
            <p style="font-size: 12px; color: #777; text-align:center;">
                Sent automatically by Daily Digest AI — Have a great day!
            </p>
          </div>
        </div>
      </body>
    </html>
    """
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(html_template, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}

def send_email(service, sender, to, subject, body_text):
    message = create_message(sender, to, subject, body_text)
    return service.users().messages().send(userId="me", body=message).execute()

# --------------------
# Main
# --------------------
if __name__ == "__main__":
    if not RECIPIENT_EMAIL:
        raise SystemExit("RECIPIENT_EMAIL not set in .env")

    creds = authenticate_google()
    gmail_service = build("gmail", "v1", credentials=creds)

    news = get_news()
    weather = get_weather(DEFAULT_CITY)
    calendar = get_calendar_events()
    quote = get_quote()

    digest = generate_summary(news, weather, calendar, quote, name="Friend")
    today = datetime.datetime.now().strftime("%b %d, %Y")
    subject = f"Daily Digest — {today}"
    send_email(gmail_service, "me", RECIPIENT_EMAIL, subject, digest)
    logger.info("Digest sent successfully.")
