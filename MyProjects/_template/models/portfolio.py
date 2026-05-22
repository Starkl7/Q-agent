# region imports
from AlgorithmImports import *
from domain.config import *
from domain.models import *
# endregion


class {{STRATEGY_NAME}}PortfolioModel(PortfolioConstructionModel):
    """
    Portfolio construction for {{STRATEGY_NAME}}.

    Converts insights to portfolio targets with {{PORTFOLIO_DESCRIPTION}}.

    Layer: ORGANISM (orchestrates portfolio construction)
    Dependencies: domain.config, domain.models
    """

    def __init__(self):
        # TODO: Initialize portfolio construction parameters
        pass

    def CreateTargets(self, algorithm: QCAlgorithm, insights: List[Insight]) -> List[PortfolioTarget]:
        """
        Convert insights to portfolio targets.

        Args:
            algorithm: The algorithm instance
            insights: List of alpha insights

        Returns:
            List[PortfolioTarget]: Position targets
        """
        targets = []

        # TODO: Implement portfolio construction
        # 1. Process insights
        # 2. Apply risk constraints (use pure functions from domain/)
        # 3. Generate targets

        return targets

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges):
        """Handle universe changes."""
        pass
