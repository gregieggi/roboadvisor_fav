from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.objective_functions import L2_reg
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import numpy as np
import pandas as pd


class MeanVarianceOptimizer:
    def __init__(self, df):
        """
        Initialize the MeanVarianceOptimizer with a DataFrame of stock prices.

        Args:
            df (pd.DataFrame): DataFrame containing stock prices with dates as index.
        """
        self.df = df

    def calculate_portfolio_weights(
        self, risk_aversion, bonds, equities, commodities, market_state="normal"
    ):
        """
        Calculate expected returns and covariance matrix.
        """
        self.expected_returns = expected_returns.mean_historical_return(self.df)
        self.cov_matrix = risk_models.sample_cov(self.df)
        self.ef = EfficientFrontier(self.expected_returns, self.cov_matrix, solver="ECOS")

        plotting_ef = self.ef.deepcopy()

        self.ef.add_objective(L2_reg, gamma=0.1)

        weights = self.ef.max_quadratic_utility(risk_aversion=risk_aversion)

        # Calculate current allocations by asset class
        bond_weight = sum(weights.get(item, 0) for item in bonds)
        equity_weight = sum(weights.get(item, 0) for item in equities)
        commodity_weight = sum(weights.get(item, 0) for item in commodities)

        # Define target allocations based on market state
        if market_state == "boom":
            # Aggressive allocation for boom
            if risk_aversion < 0.47:  # Aggressive investor
                target_bonds = 0.15
                target_equities = 0.75
                target_commodities = 0.10
            elif risk_aversion < 0.6:  # Balanced investor
                target_bonds = 0.25
                target_equities = 0.65
                target_commodities = 0.10
            else:  # Conservative investor
                target_bonds = 0.35
                target_equities = 0.55
                target_commodities = 0.10

        elif market_state == "recession":
            # Defensive allocation for recession
            if risk_aversion < 0.47:  # Aggressive investor
                target_bonds = 0.35
                target_equities = 0.55
                target_commodities = 0.10
            elif risk_aversion < 0.6:  # Balanced investor
                target_bonds = 0.50
                target_equities = 0.40
                target_commodities = 0.10
            else:  # Conservative investor
                target_bonds = 0.65
                target_equities = 0.25
                target_commodities = 0.10

        else:  # normal
            # Keep original allocations
            return weights, plotting_ef

        # Adjust weights to match target allocations
        # Maintain relative weights within each asset class
        for item in bonds:
            if item in weights and bond_weight > 0:
                weights[item] = weights[item] * (target_bonds / bond_weight)

        for item in equities:
            if item in weights and equity_weight > 0:
                weights[item] = weights[item] * (target_equities / equity_weight)

        for item in commodities:
            if item in weights and commodity_weight > 0:
                weights[item] = weights[item] * (target_commodities / commodity_weight)

        return weights, plotting_ef

    def post_process_weights(self, weights, total_portfolio_value):
        """
        Post-process the weights to get the allocation and leftover cash.
        """
        latest_prices = get_latest_prices(self.df)
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value)
        allocation, leftover = da.greedy_portfolio()
        return allocation, leftover

    def calculate_performance(self, weights):
        """
        Calculate performance for specific portfolio weights.
        """

        if isinstance(weights, dict):
            weights_series = pd.Series(weights)
        else:
            weights_series = weights

        # Calculate performance for specific weights
        expected_return = self.expected_returns.dot(weights_series)
        portfolio_variance = weights_series.T.dot(self.cov_matrix).dot(weights_series)
        volatility = np.sqrt(portfolio_variance)

        # calculate Sharpe ratio
        risk_free_rate = 0.02
        sharpe_ratio = (expected_return - risk_free_rate) / volatility

        return expected_return, volatility, sharpe_ratio