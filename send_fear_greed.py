import os
import requests
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # GUI 없는 환경(GitHub Actions 등) 지원
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

DEFAULT_BOT_TOKEN = "8538544741:AAFuPK-A0lcc0-rSUOHzO2zWD4T0ANVqV_c"
DEFAULT_CHAT_ID = "6809012214"

def get_credentials():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or DEFAULT_BOT_TOKEN
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID
    return token, chat_id

def get_fear_and_greed():
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    fng = data.get("fear_and_greed", {})
    score = round(fng.get("score", 0), 1)
    rating = fng.get("rating", "N/A").title()
    prev_close = round(fng.get("previous_close", 0), 1)
    prev_1w = round(fng.get("previous_1_week", 0), 1)
    prev_1m = round(fng.get("previous_1_month", 0), 1)
    prev_1y = round(fng.get("previous_1_year", 0), 1)
    timestamp = fng.get("timestamp", "")
    
    return {
        "score": score,
        "rating": rating,
        "prev_close": prev_close,
        "prev_1w": prev_1w,
        "prev_1m": prev_1m,
        "prev_1y": prev_1y,
        "timestamp": timestamp
    }

def score_to_angle(score):
    return 180.0 - (score / 100.0) * 180.0

def get_rating_info(score):
    if score < 25:
        return 'Extreme Fear', '#EA4335', '#FCE8E6', '#C5221F'
    elif score < 45:
        return 'Fear', '#F2711C', '#FFE8D6', '#B84500'
    elif score < 55:
        return 'Neutral', '#70757A', '#F1F3F4', '#3C4043'
    elif score < 75:
        return 'Greed', '#34A853', '#E6F4EA', '#137333'
    else:
        return 'Extreme Greed', '#0D652D', '#CEEAD6', '#08481E'

