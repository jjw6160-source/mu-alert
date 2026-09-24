import os
import json
import urllib.request
import urllib.parse

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SYMBOL = "MUUSDT"
INTERVAL = "15m"


def get_klines():
    url = (
        "https://fapi.binance.com/fapi/v1/klines"
        f"?symbol={SYMBOL}&interval={INTERVAL}&limit=5"
    )

    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode())


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()


def candle_type(candle):
    open_price = float(candle[1])
    close_price = float(candle[4])

    if close_price > open_price:
        return "bull"
    elif close_price < open_price:
        return "bear"
    else:
        return "doji"


def check_signal():
    candles = get_klines()

    # 현재 진행 중인 봉 제외
    closed = candles[:-1]

    c1 = closed[-3]
    c2 = closed[-2]
    c3 = closed[-1]

    t1 = candle_type(c1)
    t2 = candle_type(c2)
    t3 = candle_type(c3)

    close_price = float(c3[4])

    bull_signal = (
        t1 != "bull"
        and t2 == "bull"
        and t3 == "bull"
    )

    bear_signal = (
        t1 != "bear"
        and t2 == "bear"
        and t3 == "bear"
    )

    if bull_signal:
        send_telegram(
            f"🟢 MU 15분봉 2연속 양봉 최초 확정\n"
            f"확정가: {close_price}"
        )

    elif bear_signal:
        send_telegram(
            f"🔴 MU 15분봉 2연속 음봉 최초 확정\n"
            f"확정가: {close_price}"
        )


check_signal()
