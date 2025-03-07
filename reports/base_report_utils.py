import numpy as np
import pandas as pd
from line_profiler import profile

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
    positions['Exit time'] = positions['Exit time'].dt.tz_localize(None)
    year_month = positions['Exit time'].dt.to_period('M').astype(str).to_numpy()

    positions['YearMonth'] = year_month
    #
    # # Convert 'Net profit' to a NumPy array
    # net_profit = positions['Net profit'].to_numpy()
    #
    # # Calculate the sum of 'Net profit' for each 'YearMonth'
    # unique_year_months, indices = np.unique(year_month, return_inverse=True)
    # monthly_net_profit = np.zeros(len(unique_year_months))
    # np.add.at(monthly_net_profit, indices, net_profit)
    #
    # # Count the number of months with positive and negative net profits
    # positive_months = np.sum(monthly_net_profit > 0)
    # negative_months = np.sum(monthly_net_profit < 0)
    #
    # return positive_months / (positive_months + negative_months) * 100

    # # Group by 'YearMonth'
    grouped = positions.groupby('YearMonth')

    # Calculate the sum of 'Net profit' for each group
    monthly_net_profit = grouped['Net profit'].sum()

    # Count the number of months with positive and negative net profits
    positive_months = (monthly_net_profit > 0).sum()
    negative_months = (monthly_net_profit < 0).sum()

    return positive_months / (positive_months + negative_months) * 100


def calc_winrate(positions: pd.DataFrame) -> float:
    pair_net_profits = positions['Net profit'].to_numpy()
    return len(pair_net_profits[np.where(pair_net_profits > 0)]) / len(positions) * 100


def generate_equity_curve(positions: pd.DataFrame, timeframe: str) -> np.ndarray:
    positions = positions.copy()

    # Convert 'Exit time' to datetime
    exit_times = pd.to_datetime(positions['Exit time']).to_numpy()
    net_profits = positions['Net profit'].to_numpy()

    # Create a time range from the first to the last position, separated by the given time difference
    time_index = pd.date_range(start=positions['Exit time'].min(),
                               end=positions['Exit time'].max(),
                               freq=timeframe)

    time_index = np.array(time_index)

    # Initialize the equity DataFrame
    equity_curve = np.zeros(len(time_index))

    # Iterate through the positions and update the equity value at each exit time
    for position_idx, exit_time in enumerate(exit_times):
        net_profit = net_profits[position_idx]

        # Update the equity value
        equity_curve += np.where(time_index == exit_time, net_profit, 0)

    # Calculate the cumulative sum to get the equity curve
    equity_curve = np.cumsum(equity_curve)

    return equity_curve


def calc_max_drawdown(positions: pd.DataFrame, timeframe: str = "15min") -> float:
    equity_curve = generate_equity_curve(positions, timeframe=timeframe)

    # Calculate the running maximum
    running_max = np.maximum.accumulate(equity_curve)

    # Calculate the drawdown
    drawdown = abs(running_max - equity_curve)

    # Calculate the max drawdown
    max_drawdown = max(drawdown)

    return max_drawdown


def calc_consecutive_wins(positions: pd.DataFrame) -> (float, int):
    # Filter only the profitable positions
    positive_positions = positions['Net profit'].to_numpy() > 0

    # Find the indices where the value changes
    changes = np.diff(positive_positions.astype(int))

    # Identify the start and end of each streak of True values
    streak_starts = np.where(changes == 1)[0] + 1
    streak_ends = np.where(changes == -1)[0] + 1

    # Handle the case where the array starts or ends with a streak of True values
    if positive_positions[0]:
        streak_starts = np.insert(streak_starts, 0, 0)
    if positive_positions[-1]:
        streak_ends = np.append(streak_ends, len(positive_positions))

    # Calculate the lengths of the streaks
    streak_lengths = streak_ends - streak_starts

    # Calculate the average and maximum streak lengths
    avg_streak = np.mean(streak_lengths) if len(streak_lengths) > 0 else 0
    max_streak = np.max(streak_lengths) if len(streak_lengths) > 0 else 0

    return avg_streak, max_streak


def calc_consecutive_losses(positions: pd.DataFrame) -> (float, int):
    # Filter only the negative positions
    negative_positions = positions['Net profit'].to_numpy() < 0

    if len(negative_positions) == 0:
        return 0, 0

    # Find the indices where the value changes
    changes = np.diff(negative_positions.astype(int))

    # Identify the start and end of each streak of True values
    streak_starts = np.where(changes == 1)[0] + 1
    streak_ends = np.where(changes == -1)[0] + 1

    # Handle the case where the array starts or ends with a streak of True values
    if negative_positions[0]:
        streak_starts = np.insert(streak_starts, 0, 0)
    if negative_positions[-1]:
        streak_ends = np.append(streak_ends, len(negative_positions))

    # Calculate the lengths of the streaks
    streak_lengths = streak_ends - streak_starts

    # Calculate the average and maximum streak lengths
    avg_streak = np.mean(streak_lengths) if len(streak_lengths) > 0 else 0
    max_streak = np.max(streak_lengths) if len(streak_lengths) > 0 else 0

    return avg_streak, max_streak


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


def calc_total_months(positions):
    min_date = positions["Entry time"].min().replace(day=1, hour=0, minute=0, second=0)
    max_date = positions["Exit time"].max().replace(day=1, hour=0, minute=0, second=0)

    total_month_list = pd.date_range(start=min_date, end=max_date, freq="MS")
    return total_month_list


def calc_missing_months(positions, month_list: pd.DatetimeIndex):
    """
        Calculate the number of months with no positions based on the "Exit time" column.

        This function determines the number of months within the range of the dataset (from the earliest "Entry time" to the latest "Exit time")
        that do not have any positions with an "Exit time" falling within that month.

        Args:
            positions (pd.DataFrame): A DataFrame containing position data with "Entry time" and "Exit time" columns.
            month_list (pd.DatetimeIndex): A list of Datetimes for the list of months that positions spanned across.

        Returns:
            int: The number of months with no positions.
    """

    missing_months = 0

    for month in month_list:
        month_end = month + pd.offsets.MonthEnd(1)
        if not ((positions["Exit time"] >= month) & (positions["Exit time"] <= month_end)).any():
            missing_months += 1

    return missing_months


def adjust_score_for_missing_months(base_report_df) -> pd.DataFrame:
    """
    Adjust the score of each pair based on the number of missing months.

    This function multiplies the score of each pair by 0.8 for each month that it has no positions.

    Args:
        base_report_df (pd.DataFrame): The base report DataFrame containing the "Missing months" and "Score" columns.

    Returns:
        pd.DataFrame: The DataFrame with adjusted scores.
    """
    missing_months_column = base_report_df["Missing months"]

    base_report_df["Score"] *= 0.75 ** missing_months_column

    return base_report_df
