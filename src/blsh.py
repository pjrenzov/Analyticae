from stock import Stock
from pandas import DataFrame

class BLSH(Stock):
    def __init__(self):
        self.signal = None
    
    def generateSignal(self,start_date=self.start_date,end_date=self.end_date):
        stock_signal = DataFrame(index=self.stock_data.index)
        stock_signal['Price'] = self.stock_data['Adj Close']
        stock_signal['Price Difference'] = self.stock_data['Adj Close'].diff()
        self.signal = stock_signal

    