class EmaTouchScreener:
    def screen(self, df):
        df["ema200"] = df["close"].ewm(span=200).mean()
        # Überprüfe, ob das aktuelle Tief den EMA200 berührt hat
        return df.iloc[-1]["low"] <= df.iloc[-1]["ema200"] <= df.iloc[-1]["close"]

if __name__ == "__main__":
    # Testcode für den Screener
    import pandas as pd
    data = {
        "low": [95, 96, 94, 93, 92],
        "close": [97, 96, 95, 94, 93]
    }
    df = pd.DataFrame(data)
    screener = EmaTouchScreener()
    print("Screen Ergebnis:", screener.screen(df))