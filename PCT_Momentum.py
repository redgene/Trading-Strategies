import numpy as np

class MomentumAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)    # Set Start Date
        self.SetEndDate(2021, 10, 22)      # Set End Date
        self.SetCash(100000)             # Set Strategy Cash

        #self.tickers = ["NVDA","NFLX","PFE","COST","BA","SQ"]
        self.tickers = ["XLE","XLB","DIA","XLY","XLP","XLV","XLF","XLK","XLC","XLU","XLRE"]

        for ticker in self.tickers:
            self.AddEquity(ticker)
            
        self.lastday = None

        self.symbolDataBySymbol = {}
        

        self.SetWarmUp(timedelta(days=4))


    def MomentumIndicator(self, tickers):
        
        self.df = self.History(tickers, 3, Resolution.Daily)
        
        for ticker in tickers:
            
            if not self.df.empty:
                currentSymbolData = self.df.loc[ticker]
                
                '''Calculation for Momentum Indicator'''
                
                new_price = currentSymbolData["close"][2]    
                old_price= currentSymbolData["close"][0] 
                
                Momentum = (new_price - old_price)/old_price

            else:
                
                Momentum = 0
               
            self.symbolDataBySymbol[ticker] = SymbolData(ticker, Momentum)
            
            
            
    def OnData(self, data):

        if self.IsWarmingUp: return
        
        day= self.Time.day
        if day == self.lastday:
            return 
        self.lastday = day
        
        self.MomentumIndicator(self.tickers)
            
        Max_Momentum = -1
        Min_Momentum = 1
        
        Max_ticker = "XLE"
        Min_ticker = "XLE"
        
        for ticker, info in self.symbolDataBySymbol.items():    
            if info.Momentum > Max_Momentum:
                Max_Momentum=info.Momentum
                Max_ticker = ticker
            elif info.Momentum < Min_Momentum:
                Min_Momentum=info.Momentum
                Min_ticker = ticker
        
        for ticker in self.tickers:
            if ticker!=Max_ticker and self.Portfolio[ticker].Invested: self.Liquidate(ticker)
                
        if self.Portfolio[Max_ticker].Invested:
            if self.Portfolio[Max_ticker].IsShort:
                self.Liquidate(Max_ticker)
                self.SetHoldings(Max_ticker, 1)
        else: 
            self.SetHoldings(Max_ticker, 1)
            
        # if self.Portfolio[Min_ticker].Invested:
        #     if self.Portfolio[Min_ticker].IsLong:
        #         self.Liquidate(Min_ticker)
        #         self.SetHoldings(Min_ticker, -0.5)
        # else: 
        #     self.SetHoldings(Min_ticker, -0.5)
    
                    
class SymbolData:
    def __init__(self, symbol, Momentum):
        
        self.Symbol = symbol
        self.Momentum = Momentum