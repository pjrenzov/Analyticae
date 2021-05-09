from stock import Stock
from pandas import DataFrame
from numpy import where

class BLSH(Stock):
    def __init__(self):
        self.signal = None
        self.portfolio = None
    
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

    def makePortfolio(self,start=self.start_date,end=self.end_date,capital = None):
        if not capital:
            capital = self.stock_signal.loc[start,'Price']
        positions = pd.DataFrame(index=self.signal.index).fillna(0.0) 
        portfolio = pd.DataFrame(index=self.signal.index).fillna(0.0)
        positions[self.symbol] = self.signal['Signal']
        portfolio['postions'] = (positions.multiply(self.signal['Price'], axis=0)) 
        portfolio['cash'] = capital - (positions.diff().multiply(self.signal['Price'], axis=0)).cumsum()
        portfolio['total'] = portfolio['positions'] + portfolio['cash']
        self.portfolio = portfolio
    
    def profit(self,portfolio=self.portfolio,intial_capital=None):
        if not intial_capital:
            intial_capital = self.stock_signal.loc[start,'Price']
        if not portfolio:
            self.makePortfolio()
        return portfolio.iloc[len(portfolio['cash'])-1][2]-intial_capital
    
    def percentageReturn(self,profit=None,intial_capital=None):
        if not intial_capital:
            intial_capital = self.stock_signal.loc[start,'Price']
        if not profit:
            profit = self.profit(intial_capital=intial_capital)
        return float((profit/intial_capital)/100)
        