import yfinance as yf
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT"]

def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")

    if hist.empty or len(hist) < 2:
        return {"ticker": ticker, "status": "No data available"}

    prev_close = hist["Close"].iloc[-2]
    last_close = hist["Close"].iloc[-1]
    change = last_close - prev_close
    change_pct = (change / prev_close) * 100

    return {
        "ticker": ticker,
        "price": round(last_close, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2)
    }

def run(query: str = "") -> str:
    print("  Fetching stock data...")

    stocks_data = []
    for ticker in WATCHLIST:
        data = get_stock_data(ticker)
        stocks_data.append(data)
        print(f"  Got data for {ticker}")

    stocks_text = ""
    for s in stocks_data:
        if "price" in s:
            direction = "+" if s["change"] >= 0 else ""
            stocks_text += f"{s['ticker']}: ${s['price']} ({direction}{s['change_pct']}%)\n"
        else:
            stocks_text += f"{s['ticker']}: {s['status']}\n"

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system="""You are a professional financial analyst.
        You receive stock data and write a short market brief in Hebrew.
        Highlight notable movers, patterns, and give a short overall market assessment.
        Be concise and clear.""",
        messages=[
            {
                "role": "user",
                "content": f"Here is today's stock data:\n{stocks_text}\nWrite a short financial brief in Hebrew."
            }
        ]
    )

    return response.content[0].text