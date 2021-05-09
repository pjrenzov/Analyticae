from pandas_datareader import data

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