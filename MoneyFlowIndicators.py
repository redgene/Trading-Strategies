
class MoneyFlowIndicators(QCAlgorithm):
    
    def Initialize(self):    

        self.SetStartDate(2019, 10, 25)
        self.SetEndDate(2021, 10, 24)
        self.SetCash(100000)

        self.stock = self.AddEquity('TSLA', Resolution.Hour).Symbol 
        self.PERIODCMF = 21;
        self.PERIODMFI = 10;
        self.SetWarmUp(Math.Max(self.PERIODCMF + 1,self.PERIODMFI + 1))
        self.cmf = self.CMF(self.stock, self.PERIODCMF, Resolution.Daily)  # https://www.chaikinanalytics.com/chaikin-money-flow/
        self.mfi = self.MFI(self.stock, self.PERIODMFI, Resolution.Daily)  # https://school.stockcharts.com/doku.php?id=technical_indicators:money_flow_index_mfi

        self.mfioverboughtsignal = False

        
    def OnData(self, data):
        if self.IsWarmingUp or not self.cmf.IsReady or not self.mfi.IsReady: return

        self.Plot('Indicator', 'cmf',  self.cmf.Current.Value)
        self.Plot('Indicator2', 'mfi', self.mfi.Current.Value)
        self.Log(self.cmf.Current.Value )
        self.Log(self.mfi.Current.Value )
        
        if self.cmf.Current.Value > 0 and self.Portfolio[self.stock].Invested <= 0 and self.mfioverboughtsignal is False:
            self.Debug("CMF buy signal")
            self.SetHoldings(self.stock,1)

        if  self.mfi.Current.Value > 80 and self.Portfolio[self.stock].Invested > 0:
            self.Debug("MFI is greater than 80 overbought liquidate now")
            self.mfioverboughtsignal = True
            self.Liquidate()
        
        if  self.mfioverboughtsignal and self.mfi.Current.Value < 50:
            self.Debug("MFI is less than 50 ready to buy again")
            self.mfioverboughtsignal = False