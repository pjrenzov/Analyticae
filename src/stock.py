from pandas.core.frame import DataFrame
from pandas_datareader import data
from statistics import mean 
from math import sqrt
from pandas import Series,Grouper
import numpy as np
import matplotlib.pyplot as plt

class Stock():
    def __init__(self,symbol,start_date,end_date):
        self.symbol     = symbol
        self.start_date = start_date
        self.end_date   = end_date
        self.stock_data = None

    def load_data(self,path=None):
        self.stock_data = data.DataReader(self.symbol, 'yahoo', self.start_date,self.end_date)
    
    def showChart(self,start_date,end_date,subplots={}):
        #ToDo
        return

    def SMA(self, price = Series(),period = 20,add=True):
        history = []
        sma_values = []
        if price.empty:
            price = self.stock_data['Adj Close']
        for current_price in price:
            history.append(current_price)
            
            if len(history)>period:
                del (history[0])
            
            sma_values.append(mean(history))
        if add:
            self.stock_data['SMA{}'.format(period)] = sma_values
        else:
            return sma_values

    def EMA(self, price = Series(), period = 20, U = None,add=True):
        if U == None:
            U = 2/(period + 1)
        if price.empty:
            price = self.stock_data['Adj Close']
        EMA_p = 0
        EMA_values = []
        
        for current_price in price:
            if EMA_p == 0:
                EMA_p = current_price
            else:
                EMA_p = (current_price - EMA_p)*U + EMA_p
                
            EMA_values.append(EMA_p)
        
        if add:
            self.stock_data['EMA{}'.format(period)] = EMA_values
        else:    
            return EMA_values
    
    def APO(self, price = Series(),period_fast = 10, period_slow = 40, U_fast = None, U_slow = None,add=True):
        if U_fast == None:
            U_fast = 2/(period_fast + 1)
        if U_slow == None:
            U_slow = 2/(period_slow + 1)
        if price.empty:
            price = self.stock_data['Adj Close']
        EMA_fast = self.EMA(price,period=period_fast, U=U_fast,add=False)
        EMA_slow = self.EMA(price,period=period_slow, U=U_slow,add=False)

        if add:
            self.stock_data['APO F{}S{}'.format(period_fast,period_slow)] = list(np.array(EMA_fast) - np.array(EMA_slow))
        else:
            return list(np.array(EMA_fast) - np.array(EMA_slow))

    def MACD(self,price=Series(), period_fast = 10, period_slow = 40, U_fast = None, U_slow = None, period_signal = 20,U_macd = None,add=True):
        if U_fast == None:
            U_fast = 2/(period_fast + 1)
        if U_slow == None:
            U_slow = 2/(period_slow + 1)
        if U_macd == None:
            U_macd = 2/(period_signal + 1)
        if price.empty:
            price = self.stock_data['Adj Close']
        MACD = self.APO(price,period_fast = period_fast, period_slow=period_slow, U_fast=U_fast, U_slow=U_slow,add=False)
        MACD_signal = self.EMA(Series(MACD), period_signal,U=U_macd,add=False)
        MACD_histogram = list(np.array(MACD) - np.array(MACD_signal))
        
        if add:
            self.stock_data['MACD F{}S{}'.format(period_fast,period_signal)] = MACD
            self.stock_data['MACD_signal F{}S{}'.format(period_fast,period_slow)] = MACD_signal
            self.stock_data['MACD_histogram F{}S{}'.format(period_fast,period_slow)] = MACD_histogram
        else:
            return [MACD, MACD_signal, MACD_histogram]
    
    def bBand(self,price=Series(), beta = 2, average = 'SMA', period = 20, U=None,add=True):
        history = []
        upper_band = []
        lower_band = []
        if price.empty:
            price = self.stock_data['Adj Close']
        if average=='SMA':
            avg = self.SMA(price, period=period,add=False)
        if average=='EMA':
            avg = self.EMA(price,period,U,add=False)
        
        for index in range(len(price)):
            history.append(price[index])
            if len(history)>period:
                del history[0]
                
            variance = 0
            
            for hist_price in history:
                variance = variance + ((hist_price - avg[index])**2)
            
            sigma = sqrt(variance/len(history))
            
            upper_band.append(avg[index] + beta*sigma)
            lower_band.append(avg[index] - beta*sigma)
        
        if add:
            self.stock_data['Bollinger bands upper {}'.format(period)] = upper_band
            self.stock_data['Bollinger bands lower {}'.format(period)] = lower_band
            self.stock_data['Bollinger bands avg {}'.format(period)]   = avg
        else:
            return [upper_band,avg,lower_band]
        
    def RSI(self, close=Series(),period = 20,add=True):
        gain_history = []
        loss_history = []
        if close.empty:
            close = self.stock_data['Adj Close']
        avg_gain_values = [] 
        avg_loss_values = [] 
        
        rsi_values = []
        
        last_price = 0
        
        for close_price in close:
            if last_price == 0:
                last_price = close_price
            gain_history.append(max(0, close_price - last_price))
            loss_history.append(max(0, last_price - close_price))
            last_price = close_price
            if len(gain_history) > period: 
                del (gain_history[0])
                del (loss_history[0])
            avg_gain = mean(gain_history) # average gain over lookback period
            avg_loss = mean(loss_history) # average loss over lookback period
            avg_gain_values.append(avg_gain)
            avg_loss_values.append(avg_loss)
            rs = 0
            if avg_loss > 0: 
                rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        if add:
            self.stock_data['RSI{}'.format(period)] = rsi_values
        else:
            return rsi_values
        
    def standardDeviation(self, close=Series(),period = 20,add=True):
        history = []
        sma_values = []
        stddev_values = []
        if close.empty:
            close = self.stock_data['Adj Close']
        for close_price in close:
            history.append(close_price)
            if len(history)>period:
                del history[0]
                
            sma = mean(history)
            sma_values.append(sma)
            
            variance = 0
            
            for hist_price in history:
                variance = variance + ((hist_price - sma) ** 2)
            stdev = sqrt(variance / len(history))
            stddev_values.append(stdev)
        if add:
            self.stock_data['stdDev{}'.format(period)] = stddev_values
        else:
            return stddev_values
    
    def momentum(self,close=Series(),period=20,add=True):
        history = []
        momentum_values = []
        if  close.empty:
            close = self.stock_data['Adj Close']
        for close_price in close:
            history.append(close_price)
            if len(history)>period:
                del history[0]
                
            mom = close_price - history[0]
            momentum_values.append(mom)
        if add:
            self.stock_data['Momentum{}'.format(period)] = momentum_values
        else:
            return momentum_values

    def returns(self, start=None,end=None,add=True,method='SIMP'):
        if not start:
            start = self.stock_data.index[0]
        if not end:
            end = self.stock_data.index[-1]
        if add:
            if method=='SIMP':
                self.stock_data['Simple_return'] = self.stock_data['Adj Close']
                self.stock_data['Simple_return'] = self.stock_data.Simple_return.pct_change()
            else:
                self.stock_data['log_returns'] = self.stock_data['Adj Close']
                self.stock_data['log_returns'] = np.log(self.stock_data.log_returns/self.stock_data.log_returns.shift(1))
        else:
            prices = DataFrame()
            prices['Return'] = self.stock_data.loc[start:end,'Adj Close']
            if method=='SIMP':
                return prices.pct_change()
            else:
                return np.log(prices/prices.shift(1))
    
    def realized_volatility(self,x):
        return np.sqrt(np.sum(x**2))
    
    def RV(self):
        try:
            rv = self.stock_data['log_returns']
        except:
            self.returns(method='LOG')
            rv = self.stock_data['log_returns']
        return self.stock_data.groupby(Grouper(freq='M')).apply(self.realized_volatility).log_returns*np.sqrt(12)

    def indentify_outliers(self,row,n_sigmas=3):
        x = row['Return']
        mu = row['mean']
        sigma = row['std']
        if (x > mu + 3 * sigma) | (x < mu - 3 * sigma):
            return 1
        else:
            return 0

    def findOutliers(self,start=None,end=None,n_sigma=3,window=21,plot=True):
        if not start:
            start = self.stock_data.index[0]
        if not end:
            end = self.stock_data.index[-1]

        outlier = DataFrame(self.returns(start=start,end=end,add=False))
        temp = outlier[['Return']].rolling(window=window).agg(['mean','std'])
        temp.columns = temp.columns.droplevel()
        outlier = outlier.join(temp)
        outlier['outlier'] = outlier.apply(self.indentify_outliers,axis=1)
        outliers = outlier.loc[outlier['outlier']==1,['Return']]
        if plot:
            fig, ax = plt.subplots()
            ax.plot(outlier.index, outlier.Return,
                    color='blue', label='Normal')
            ax.scatter(outliers.index, outliers.Return,
                        color='red', label='Anomaly')
            ax.set_title("{}'s stock returns".format(self.symbol))
            ax.legend(loc='lower right')
        return outliers      