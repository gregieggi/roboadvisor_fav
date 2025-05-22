import yfinance as yf
import pandas as pd


class TickerDataset:
    """
    This class gets ticker data from yahoo finance and converts it to a usable dataset.

    Args:
    ticker (str): The ticker symbol of the stock.
    start_date (str): The start date of the data to get in the format 'YYYY-MM-DD'.
    """

    def __init__(self, tickers: list, start_date: str, price_type: str = "High"):
        self.tickers = tickers
        self.start_date = start_date
        self.price_type = price_type

    def get_data(self):

        data = pd.DataFrame(yf.download(self.tickers, start=self.start_date))

        # Here we chose to only keep the daily high prices
        data = data.filter(like=self.price_type, axis=1)

        # Here we filled the missing values for tickers that didn't exist at a certain starting date
        # For example, if a ticker was added to the market in 2021, we fill the missing values with the next available value
        # Another option would be to find the a common starting date, but this would get complicated with a lot of tickers
        data = data.bfill()

        data.columns = [col[1] for col in data.columns]
        data = data.set_index(data.index.date)

        return pd.DataFrame(data)


if __name__ == "__main__":
    # Example usage
    dataset = TickerDataset(tickers=["AAPL", "MSFT"], start_date="2020-01-01")
    data = dataset.get_data()
    print(data.head())