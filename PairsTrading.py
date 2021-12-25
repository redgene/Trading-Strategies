import numpy as np
import pandas as pd
from scipy import stats
from math import floor
from datetime import timedelta
from collections import deque
import itertools as it
from decimal import Decimal

class PairsTradingwithETFsAlgorithm(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2018, 11, 1)  
        self.SetEndDate(2021, 11, 1)  
        self.SetCash(10000000) 
        oil_tickers =  [
            "PXE",  #  Invesco Dynamic Energy Exploration & Prod ETF
            "XOP",  # SPDR S&P Oil & Gas Exploration & Production ETF
            "USO",  # United States Oil ETF
            "USL", #United States 12 Month Oil Fund LP
            "BNO",  # United States Brent Oil Fund LP
            "OILK", # ProShares K-1 Free Crude Oil Strategy ETF
            "DBO",  # Invesco DB Oil Fund
            "UNL", #United States 12 Month Natural Gas Fund LP    
            "IEO",  # iShares US Oil & Gas Exploration & Production ETF
            "IEZ",  # iShares US Oil Equipment & Services ETF
            "OIH", # VanEck Oil Services ETF
            "FTXN" # First Trust NASDAQ Oil & Gas ETF
            ]  
            
        gold_tickers =  [
            "GLD",  #  SPDR Gold Shares    
            "IAU",  # iShares Gold Trust    
            "GLDM",  # SPDR Gold MiniShares Trust    
            "SGOL", #Aberdeen Standard Physical Gold Shares ETF    
            "BAR",  # GraniteShares Gold Shares    
            "IAUM", # iShares Gold Trust Micro ETF of Benef Interest    
            "OUNZ",  #VanEck Merk Gold Trust    
            "AAAU", #Goldman Sachs Physical Gold ETF    
            "DGL",  #Invesco DB Gold Fund    
            "IAUF",  # iShares Gold Strategy ETF    
            "IGLD", # FT Cboe Vest Gold Strategy Target Income ETF    
            "PBUG" # Pacer iPath Gold Trendpilot ETN    
            "BGLD",  # FT Cboe Vest Gold Strategy Quarterly Buffer ETF    
            "WGLD", # wShares Enhanced Gold ETF    
            # "GDX",  # VanEck Gold Miners ETF    
            # "RING" # iShares MSCI Global Gold Miners ETF    
            # "SGDM",  # Sprott Gold Miners ETF    
            # "GLD", #Amplify Pure Junior Gold Miners ETF    
            ]  
            
        
        silver_tickers =  [
            "SLV",  #  iShares Silver Trust    
            "SLVR",  # Aberdeen Standard Physical Silver Shares ETF
            "DBS",  # Invesco DB Silver Fund     
            "SIL", # Global X Silver Miners ETF 
            "SLVP" # iShares MSCI Global Silver Miners ETF    
            ]  
            
        
        self.threshold = 0.5
        self.symbols = []
        for i in oil_tickers:
            self.symbols.append(self.AddEquity(i, Resolution.Daily).Symbol)
        
        self.pairs = {}
        self.formation_period = 90

        self.history_price = {}
        for symbol in self.symbols:
            hist = self.History([symbol.Value], self.formation_period+1, Resolution.Daily)
            if hist.empty: 
                self.symbols.remove(symbol)
            else:
                self.history_price[symbol.Value] = deque(maxlen=self.formation_period)
                for tuple in hist.loc[str(symbol)].itertuples():
                    self.history_price[symbol.Value].append(float(tuple.close))
                if len(self.history_price[symbol.Value]) < self.formation_period:
                    self.symbols.remove(symbol)
                    self.history_price.pop(symbol.Value)

        self.symbol_pairs = list(it.combinations(self.symbols, 2))  
        # Add the benchmark for rebalance timing 
        self.AddEquity("SPY", Resolution.Daily) 
        self.Schedule.On(self.DateRules.MonthStart("SPY"), self.TimeRules.AfterMarketOpen("SPY"), self.Rebalance)
        self.sorted_pairs = None


    def OnData(self, data):
        # Update the price series everyday
        for symbol in self.symbols:
            if data.Bars.ContainsKey(symbol) and symbol.Value in self.history_price:
                self.history_price[symbol.Value].append(float(data[symbol].Close)) 
        if self.sorted_pairs is None: return
        
        for i in self.sorted_pairs:
            pair = Pair(i[0], i[1], self.history_price[i[0].Value],  self.history_price[i[1].Value])
            index_a = pair.index_a[-1]
            index_b = pair.index_b[-1]
            delta = pair.distance()
            if index_a - index_b > self.threshold*delta:
                if not self.Portfolio[pair.symbol_a].Invested and not self.Portfolio[pair.symbol_b].Invested:
                    ratio = self.Portfolio[pair.symbol_a].Price / self.Portfolio[pair.symbol_b].Price
                    quantity = int(self.CalculateOrderQuantity(pair.symbol_a, 1/3))
                    self.Sell(pair.symbol_a, quantity) 
                    self.Buy(pair.symbol_b,  floor(ratio*quantity))                  
            
            elif index_a - index_b < -self.threshold*delta:
                if not self.Portfolio[pair.symbol_a].Invested and not self.Portfolio[pair.symbol_b].Invested:
                    ratio = self.Portfolio[pair.symbol_b].Price / self.Portfolio[pair.symbol_a].Price
                    quantity = int(self.CalculateOrderQuantity(pair.symbol_b, 1/3))
                    self.Sell(pair.symbol_b, quantity) 
                    self.Buy(pair.symbol_a, floor(ratio*quantity))              
            
            # the position is closed when prices revert back
            elif self.Portfolio[i[0]].Invested and self.Portfolio[i[1]].Invested:
                    self.Liquidate(pair.symbol_a) 
                    self.Liquidate(pair.symbol_b)  
      
    
    def Rebalance(self):
        # schedule the event to fire every month to select pairs with the smallest historical distance
        distances = {}
        for i in self.symbol_pairs:
            if i[0].Value in self.history_price and i[1].Value in self.history_price:
                distances[i] = Pair(i[0], i[1], self.history_price[i[0].Value],  self.history_price[i[1].Value]).distance()
        self.sorted_pairs = sorted(distances, key = lambda x: distances[x])[:3]

class Pair:
    def __init__(self, symbol_a, symbol_b, price_a, price_b):
        self.symbol_a = symbol_a
        self.symbol_b = symbol_b
        self.price_a = np.array(price_a)
        self.price_b = np.array(price_b)
        # compute normalized cumulative price indices 
        self.index_a = np.cumprod(self.price_a[1:]/self.price_a[:-1])
        self.index_b = np.cumprod(self.price_b[1:]/self.price_b[:-1])
        
    
    def distance(self):
        return sum((self.index_a -self.index_b)*(self.index_a -self.index_b))