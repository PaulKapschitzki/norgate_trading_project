# screeners/ema_touch.py
class EmaTouchScreener:
    def screen(self, df):
        df["ema200"] = df["close"].ewm(span=200).mean()
        return df.iloc[-1]["low"] <= df.iloc[-1]["ema200"] <= df.iloc[-1]["close"]
