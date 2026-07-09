from app.core.strategy import SignalType
from app.core.order_matcher import OrderMatcher
from app.core.portfolio import Portfolio


class BacktestEngine:
    def __init__(self, strategy, starting_cash=10000, slippage_pct=0.001, commission_pct=0.001):
        self.strategy = strategy
        self.order_matcher = OrderMatcher(slippage_pct, commission_pct)
        self.portfolio = Portfolio(starting_cash, self.order_matcher)
        self.equity_curve = []

    def run(self, bars, ticker):
        history = []

        for i, bar in enumerate(bars):
            bar.ticker = ticker
            signal = self.strategy.on_bar(bar, history)
            history.append(bar)

            if signal.signal_type != SignalType.HOLD:
                is_last_bar = (i == len(bars) - 1)
                if not is_last_bar:
                    next_bar = bars[i + 1]
                    self.portfolio.process_signal(
                        signal_type=signal.signal_type,
                        ticker=ticker,
                        next_bar_open=next_bar.open,
                        timestamp=next_bar.timestamp
                    )

            current_value = self.portfolio.total_value(bar.close)
            self.equity_curve.append({
                "timestamp": bar.timestamp,
                "value": current_value
            })

        return {
            "final_value": self.equity_curve[-1]["value"] if self.equity_curve else self.portfolio.starting_cash,
            "starting_cash": self.portfolio.starting_cash,
            "trades": self.portfolio.trades,
            "equity_curve": self.equity_curve
        }
    
    