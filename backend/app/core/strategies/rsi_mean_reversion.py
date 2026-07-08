from app.core.strategy import Strategy, Signal, SignalType


class RSIMeanReversion(Strategy):
    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def _calculate_rsi(self, closes):
        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def on_bar(self, bar, history) -> Signal:
        if len(history) < self.period + 1:
            return Signal(
                signal_type=SignalType.HOLD,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason="Not enough history yet"
            )

        closes = [b.close for b in history[-(self.period + 1):]]
        rsi = self._calculate_rsi(closes)

        if rsi < self.oversold:
            return Signal(
                signal_type=SignalType.BUY,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason=f"RSI {rsi:.1f} below oversold threshold {self.oversold}"
            )
        elif rsi > self.overbought:
            return Signal(
                signal_type=SignalType.SELL,
                timestamp=bar.timestamp,
                ticker=bar.ticker,
                reason=f"RSI {rsi:.1f} above overbought threshold {self.overbought}"
            )

        return Signal(
            signal_type=SignalType.HOLD,
            timestamp=bar.timestamp,
            ticker=bar.ticker,
            reason=f"RSI {rsi:.1f} — no signal"
        )
    
    