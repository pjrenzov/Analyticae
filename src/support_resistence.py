from .stock import Stock
from pandas import DataFrame
from numpy import where
import pandas as pd
import numpy as np

class supportAndResistence(Stock):
    def __init__(self,stock):
        stock_signal = pd.DataFrame(index=stock.stock_data.index)
        stock_signal['price'] = stock.stock_data['Adj Close']
        self.signal = stock_signal
        self.portfolio = pd.Series()
        super().__init__(stock.symbol, stock.start_date, stock.end_date)
        self.stock_data = stock.stock_data
    
    def generateSignal(self,bin_width=20):
        data = self.signal
        data['sup_tolerance'] = pd.Series(np.zeros(len(data)))
        data['res_tolerance'] = pd.Series(np.zeros(len(data)))
        data['sup_count'] = pd.Series(np.zeros(len(data)))
        data['res_count'] = pd.Series(np.zeros(len(data)))
        data['sup'] = pd.Series(np.zeros(len(data)))
        data['res'] = pd.Series(np.zeros(len(data)))
        data['positions'] = pd.Series(np.zeros(len(data)))
        data['signal'] = pd.Series(np.zeros(len(data)))
        in_support=0
        in_resistance=0

        for x in range((bin_width - 1) + bin_width, len(data)):
            data_section = data[x - bin_width:x + 1]
            support_level=min(data_section['price'])
            resistance_level=max(data_section['price'])
            range_level=resistance_level-support_level
            data['res'][x]=resistance_level
            data['sup'][x]=support_level
            data['sup_tolerance'][x]=support_level + 0.2 * range_level
            data['res_tolerance'][x]=resistance_level - 0.2 * range_level
            if data['price'][x]>=data['res_tolerance'][x] and data['price'][x] <= data['res'][x]:
                in_resistance+=1
                data['res_count'][x]=in_resistance
            elif data['price'][x] <= data['sup_tolerance'][x] and data['price'][x] >= data['sup'][x]:
                in_support += 1
                data['sup_count'][x] = in_support
            else:
                in_support=0
                in_resistance=0
            if in_resistance>2:
                data['signal'][x]=1
            elif in_support>2:
                data['signal'][x]=0
            else:
                data['signal'][x] = data['signal'][x-1]
            
        data['Positions']=data['signal'].diff()
        self.signal = data
    
    def Call(self,date = None):
        if not date:
            date = self.stock_data.index[-1]
        if self.signal.loc[date,'Positions'] == -1.0:
            return "Sell"
        elif self.signal.loc[date,'Positions'] == 1.0:
            return "Buy"
        else:
            return "Hold"
    
    def mostRecentCall(self,date=None):
        if not date:
            date=self.end_date
        temp_sig = self.signal[:date]
        temp_sig = self.signal[self.signal['Positions']!=0.0]
        return self.Call(temp_sig.index[-1])
    
    def makePortfolio(self,start=None,end=None,capital=None):
        positions = DataFrame(index=self.signal.index).fillna(0.0) 
        portfolio = DataFrame(index=self.signal.index).fillna(0.0)
        if not start:
            start=self.signal.index[0]
        if not end:
            end=self.signal.index[-1]
        if not capital:
            capital = self.signal.loc[start,'price']

        positions[self.symbol] = self.signal['signal']
        portfolio['Positions'] = (positions.multiply(self.signal['price'], axis=0))
        portfolio['cash'] = capital - (positions.diff().multiply(self.signal['price'], axis=0)).cumsum()
        portfolio['total'] = portfolio['Positions'] + portfolio['cash']
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