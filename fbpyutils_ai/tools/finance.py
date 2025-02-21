import pandas as pd
import yfinance as yf

from fbpyutils_ai import logging


def _reorder_columns(df, ticker):
    """
    Reorders the columns of the given DataFrame to prioritize 'Ticker' and 'Date' columns.

    Parameters
    ----------
    df (pd.DataFrame) : The DataFrame whose columns are to be reordered.
    ticker (str) : The ticker symbol to be added to the DataFrame.
    Returns
    -------
    pd.DataFrame : The DataFrame with reordered columns, 'Ticker' and 'Date' at the beginning, and a reset index.
    """
    df['Ticker'] = ticker
    df['Date'] = df.index
    return df[
        [
            'Ticker', 'Date'] + [col 
            for col in df if col not in ['Ticker', 'Date']
        ]
    ].copy().reset_index(drop = True)


class YahooCurrencyDataProvider():
    """
    Provides cryptocurrency or currency exchange rate data for a specific time frame.

    Parameters
    ----------
    params (dict) : A dictionary containing the parameters required to fetch the data.

        - 'currency_from' (str) : The base currency to fetch the exchange rate for.
        - 'currency_to' (str) : The target currency to fetch the exchange rate for.
        - 'start' (str) : The start date to fetch the data from. It should be in a format that yfinance can understand.
        - 'end' (str) : The end date to fetch the data until. It should be in a format that yfinance can understand.

    Returns
    -------
    pd.DataFrame : The DataFrame with the currency exchange rate data, 'Ticker' and 'Date' columns at the beginning.

    Raises
    ------
    AssertionError : If 'end' is not greater than 'start' or if not all required parameters are provided.
    """

    def _check_params(self, params) -> bool:
        return all(
            [p in params for p in ('currency_from', 'currency_to', 'start', 'end')]
        ) and params['end'] > params['start'] 
        

    def __init__(self, params):
        super().__init__(params)

    def get_data(self) -> pd.DataFrame:
        currency_from = self.params['currency_from']
        currency_to = self.params['currency_to']
        start   = self.params['start']
        end   = self.params['end']

        ticker = currency_from.upper() + currency_to.upper()
        _ticker = ticker + '=X'

        data = yf.download(_ticker, start=start, end=end)
        return _reorder_columns(data, ticker)


class YahooStockDataProvider():
    """
    A class that provides stock data from Yahoo Finance for a specified ticker, including dividend payments if required.
    
    Parameters:
    - params (dict): Dictionary containing the necessary parameters to fetch the data. Mandatory keys are 'ticker' (str), 'market' (str), 'start' (str or datetime.date), and 'end' (str or datetime.date). The 'market' key should contain either 'BR' for Brazilian stocks or 'US' for American stocks. The 'payments' key (bool) indicates whether to fetch dividend payments in addition to the stock data.
       - 'ticker': The stock ticker symbol (e.g., 'AAPL').
       - 'market': The market where the stock is traded ('BR' or 'US').
       - 'start': The start date for the data range (format: YYYY-MM-DD or a pandas datetime.date object).
       - 'end': The end date for the data range (format: YYYY-MM-DD or a pandas datetime.date object).
    
    Returns:
    - pd.DataFrame: A DataFrame containing stock data, including dividend payments if specified in the parameters.
        
    Note:
    - The 'market' parameter is converted to uppercase within the class for consistency and case-insensitive comparison.
    - If 'payments' is True, the method returns a DataFrame with dividend payment data filtered by the specified start and end dates. If no dates are specified, all available dividend payments are returned.
    """

    def _check_params(self, params) -> bool:
        return all(
            [p in params for p in ('ticker', 'market', 'start', 'end')]
        ) and params['end'] > params['start'] and params['market'].upper() in ('BR', 'US')

    def __init__(self, params):
        super().__init__(params)

    def get_data(self) -> pd.DataFrame:
        ticker = self.params['ticker']
        start = self.params['start']
        end   = self.params['end']
        market = self.params['market'].upper()

        ticker = ticker.upper()

        if market == 'BR':
            ticker = ticker + '.SA'

        if self.params.get('payments', False):
            xdata = yf.Ticker(ticker).dividends
            # Apply filters to dividends
            if start is not None and end is not None:
                filtered_dividends = xdata.loc[(xdata.index >= start) & (xdata.index <= end)]
            elif start is not None:
                filtered_dividends = xdata.loc[xdata.index >= start]
            else:
                filtered_dividends = xdata
            # Check if the resulting series has more than one row
            if isinstance(filtered_dividends, pd.Series):
                filtered_dividends = filtered_dividends.to_frame(name='Payment')
            else:
                filtered_dividends = None
            
            data = filtered_dividends
        else:
            data = yf.download(ticker, start=start, end=end)

        return _reorder_columns(data, ticker)
