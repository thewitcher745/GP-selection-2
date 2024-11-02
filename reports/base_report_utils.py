import pandas as pd

# Define the weights for each column
weights = {
    "Performance - total": 0.3,
    "Winrate - total": 0.2,
    "Net profit - total": 0.4,
    "Gross profit - total": 0.1,
    "Gross loss - total": 0.1,  # Values are negative, so a positive weight would minimize its absolute
    "Largest profit in a trade - total": 0.05,
    "Average profit per trade - total": 0.05,
    "Max drawdown - total": -0.1,  # Negative weight to minimize
    "Average consecutive wins": 0.05,
    "Max consecutive wins": 0.05,
    "Average consecutive losses": -0.025,  # Negative weight to minimize
    "Max consecutive losses": -0.025  # Negative weight to minimize
}


def calc_sum_net_profit(positions: pd.DataFrame) -> float:
    return float(positions["Net profit"].sum())


def calc_performance(positions: pd.DataFrame) -> float:
    positions = positions.copy()

    # Extract month and year from 'Exit time'
    positions['YearMonth'] = positions['Exit time'].dt.to_period('M')

    # Group by 'YearMonth'
    grouped = positions.groupby('YearMonth')

    # Calculate the sum of 'Net profit' for each group
    monthly_net_profit = grouped['Net profit'].sum()

    # Count the number of months with positive and negative net profits
    positive_months = (monthly_net_profit > 0).sum()
    negative_months = (monthly_net_profit < 0).sum()

    return positive_months / (positive_months + negative_months) * 100


def calc_winrate(positions: pd.DataFrame) -> float:
    return len(positions[positions["Net profit"] > 0]) / len(positions) * 100


def generate_equity_curve(positions: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    positions = positions.copy()

    # Convert 'Exit time' to datetime
    positions['Exit time'] = pd.to_datetime(positions['Exit time'])

    # Create a time range from the first to the last position, separated by the given time difference
    time_index = pd.date_range(start=positions['Exit time'].min(),
                               end=positions['Exit time'].max(),
                               freq=timeframe)

    # Initialize the equity DataFrame
    equity_curve = pd.DataFrame(index=time_index, columns=['value'], dtype='float64')
    equity_curve['value'] = 0.0

    # Iterate through the positions and update the equity value at each exit time
    for _, row in positions.iterrows():
        exit_time = row['Exit time']
        net_profit = float(row['Net profit'])

        # Another safety net for incorrect positions
        if net_profit is None:
            continue

        # Update the equity value
        try:
            equity_curve.loc[exit_time, 'value'] += net_profit

        # Catching any errors due to wrong positions being passed
        except KeyError:
            continue

    # Calculate the cumulative sum to get the equity curve
    equity_curve['value'] = equity_curve['value'].cumsum()

    return equity_curve


def calc_max_drawdown(positions: pd.DataFrame, timeframe: str = "15min") -> float:
    equity_curve = generate_equity_curve(positions, timeframe=timeframe)

    # Calculate the running maximum
    equity_curve['running_max'] = equity_curve['value'].cummax()

    # Calculate the drawdown
    equity_curve['drawdown'] = abs(equity_curve['running_max'] - equity_curve['value'])

    # Calculate the max drawdown
    max_drawdown = equity_curve['drawdown'].max()

    return max_drawdown


def calc_consecutive_wins(positions: pd.DataFrame) -> (float, int):
    # Filter only the profitable positions
    positive_positions = positions['Net profit'] > 0

    # Calculate the lengths of consecutive profitable positions
    consecutive_wins = (positive_positions != positive_positions.shift()).cumsum()
    streak_lengths = positive_positions.groupby(consecutive_wins).cumsum()

    # Calculate the average and maximum streak lengths
    avg_consecutive_wins = streak_lengths[positive_positions].mean()
    max_consecutive_wins = streak_lengths[positive_positions].max()

    return avg_consecutive_wins, max_consecutive_wins


def calc_consecutive_losses(positions: pd.DataFrame) -> (float, int):
    # Filter only the profitable positions
    negative_positions = positions['Net profit'] < 0

    # Calculate the lengths of consecutive profitable positions
    consecutive_losses = (negative_positions != negative_positions.shift()).cumsum()
    streak_lengths = negative_positions.groupby(consecutive_losses).cumsum()

    # Calculate the average and maximum streak lengths
    avg_consecutive_losses = streak_lengths[negative_positions].mean()
    max_consecutive_losses = streak_lengths[negative_positions].max()

    return avg_consecutive_losses, max_consecutive_losses


def calculate_score(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    This function takes in a base_report dataframe without its Score column, and returns a dataframe with the Score column attached. The score is
    calculated based on the weights provided in the weights dict. The higher the absolute value of a weight, the more impact it will have. The
    negative weights represent a column we want to minimize. The columns of the raw base_Report_df are also normalized to make the weights more
    meaningful, since comparing raw numbers for totally different metrics with very different scales is not very useful.

    Args:
        df (pd.Dataframe): The "raw" base_report_df without the Score column
        weights (dict): A dict containing the weights for calculating the score from each column

    Returns:
        pd.DataFrame: A dataframe with the Score column added

    """

    # This function normalizes a column in a dataframe based on its min and max values.
    def normalize_column(df: pd.DataFrame, column: str) -> pd.Series:
        min_val = df[column].min()
        max_val = df[column].max()
        return (df[column] - min_val) / (max_val - min_val)

    df = df.copy()

    # Normalize each column and apply weights
    for column, weight in weights.items():
        df[f"{column} - normalized"] = normalize_column(df, column) * weight

    # Calculate the final score
    df["Score"] = df[[f"{column} - normalized" for column in weights.keys()]].sum(axis=1)

    return df
