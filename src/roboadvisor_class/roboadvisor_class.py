import json
from mvo.meanvarianceoptimizer import MeanVarianceOptimizer
from dataset.ticker_dataset import TickerDataset
from plotting.plotting import (
    generate_charts,
    generate_ef_plot,
)


class RoboAdvisorClass:
    """
    Main roboadvisor class that orchestrates the portfolio optimization.
    """

    def __init__(
        self,
        risk_aversion,
        investment_amount,
        config_path="config/config.json",
        market_state="normal",
    ):
        """
        Initialize the roboadvisor with configuration.

        Args:
            config_path (str): Path to configuration file
        """

        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.risk_aversion = risk_aversion
        self.start_date = self.config["START_DATE"]
        self.investment_amount = investment_amount

        self.bonds = self.config["TICKERS"]["BONDS"]
        self.equities = self.config["TICKERS"]["EQUITIES"]
        self.commodities = self.config["TICKERS"]["COMMODITIES"]
        self.tickers = (
            self.config["TICKERS"]["EQUITIES"]
            + self.config["TICKERS"]["BONDS"]
            + self.config["TICKERS"]["COMMODITIES"]
        )

        self.market_state = market_state

    def load_data(self):
        """
        Load ticker data.

        Args:
            price_type (str): Type of price data to use
        """
        dataset = TickerDataset(self.tickers, self.start_date)
        self.data = dataset.get_data()

    def optimize_portfolio(self):
        """
        Optimize portfolio for given risk aversion.

        Args:
            risk_aversion (float): Risk aversion coefficient

        Returns:
            dict: Portfolio allocation and performance
        """
        self.load_data()

        performance_dict = {
            "weights": None,
            "allocation": None,
            "leftover": None,
            "total_portfolio_value": self.investment_amount,
            "performance": None,
        }

        self.optimizer = MeanVarianceOptimizer(self.data)

        weights, plotting_ef = self.optimizer.calculate_portfolio_weights(
            self.risk_aversion,
            self.bonds,
            self.equities,
            self.commodities,
            market_state=self.market_state,
        )
        allocation, leftover = self.optimizer.post_process_weights(
            weights, self.investment_amount
        )
        performance = self.optimizer.calculate_performance(weights)

        performance_dict["weights"] = weights
        performance_dict["allocation"] = allocation
        performance_dict["leftover"] = leftover
        performance_dict["performance"] = {
            "expected_annual_return": performance[0],
            "annual_volatility": performance[1],
            "sharpe_ratio": performance[2],
        }

        charts = generate_charts(performance_dict)
        ef_plot = generate_ef_plot(plotting_ef, performance)

        return performance_dict, ef_plot, charts


if __name__ == "__main__":
    # Example usage
    roboadvisor = RoboAdvisorClass(risk_aversion=0.5, investment_amount=10000)
    performance_dict, ef_plot, charts = roboadvisor.optimize_portfolio()