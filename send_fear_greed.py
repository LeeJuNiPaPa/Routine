import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_fear_and_greed():
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    fng = data.get("fear_and_greed", {})
    score = round(fng.get("score", 0), 1)
    rating = fng.get("rating", "N/A").title()
    prev_close = round(fng.get("previous_close", 0), 1)
    prev_1w = round(fng.get("previous_1_week", 0), 1)
    
    return {
        "score": score,
        "rating": rating,
        "prev_close": prev_close,
        "prev_1w": prev_1w
    }

def send_telegram_message(info):
    rating_emojis = {
        "Extreme Fear": "😱",
        "Fear": "😨",
        "Neutral": "😐",
        "Greed": "😀",
        "Extreme Greed": "🤑"
    }
    emoji = rating_emojis.get(info["rating"], "📊")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    message = (
        f"{emoji} *CNN Fear & Greed Index* ({today_str})\n\n"
        f"• *현재 지수*: `{info['score']}` / 100 ({info['rating']})\n"
        f"• *전일 종가*: `{info['prev_close']}`\n"
        f"• *1주일 전*: `{info['prev_1w']}`\n\n"
        f"[CNN 시장 지표 바로가기](https://edition.cnn.com/markets/fear-and-greed)"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    print("알림 메시지 전송 완료!")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID or CHAT_ID == "YOUR_CHAT_ID":
        raise ValueError("TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 정확히 설정해주세요.")
    
    data = get_fear_and_greed()
    send_telegram_message(data)
