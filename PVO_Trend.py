# Percentage Volume Oscillator (PVO)
# ---------------------------------
STOCK = 'SQ'
MA_F= 12; MA_S = 26; # default
#MA_F= 5; MA_S = 21; # for short term trading
#MA_F= 21; MA_S = 42; # for long term traing
UpperBound = 20; LowerBound = -20;
# ---------------------------------
class PercentageVolumeOscillator(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021,10,24)
        self.SetCash(100000)
        self.stock = self.AddEquity(STOCK, Resolution.Daily).Symbol
        
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        v = self.History(self.stock,MA_S,Resolution.Daily)['volume'].unstack(level = 0).dropna() 
        pvo = float(100*(v[-MA_F:].mean()/v[-MA_S:].mean() - 1))
        
        holdings = self.Portfolio[STOCK].Quantity

        # if buy volume exceeds the predetermined value, then let's go long
        if holdings <= 0 and pvo > UpperBound:
            # longterm says buy as well
            self.SetHoldings(STOCK, 1.0)

        # if buy volume subceeds the predetermined value, then let's go short
        elif holdings >= 0 and pvo < LowerBound:
            self.Liquidate(STOCK)