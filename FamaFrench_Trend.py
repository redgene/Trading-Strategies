import numpy as np

class MomentumAlgorithm(QCAlgorithm):
    ''' Stocks Selecting Strategy based on Fama French 5 Factors Model
        Reference: https://tevgeniou.github.io/EquityRiskFactors/bibliography/FiveFactor.pdf
    '''
    def Initialize(self):
        self.SetStartDate(2010, 1, 1)    # Set Start Date
        self.SetEndDate(2019, 8, 1)      # Set End Date
        self.SetCash(100000)             # Set Strategy Cash

        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)

        self.num_coarse = 200            # Number of symbols selected at Coarse Selection

        self.symbolDataBySymbol = {}
        
        self.longSymbols = []            # Contains the stocks we'd like to long
        self.shortSymbols = []           # Contains the stocks we'd like to short


        self.MomentumIndicator(self.tickers)

        self.SetWarmUp(timedelta(days=3))

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
            
        sorted_dict = sorted(symbolDataBySymbol.items(), key = lambda x: x.Momentum, reverse = False)
        symbols = [x.Symbol for x in sorted_dict]

        # Pick the stocks with the highest scores to long
        self.longSymbols= symbols[:5]
        # Pick the stocks with the lowest scores to short
        self.shortSymbols = symbols[-5:]
        
        
        for holding in self.Portfolio.Values:
            # If the holding is in the long/short list for the next month, don't liquidate
            if holding.Symbol in self.longSymbols or holding.Symbol in self.shortSymbols:
                continue
            # If the holding is not in the list, liquidate
            if holding.Invested:
                self.Liquidate(holding.Symbol)

        count = len(self.longSymbols + self.shortSymbols)

        # It means the long & short lists for the month have been cleared
        if count == 0: 
            return

        # Open long position at the start of every month
        for symbol in self.longSymbols:
            self.SetHoldings(symbol, 1/count)

        # Open short position at the start of every month    
        for symbol in self.shortSymbols:
            self.SetHoldings(symbol, -1/count)

        # After opening positions, clear the long & short symbol lists until next universe selection
        self.longSymbols.clear()
        self.shortSymbols.clear()
                    
class SymbolData:
    def __init__(self, symbol, Momentum):
        
        self.Symbol = symbol
        self.Momentum = Momentum