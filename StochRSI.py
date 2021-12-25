# StochRSI Indicator
# STOCK = "PFE"; 
RSI_PERIOD = 14; STO_PERIOD = 20;

# some functions were not utilized, so ignore those please :P
class StochasticRSI(QCAlgorithm):
    def CoarseSelectionFunction(self, coarse):
        '''Drop securities which have no fundamental data or have too low prices.
        Select those with highest by dollar volume'''

        if self.Time < self.nextLiquidate:
            return Universe.Unchanged

        selected = sorted([x for x in coarse if x.HasFundamentalData and x.Price > 5],
                          key=lambda x: x.DollarVolume, reverse=True)

        return [x.Symbol for x in selected[:self.num_coarse]]
    def FineSelectionFunction(self, fine):
        '''Select securities with highest vs lowest momentum'''

        filtered = [x for x in fine if  (x.EarningReports.BasicAverageShares.ThreeMonths > 0) ]
        self.tickers=[x.Symbol for x in filtered]
        
        return self.tickers
    def consolidation_handler(self, sender, bar):
        if self.rsi.IsReady:
            rsi = self.rsi.Current.Value
            trade_bar = TradeBar(bar.EndTime, self.stock, rsi, rsi, rsi, rsi, 0)
            self.stoch.Update(trade_bar)
            
    def MomentumIndicator(self, tickers):
        self.df = self.History(tickers, 3, Resolution.Daily)
        for ticker in tickers:
            if not self.df.empty:
                currentSymbolData = self.df.loc[ticker]
                
                '''Calculation for Momentum Indicator'''
                
                # self.rsi = self.RSI(ticker, RSI_PERIOD, Resolution.Daily) 
                self.stoch = self.STO(ticker, STO_PERIOD)  # FastStoch, StochK, StochD
                # self.rsi.Updated += self.consolidation_handler

                # new_price = currentSymbolData["close"][2]    
                # old_price= currentSymbolData["close"][0] 
                # Momentum = (new_price - old_price)/old_price
                
                fastVal = self.stoch.FastStoch.Current.Value
                Momentum = fastVal
                
            else:
                Momentum = 0
               
            self.symbolDataBySymbol[ticker] = SymbolData(ticker, Momentum)

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)  
        self.SetEndDate(2021, 10, 20)
        self.SetCash(100000)
        # self.stock  = self.AddEquity(STOCK, Resolution.Daily).Symbol 
        # self.tickers = ["NVDA","NFLX","PFE","COST","BA","SQ"]
        self.tickers = ["XLE","XLB","DIA","XLY","XLP","XLV","XLF","XLK","XLC","XLU","XLRE"]
        for ticker in self.tickers:
            self.AddEquity(ticker)

        # self.UniverseSettings.Resolution = Resolution.Daily
        # self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        
        # self.num_coarse = 200            # Number of symbols selected at Coarse Selection
        # self.symbolDataBySymbol, self.longSymbols,self.shortSymbols = [],[],{}
        # self.MomentumIndicator(self.tickers)
        self.lastday = None
        self.symbolDataBySymbol = {}
        self.SetWarmUp(RSI_PERIOD + STO_PERIOD + 10)
        
    def OnData(self, data):
        if self.IsWarmingUp or not self.stoch: return 

        self.Plot("Indicator", "StochRSI_FastK", self.stoch.FastStoch.Current.Value)
        self.Plot("Indicator", "StochRSI_SlowK", self.stoch.StochK.Current.Value)
        
        ###

        self.MomentumIndicator(self.tickers)
        Max_Momentum = 100
        Min_Momentum = 0
        
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
        ###
        
        # fastVal, slowVal = self.stoch.FastStoch.Current.Value, self.stoch.StochK.Current.Value
        
        # # Enter a long position when the current value of the indicator is less than the 20
        # # if not self.Portfolio.Invested and fastVal < 20:
        # if fastVal < 20:
        #     self.Debug("fastval less than 20")
        #     self.MarketOrder(self.stock, 10)

        # # Liquidate position when the current value of the indicator is greater than 80
        # elif fastVal > 80:
        #     self.Debug("fastval greater than 20")
        #     self.Liquidate()
