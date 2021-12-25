from datetime import datetime
from QuantConnect.Data.UniverseSelection import * 
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class DylansResearch(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015,9, 1)  #Set Start Date
        self.SetEndDate(2021,9,30)    #Set End Date
        self.SetCash(50000)           #Set Strategy Cash
        self.AddEquity("TSLA", Resolution.Daily)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage) 
        self.rsi = self.RSI("TSLA", 14)

    def OnData(self, data):
        
        if not self.rsi.IsReady: 
            return
    
        if self.rsi.Current.Value < 30 and self.Portfolio["TSLA"].Invested <= 0:
            self.Debug("RSI is less then 30")
            # Calculate the number of shares if 100% of our portfolio is TSLA
            shares = self.CalculateOrderQuantity("TSLA", 1.0)
            self.MarketOrder("TSLA", shares)
            self.Debug("Market order was placed")
        
        if self.rsi.Current.Value > 70:
            self.Debug("RSI is greater then 70")
            self.Liquidate()
            
    def OnEndOfDay(self):
        self.Plot("Indicators","RSI", self.rsi.Current.Value)