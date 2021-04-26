import statistics as stats
import numpy as np
import math

def SMA(price, period = 20):
    history = []
    sma_values = []
    
    for current_price in price:
        history.append(current_price)
        
        if len(history)>period:
            del (history[0])
        
        sma_values.append(stats.mean(history))
        
    return sma_values

def EMA(price, period = 20, U = None):
    if U == None:
        U = 2/(period + 1)
        
    EMA_p = 0
    EMA_values = []
    
    for current_price in price:
        if EMA_p == 0:
            EMA_p = current_price
        else:
            EMA_p = (current_price - EMA_p)*U + EMA_p
            
        EMA_values.append(EMA_p)
        
    return EMA_values

def APO(price, period_fast = 10, period_slow = 40, U_fast = None, U_slow = None):
    if U_fast == None:
        U_fast = 2/(period_fast + 1)
    if U_slow == None:
        U_slow = 2/(period_slow + 1)
    
    EMA_fast = EMA(price, period=period_fast, U=U_fast)
    EMA_slow = EMA(price,period=period_slow, U=U_slow)
    
    return list(np.array(EMA_fast) - np.array(EMA_slow))

def MACD(price, period_fast = 10, period_slow = 40, U_fast = None, U_slow = None, period_signal = 20,U_macd = None):
    if U_fast == None:
        U_fast = 2/(period_fast + 1)
    if U_slow == None:
        U_slow = 2/(period_slow + 1)
    if U_macd == None:
        U_macd = 2/(period_signal + 1)
        
    MACD = APO(price, period_fast, period_slow, U_fast, U_slow)
    MACD_signal = EMA(MACD, period_signal,U=U_macd)
    MACD_histogram = list(np.array(MACD) - np.array(MACD_signal))
    
    return [MACD, MACD_signal, MACD_histogram]

def bBand(price, beta = 2, average = 'SMA', period = 20, U=None):
    history = []
    upper_band = []
    lower_band = []
    
    if average=='SMA':
        avg = SMA(price, period=period)
    if average=='EMA':
        avg = EMA(price,period,U)
    
    for index in range(len(price)):
        history.append(price[index])
        if len(history)>period:
            del history[0]
            
        variance = 0
        
        for hist_price in history:
            variance = variance + ((hist_price - avg[index])**2)
        
        sigma = math.sqrt(variance/len(history))
        
        upper_band.append(avg[index] + beta*sigma)
        lower_band.append(avg[index] - beta*sigma)
    
    return [upper_band,avg,lower_band]

def RSI(close, period = 20):
    gain_history = []
    loss_history = []
    
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
        avg_gain = stats.mean(gain_history) # average gain over lookback period
        avg_loss = stats.mean(loss_history) # average loss over lookback period
        avg_gain_values.append(avg_gain)
        avg_loss_values.append(avg_loss)
        rs = 0
        if avg_loss > 0: 
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
        
    return rsi_values

def standardDeviation(close, period = 20):
    history = []
    sma_values = []
    stddev_values = []
    
    for close_price in close:
        history.append(close_price)
        if len(history)>period:
            del history[0]
            
        sma = stats.mean(history)
        sma_values.append(sma)
        
        variance = 0
        
        for hist_price in history:
            variance = variance + ((hist_price - sma) ** 2)
        stdev = math.sqrt(variance / len(history))
        stddev_values.append(stdev)
    
    return stddev_values

def momentum(close,period=20):
    history = []
    momentum_values = []
    
    for close_price in close:
        history.append(close_price)
        if len(history)>period:
            del history[0]
            
        mom = close_price - history[0]
        momentum_values.append(mom)
    return momentum_values