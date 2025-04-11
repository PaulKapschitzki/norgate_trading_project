# backtest_engine/engine.py
def run_backtest(strategy, data):
    signals = strategy.generate_signals(data)
    results = strategy.backtest(data)
    return results
