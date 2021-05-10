from pandas_datareader import data
from statistics import mean 

class Stock():
    def __init__(self,symbol,start_date,end_date):
        self.symbol     = symbol
        self.start_date = start_date
        self.end_date   = end_date
        self.stock_data = None

    def load_data(self,path=None):
        self.stock_data = data.DataReader(self.symbol, 'yahoo', self.start_date,self.end_date)
    
    def showChart(self,start_date,end_date):
        #ToDo
        return

    def SMA(self, period = 20,add=True):
        history = []
        sma_values = []
        
        for current_price in self.stock_data['Adj Close']:
            history.append(current_price)
            
            if len(history)>period:
                del (history[0])
            
            sma_values.append(mean(history))
        if add:
            self.stock_data['SMA{}'.format(period)] = sma_values
        else:
            return sma_values

    def EMA(self, period = 20, U = None,add=True):
        if U == None:
            U = 2/(period + 1)
            
        EMA_p = 0
        EMA_values = []
        
        for current_price in self.stock_data['Adj Close']:
            if EMA_p == 0:
                EMA_p = current_price
            else:
                EMA_p = (current_price - EMA_p)*U + EMA_p
                
            EMA_values.append(EMA_p)
        
        if add:
            self.stock_data['EMA{}'.format(period)] = EMA_values
        else:    
            return EMA_values
    
    def APO(self, period_fast = 10, period_slow = 40, U_fast = None, U_slow = None,add=True):
        if U_fast == None:
            U_fast = 2/(period_fast + 1)
        if U_slow == None:
            U_slow = 2/(period_slow + 1)
        price = self.stock_data['Adj Close']
        EMA_fast = EMA(price, period=period_fast, U=U_fast)
        EMA_slow = EMA(price,period=period_slow, U=U_slow)

        if add:
            self.stock_data['APO F{}S{}'.format(period_fast,period_slow)] = list(np.array(EMA_fast) - np.array(EMA_slow))
        else:
            return list(np.array(EMA_fast) - np.array(EMA_slow))

    def MACD(self, period_fast = 10, period_slow = 40, U_fast = None, U_slow = None, period_signal = 20,U_macd = None):
        if U_fast == None:
            U_fast = 2/(period_fast + 1)
        if U_slow == None:
            U_slow = 2/(period_slow + 1)
        if U_macd == None:
            U_macd = 2/(period_signal + 1)
        price = self.stock_data['Adj Close']
        MACD = APO(price, period_fast, period_slow, U_fast, U_slow)
        MACD_signal = EMA(MACD, period_signal,U=U_macd)
        MACD_histogram = list(np.array(MACD) - np.array(MACD_signal))
        
        return [MACD, MACD_signal, MACD_histogram]