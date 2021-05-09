from stock import Stock
from pandas import DataFrame
from numpy import where

class BLSH(Stock):
    def __init__(self):
        self.signal = None
    
    def generateSignal(self,start_date=self.start_date,end_date=self.end_date):
        stock_signal = DataFrame(index=self.stock_data.index)
        stock_signal['Price'] = self.stock_data['Adj Close']
        stock_signal['Price Difference'] = self.stock_data['Adj Close'].diff()
        stock_signal['Signal'] = 0
        stock_signal['Signal'] = where(stock_signal['Price Difference']>=0,1.0,0.0)
        stock_signal['Position'] = stock_signal['Signal'].diff()
        self.signal = stock_signal

    def Call(self,date = self.end_date):
        if self.signal.loc[date,'Position'] == -1.0:
            return "Sell"
        elif self.signal.loc[date,'Position'] == 1.0:
            return "Buy"
        else:
            return "Hold"
    
    def mostRecentCall(self,date=self.end_date):
        temp_sig = self.signal[:date]
        temp_sig = self.signal[self.signal['Position']!=0.0]
        return self.Call(temp_sig.index[-1])

