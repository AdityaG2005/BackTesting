import math


def calculate_daily_returns(equity_curve):
    values = [point["value"] for point in equity_curve]
    returns = []
    for i in range(1, len(values)):
        daily_return = (values[i] - values[i - 1]) / values[i - 1]
        returns.append(daily_return)
    return returns


def calculate_sharpe(equity_curve, risk_free_rate=0.0, trading_days=252):
    returns = calculate_daily_returns(equity_curve)
    if len(returns) < 2:
        return 0.0

    avg_return = sum(returns) / len(returns)
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return 0.0

    daily_rf = risk_free_rate / trading_days
    sharpe = (avg_return - daily_rf) / std_dev
    return sharpe * math.sqrt(trading_days)


def calculate_sortino(equity_curve, risk_free_rate=0.0, trading_days=252):
    returns = calculate_daily_returns(equity_curve)
    if len(returns) < 2:
        return 0.0

    avg_return = sum(returns) / len(returns)
    downside_returns = [r for r in returns if r < 0]

    if len(downside_returns) == 0:
        return 0.0

    downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
    downside_dev = math.sqrt(downside_variance)

    if downside_dev == 0:
        return 0.0

    daily_rf = risk_free_rate / trading_days
    sortino = (avg_return - daily_rf) / downside_dev
    return sortino * math.sqrt(trading_days)


def calculate_cagr(starting_value, final_value, num_trading_days, trading_days_per_year=252):
    if starting_value <= 0 or num_trading_days <= 0:
        return 0.0
    years = num_trading_days / trading_days_per_year
    return ((final_value / starting_value) ** (1 / years)) - 1


def calculate_max_drawdown(equity_curve):
    values = [point["value"] for point in equity_curve]
    if not values:
        return 0.0

    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_dd:
            max_dd = drawdown

    return max_dd


def calculate_win_rate(trades):
    closed_trades = [t for t in trades if not t.is_open]
    if not closed_trades:
        return 0.0

    wins = [t for t in closed_trades if t.pnl > 0]
    return len(wins) / len(closed_trades)

