from .stock import Stock
from pandas import DataFrame
from numpy import where

class BLSH(Stock):
    def __init__(self,stock):
        self.signal = None
        self.portfolio = None
        super().__init__(stock.symbol, stock.start_date, stock.end_date)
        

    def generateSignal(self,start_date=None,end_date=None):
        if not start_date:
            start_date=self.start_date + ' 00:00:00'
        if not end_date:
            end_date=self.end_date + ' 00:00:00'
        if not self.stock_data:
            self.load_data()
        stock_signal = DataFrame(index=self.stock_data.index)
        stock_signal['Price'] = self.stock_data['Adj Close']
        stock_signal['Price Difference'] = self.stock_data['Adj Close'].diff()
        stock_signal['Signal'] = 0
        stock_signal['Signal'] = where(stock_signal['Price Difference']>=0,1.0,0.0)
        stock_signal['Position'] = stock_signal['Signal'].diff()
        self.signal = stock_signal

    def Call(self,date = None):
        if not date:
            date = self.end_date
        if self.signal.loc[date,'Position'] == -1.0:
            return "Sell"
        elif self.signal.loc[date,'Position'] == 1.0:
            return "Buy"
        else:
            return "Hold"

    def mostRecentCall(self,date=None):
        if not date:
            date=self.end_date
        temp_sig = self.signal[:date]
        temp_sig = self.signal[self.signal['Position']!=0.0]
        return self.Call(temp_sig.index[-1])

    def makePortfolio(self,start=None,end=None,capital = None):
        if not start:
            start=self.signal.index[0]
        if not end:
            end=self.signal.index[-1]
        if not capital:
            capital = self.signal.loc[start,'Price']
        positions = DataFrame(index=self.signal.index).fillna(0.0) 
        portfolio = DataFrame(index=self.signal.index).fillna(0.0)
        positions[self.symbol] = self.signal['Signal']
        portfolio['positions'] = (positions.multiply(self.signal['Price'], axis=0)) 
        portfolio['cash'] = capital - (positions.diff().multiply(self.signal['Price'], axis=0)).cumsum()
        portfolio['total'] = portfolio['positions'] + portfolio['cash']
        self.portfolio = portfolio

    def profit(self):
        if not self.portfolio.empty:
            self.makePortfolio()
        total = self.portfolio['total']
        total = total[total.notna()]
        return total[-1]-total[0]
        
    def percentageReturn(self):
        if not self.portfolio.empty:
            self.makePortfolio()
        total = self.portfolio['total']
        total = total[total.notna()]
        return ((total[-1]-total[0])/total[0])*100
        
