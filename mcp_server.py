from mcp.server.fastmcp import FastMCP
from typing import Annotated
import yfinance as yf
from langchain_experimental.utilities import PythonREPL
from typing import Annotated
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import contextlib
import sys


mcp = FastMCP(
    name="count-r",
    host="127.0.0.1",
    port=8080,
    timeout=30,
    debug=True
    )

repl = PythonREPL()

@mcp.tool()
def get_stock_data(
    ticker: Annotated[str, "企業のティッカーシンボル（例：AAPL、7203.T）"],
    start_date: Annotated[str, "データ取得の開始日 (YYYY-MM-DD)"],
    end_date: Annotated[str, "データ取得の終了日 (YYYY-MM-DD)"]
) -> str:
    """
    Yahooファイナンスから株価情報（日付、始値、高値、安値、終値、出来高、銘柄）を取得します。
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return f"{ticker} のデータが見つかりませんでした。"

        df = df.reset_index()
        df["Ticker"] = ticker
        df = df.rename(columns={
            "Date": "日付", "Open": "始値", "High": "高値",
            "Low": "安値", "Close": "終値", "Volume": "出来高",
            "Ticker": "銘柄"
        })

        result = df[["日付", "銘柄", "始値", "高値", "安値", "終値", "出来高"]].to_string(index=False)
        return f"{ticker} の株価データ:\n```\n{result}\n```"

    except Exception as e:
        return f"データ取得中にエラーが発生しました: {repr(e)}"



@mcp.tool()
def python_repl(code: Annotated[str, "チャートを生成するために実行する Python コード"]) -> str:
    """
    Python コードを実行し、matplotlib のグラフが含まれる場合は base64 PNG 画像として返す。
    """
    try:
        # stdout の捕捉
        stdout = BytesIO()
        with contextlib.redirect_stdout(sys.stdout):
            exec(code, globals())

        # matplotlibの画像を base64 に変換
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()

        return f"Successfully executed:\n```python\n{code}\n```\n\n![chart](data:image/png;base64,{img_base64})"
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"

@mcp.tool()
def count_r(word: str) -> int:
    """
    Count the number of 'r' letters in a given word.
    """
    try:
        if not isinstance(word, str):
            return 0
        return word.lower().count("r")  # .lower() にカッコを追加
    except Exception as e:
        return 0


if __name__ == "__main__":
    mcp.run(transport="stdio")
