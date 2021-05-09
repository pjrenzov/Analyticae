from pandas_datareader import data

class Stock():
    def __init__(self):
        self.symbol     = None
        self.start_date = None
        self.end_date   = None
        self.stock_data = None

    def load_data(self,path=None):
        self.stock_data = data.DataReader(symbol, 'yahoo', start_date,end_date)
    
    def showChart(self,start_date,end_date):
        #ToDo
        return