def draw_fng_chart(data, filename='fng_chart.png'):
    fig = plt.figure(figsize=(11, 6), dpi=160, facecolor='white')
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    ax.set_xlim(-1.3, 2.6)
    ax.set_ylim(-0.4, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')

    score = data.get('score', 50)

    # Title & Subtitle
    ax.text(-1.25, 1.3, 'Fear & Greed Index', fontsize=22, weight='bold', color='#111111')
    ax.text(-1.25, 1.15, 'What emotion is driving the market now?', fontsize=11, color='#555555')

    # Segments configuration
    segments = [
        ('Extreme Fear', 0, 25, 'EXTREME\nFEAR'),
        ('Fear', 25, 45, 'FEAR'),
        ('Neutral', 45, 55, 'NEUTRAL'),
        ('Greed', 55, 75, 'GREED'),
        ('Extreme Greed', 75, 100, 'EXTREME\nGREED')
    ]

    r_outer = 1.0
    r_inner = 0.58
    center = (0, 0)

    for name, s_min, s_max, label in segments:
        theta2 = score_to_angle(s_min)
        theta1 = score_to_angle(s_max)
        is_active = (s_min <= score <= s_max) if s_max == 100 else (s_min <= score < s_max)
        
        _, active_border, active_bg, text_color = get_rating_info((s_min + s_max) / 2)
        
        if is_active:
            bg_color = active_bg
            edge_color = active_border
            lw = 2.4
            z = 3
        else:
            bg_color = '#F8F9FA'
            edge_color = '#E9ECEF'
            lw = 1.2
            z = 2

        # Draw segment wedge
        w = patches.Wedge(center, r_outer, theta1, theta2, width=(r_outer - r_inner),
                          facecolor=bg_color, edgecolor=edge_color, linewidth=lw, zorder=z)
        ax.add_patch(w)

        # Label inside segment
        mid_theta = np.deg2rad((theta1 + theta2) / 2)
        text_r = (r_outer + r_inner) / 2
        tx = center[0] + text_r * np.cos(mid_theta)
        ty = center[1] + text_r * np.sin(mid_theta)
        
        # Calculate rotation angle
        rot_deg = (theta1 + theta2) / 2 - 90
        if rot_deg > 90:
            rot_deg -= 180
        elif rot_deg < -90:
            rot_deg += 180

        lbl_color = text_color if is_active else '#6C757D'
        weight = 'bold' if is_active else 'semibold'
        ax.text(tx, ty, label, fontsize=9.5, weight=weight, color=lbl_color,
                ha='center', va='center', rotation=rot_deg, zorder=z+1)

    # Dotted tick arc inside
    r_ticks = 0.44
    for s in range(0, 101, 2):
        th = np.deg2rad(score_to_angle(s))
        px = center[0] + r_ticks * np.cos(th)
        py = center[1] + r_ticks * np.sin(th)
        if s in [0, 25, 50, 75, 100]:
            continue
        ax.plot(px, py, '.', color='#CED4DA', markersize=2.5, zorder=1)

    # Key score numbers
    for s in [0, 25, 50, 75, 100]:
        th = np.deg2rad(score_to_angle(s))
        tx = center[0] + r_ticks * np.cos(th)
        ty = center[1] + r_ticks * np.sin(th)
        ax.text(tx, ty, str(s), fontsize=9, color='#6C757D', weight='semibold', ha='center', va='center', zorder=4)

    # Needle
    needle_angle = score_to_angle(score)
    rad = np.deg2rad(needle_angle)
    needle_len = 0.88
    tip_x = center[0] + needle_len * np.cos(rad)
    tip_y = center[1] + needle_len * np.sin(rad)
    
    perp_rad = rad + np.pi / 2
    base_w = 0.04
    p1 = (center[0] + base_w * np.cos(perp_rad), center[1] + base_w * np.sin(perp_rad))
    p2 = (center[0] - base_w * np.cos(perp_rad), center[1] - base_w * np.sin(perp_rad))
    needle = patches.Polygon([p1, (tip_x, tip_y), p2], closed=True, facecolor='#212529', edgecolor='#111111', zorder=5)
    ax.add_patch(needle)

    # Central hub
    hub = patches.Circle(center, 0.23, facecolor='white', edgecolor='#E9ECEF', linewidth=1.5, zorder=6)
    ax.add_patch(hub)
    ax.text(center[0], center[1] - 0.02, str(int(round(score))), fontsize=26, weight='bold', color='#111111',
            ha='center', va='center', zorder=7)

    # Right side: Historical readings
    hx = 1.35
    hist_items = [
        ('Previous close', data.get('prev_close', 0)),
        ('1 week ago', data.get('prev_1w', 0)),
        ('1 month ago', data.get('prev_1m', 0)),
        ('1 year ago', data.get('prev_1y', 0)),
    ]

    y_start = 0.82
    y_step = 0.28
    for i, (label, val) in enumerate(hist_items):
        cy = y_start - i * y_step
        item_rating, badge_color, badge_bg, _ = get_rating_info(val)
        
        # Label & rating
        ax.text(hx, cy + 0.05, label, fontsize=9.5, color='#6C757D', zorder=2)
        ax.text(hx, cy - 0.06, item_rating, fontsize=11, weight='bold', color='#212529', zorder=2)
        
        # Connecting line
        ax.plot([hx + 0.65, hx + 0.95], [cy, cy], ':', color='#E0E0E0', linewidth=1.5, zorder=1)
        
        # Circle badge
        bx = hx + 1.1
        badge = patches.Circle((bx, cy), 0.08, facecolor=badge_bg, edgecolor=badge_color, linewidth=1.5, zorder=3)
        ax.add_patch(badge)
        ax.text(bx, cy - 0.01, str(int(round(val))), fontsize=10, weight='bold', color=badge_color,
                ha='center', va='center', zorder=4)

    # Footer update time
    raw_ts = data.get('timestamp', '')
    if raw_ts:
        try:
            dt = datetime.fromisoformat(raw_ts.replace('Z', '+00:00'))
            ts_display = dt.strftime("%b %d, %Y %H:%M UTC")
            ax.text(-1.25, -0.3, f'Last updated {ts_display}', fontsize=8.5, color='#888888')
        except Exception:
            pass

    plt.savefig(filename, bbox_inches='tight', facecolor='white', dpi=160)
    plt.close()
    return filename

def send_telegram(info):
    rating_emojis = {
        "Extreme Fear": "😱",
        "Fear": "😨",
        "Neutral": "😐",
        "Greed": "😀",
        "Extreme Greed": "🤑"
    }
    emoji = rating_emojis.get(info["rating"], "📊")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    caption = (
        f"{emoji} *CNN Fear & Greed Index* ({today_str})\n\n"
        f"• *현재 지수*: `{info['score']}` / 100 ({info['rating']})\n"
        f"• *전일 종가*: `{info['prev_close']}`\n"
        f"• *1주일 전*: `{info['prev_1w']}`\n"
        f"• *1개월 전*: `{info['prev_1m']}`\n"
        f"• *1년 전*: `{info['prev_1y']}`\n\n"
        f"[CNN 시장 지표 바로가기](https://edition.cnn.com/markets/fear-and-greed)"
    )
    
    token, chat_id = get_credentials()
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 설정해주세요.")

    # 1. 차트 이미지 생성
    chart_path = None
    try:
        chart_path = draw_fng_chart(info, 'fng_chart.png')
    except Exception as e:
        print(f"차트 이미지 생성 실패 (텍스트로 대체): {e}")

    # 2. 이미지 첨부하여 텔레그램 전송 (sendPhoto)
    if chart_path and os.path.exists(chart_path):
        try:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "Markdown"
            }
            with open(chart_path, "rb") as f:
                files = {"photo": f}
                res = requests.post(url, data=payload, files=files, timeout=20)
            res.raise_for_status()
            print("차트 이미지 및 알림 메시지 전송 완료!")
            return
        except Exception as e:
            print(f"이미지 전송 실패, 텍스트 메시지로 재시도: {e}")

    # 3. 이미지 전송 실패 시 텍스트 전송 (sendMessage fallback)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": caption,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    res = requests.post(url, json=payload, timeout=15)
    res.raise_for_status()
    print("텍스트 알림 메시지 전송 완료!")

if __name__ == "__main__":
    token, chat_id = get_credentials()
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 설정해주세요.")
    
    data = get_fear_and_greed()
    send_telegram(data)
