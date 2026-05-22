# region imports
from AlgorithmImports import *
from domain.config import *
from domain.models import *
# endregion


class {{STRATEGY_NAME}}AlphaModel(AlphaModel):
    """
    Alpha model for {{STRATEGY_NAME}}.

    Generates trading signals based on {{SIGNAL_DESCRIPTION}}.

    Layer: ORGANISM (orchestrates signal generation)
    Dependencies: domain.config, domain.models
    """

    def __init__(self):
        self.name = "{{STRATEGY_NAME}}Alpha"
        # TODO: Initialize indicators, state tracking

    def Update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        """
        Generate insights based on current data.

        Returns:
            List[Insight]: Trading signals
        """
        insights = []

        # TODO: Implement signal generation logic
        # 1. Check data availability
        # 2. Calculate indicators/signals (use pure functions from domain/)
        # 3. Generate insights

        return insights

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges):
        """Handle universe changes."""
        for added in changes.AddedSecurities:
            # TODO: Initialize tracking for new securities
            pass

        for removed in changes.RemovedSecurities:
            # TODO: Clean up removed securities
            pass
