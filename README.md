# 📊 Routine - CNN Fear & Greed Index 텔레그램 브리핑 봇

매일 아침 미국 주식 시장의 심리 지표인 **CNN Fear & Greed Index(공포 & 탐욕 지수)**를 자동으로 조회하여, **실시간 다이얼 게이지 인포그래픽 차트(이미지)**와 함께 텔레그램으로 브리핑해 주는 자동화 루틴 프로젝트입니다.

---

## 🚀 주요 기능

* **📈 실시간 다이얼 게이지 차트 자동 생성**:
  * CNN 공식 API 데이터를 바탕으로 `matplotlib`을 이용해 CNN 웹사이트와 동일한 반원형 다이얼 게이지 차트를 동적으로 렌더링합니다.
  * 현재 지수, 해당 구간 하이라이트(Extreme Fear, Fear, Neutral, Greed, Extreme Greed), 바늘 지시계 및 전일/1주/1달/1년 전 지표를 포함합니다.
* **📱 텔레그램 카드 알림 (`sendPhoto`)**:
  * 생성된 고화질 차트 이미지와 요약 텍스트(캡션)를 하나의 메시지 카드로 전송합니다.
  * 이미지 전송 오류 시 텍스트 전송으로 자동 전환되는 Fallback 안전장치를 포함합니다.
* **⏰ GitHub Actions 서버리스 자동 실행**:
  * 개인 PC를 켜둘 필요 없이 GitHub 서버에서 매일 정해진 시각에 완전 무료로 무중단 실행됩니다.

---

## ⚙️ 실행 스케줄

* **실행 시각**: 매일 한국 시간(KST) **아침 07:35** (UTC 22:35)
* **피크 타임 회피**: 정각(`:00`)과 30분(`:30`)에 전 세계 cron 작업이 몰려 지연/누락되는 현상을 방지하기 위해 35분으로 최적화되어 있습니다.
* **수동 실행 지원**: GitHub 저장소의 `Actions` 탭에서 언제든지 `Run workflow` 버튼으로 즉시 테스트 실행이 가능합니다.

---

## 🔐 환경 변수 (GitHub Secrets 설정)

보안을 위해 봇 토큰과 채팅 ID는 코드에 노출되지 않고 GitHub Repository Secrets로 안전하게 관리됩니다.

저장소의 **Settings** ➔ **Secrets and variables** ➔ **Actions**에 아래 두 변수를 등록합니다:

| 변수명 | 설명 |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 BotFather에서 발급받은 봇 토큰 |
| `TELEGRAM_CHAT_ID` | 알림을 수신할 사용자의 텔레그램 Chat ID |

---

## 💻 로컬 환경 실행 방법

```bash
# 1. 의존성 패키지 설치
pip install requests matplotlib

# 2. 환경 변수 설정 (PowerShell 기준)
$env:TELEGRAM_BOT_TOKEN="your_bot_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"

# 3. 스크립트 실행
python send_fear_greed.py
```

---

## 📝 최근 수정 및 개선 내역 (Changelog)

### [2026-09-17]
* **차트 이미지 첨부 기능 구현**:
  * CNN 다이얼 게이지 및 히스토리 지표를 렌더링하는 `draw_fng_chart()` 모듈 추가
  * 텔레그램 전송 방식을 기존 단순 텍스트(`sendMessage`)에서 고화질 사진 첨부(`sendPhoto`)로 업그레이드
* **GitHub Actions 스케줄 최적화**:
  * 아침 7시 30분 피크 타임 러너 지연/누락을 방지하기 위해 cron 스케줄을 `35 22 * * *` (07:35 KST)로 변경
* **보안 취약점 개선**:
  * 워크플로 파일 내 하드코딩되어 있던 텔레그램 봇 토큰 및 챗 ID를 GitHub Repository Secrets 연동 방식으로 전환
* **런타임 호환성 업그레이드 (Node.js 24 대응)**:
  * GitHub 러너의 Node.js 20 지원 중단(Deprecation) 경고를 해결하기 위해 `actions/checkout@v7` 및 `actions/setup-python@v7` 공식 최신 버전으로 업그레이드
