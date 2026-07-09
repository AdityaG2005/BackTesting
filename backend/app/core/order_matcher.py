class OrderMatcher:
    def __init__(self, slippage_pct=0.001, commission_pct=0.001):
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct

    def calculate_fill_price(self, next_bar_open, is_buy):
        if is_buy:
            fill_price = next_bar_open * (1 + self.slippage_pct)
        else:
            fill_price = next_bar_open * (1 - self.slippage_pct)
        return fill_price

    def calculate_commission(self, fill_price, quantity):
        trade_value = fill_price * quantity
        return trade_value * self.commission_pct
    
    