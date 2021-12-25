class PensiveBlackSnake(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1)  
        self.SetEndDate(2021, 10, 10) 
        self.SetCash(100000)  
        self.AddUniverse(self.CoarseSelectionFilter,self.FineSelectionFilter)
        self.UniverseSettings.Resolution = Resolution.Daily 
        
        # Set a minnimum Time that a stock will remain in the universe
        #self.UniverseSettings.MinimumTimeInUniverse  = timedelta(days=25)
        
        # Adjust the cash buffer from the default 2.5% to 5%
        #self.Settings.FreePortfolioValuePercentage = 0.05

    
    # https://www.quantconnect.com/docs/algorithm-reference/universes   
    def CoarseSelectionFilter(self, coarse):
        sortedByDollarVolume = sorted(coarse, key=lambda c: c.DollarVolume, reverse=True)
        filteredByPrice = [c.Symbol for c in sortedByDollarVolume if c.Price > 10 and c.HasFundamentalData]
        return filteredByPrice[:100] 
    
    # Fundamentals-Morningstar-US-Equity-Data
    # https://www.quantconnect.com/docs/data-library/fundamentals
    def FineSelectionFilter(self, fine):
        sortedByPeRatio = sorted(fine, key=lambda x: x.ValuationRatios.PERatio, reverse=False)
        sortedByEbitdaG = sorted(sortedByPeRatio, key=lambda x: x.ValuationRatios.EVToEBITDA, reverse=False)

        return [ x.Symbol for x in sortedByEbitdaG[0:10] ]
    
    def OnSecuritiesChanged(self, changes):
        self.changes = changes
        self.Log(f"OnSecuritiesChanged({self.Time}):: {changes}")
        
        for security in self.changes.RemovedSecurities:
            if security.Invested:
                self.Liquidate(security.Symbol)
        
        for security in self.changes.AddedSecurities:
            # Allocate 10% portfolio/ security
            self.SetHoldings(security.Symbol, 0.1)