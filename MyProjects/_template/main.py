# region imports
from AlgorithmImports import *
from models import *
# endregion


class {{STRATEGY_CLASS}}(QCAlgorithm):
    """
    {{STRATEGY_DESCRIPTION}}

    Architecture: Atomic Structure
    - Composition Root: This file (main.py)
    - Organisms: models/ (alpha, portfolio, execution, logger)
    - Molecules + Atoms: domain/ (business logic, DTOs, config)
    """

    def Initialize(self):
        # === Backtest Configuration ===
        self.SetStartDate(2022, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100_000)
        self.SetBenchmark("SPY")

        # === Universe ===
        # TODO: Configure universe selection
        # self.AddEquity("SPY", Resolution.Daily)
        # self.SetUniverseSelection(...)

        # === Models (Organisms) ===
        # TODO: Wire up models
        # self.SetAlpha(...)
        # self.SetPortfolioConstruction(...)
        # self.SetExecution(...)

        # === Warmup ===
        # self.SetWarmUp(timedelta(days=252))

        # === Scheduled Events ===
        # self.Schedule.On(
        #     self.DateRules.EveryDay(),
        #     self.TimeRules.AfterMarketOpen("SPY", 30),
        #     self._daily_rebalance
        # )

    def OnData(self, data: Slice):
        """Process incoming data."""
        pass

    def OnOrderEvent(self, orderEvent: OrderEvent):
        """Handle order events."""
        pass

    def OnEndOfAlgorithm(self):
        """Finalize and save data to ObjectStore."""
        pass
