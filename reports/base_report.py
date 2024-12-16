import pandas as pd

from reports.base_report_utils import *

mode = "LIMITED_PAIRS"

positions_df: pd.DataFrame = pd.read_excel("./all_positions.xlsx")
positions_df.sort_values(["Entry time"], inplace=True)

pair_list = []
if mode == "LIMITED_PAIRS":
    pair_list = pd.read_csv("pair_list.csv").pairs.tolist()
elif mode == "ALL_PAIRS":
    pair_list = positions_df["Pair name"].unique().tolist()

# The list which contains items that have data related to each pair. Each item is a dict and the list finally converts into a python dataframe.
base_report_list: list = []

for pair_name in pair_list:
    # The positions that have pair_name as their first column, and have been actually entered
    positions_from_pair: pd.DataFrame = positions_df[
        (positions_df["Pair name"] == pair_name) & (positions_df["Status"] != "ACTIVE") & (positions_df["Status"] != "ENTERED")]

    # Number of trades
    total_number_of_positions = len(positions_from_pair)
    # If the file has no positions, skip to the next pair
    if total_number_of_positions == 0:
        continue

    # The summation of the net profit for the list of trades
    total_net_profit: float = calc_sum_net_profit(positions_from_pair)

    # The gross positive and negative trades
    total_gross_profit: float = positions_from_pair[positions_from_pair["Net profit"] > 0]["Net profit"].sum()
    total_gross_loss: float = positions_from_pair[positions_from_pair["Net profit"] < 0]["Net profit"].sum()

    total_largest_profit_per_position: float = positions_from_pair[positions_from_pair["Net profit"] > 0]["Net profit"].max()
    total_average_profit_per_position: float = total_net_profit / len(positions_from_pair)

    # Performance means what percentage of months have had positive net profits.
    total_performance: float = calc_performance(positions_from_pair)

    # Winrate represents what percentage of positions have had positive net profits.
    total_winrate: float = calc_winrate(positions_from_pair)

    # Drawdown represents the maximum drawdown of the equity curve formed by the positions
    total_drawdown: float = calc_max_drawdown(positions_from_pair)

    # Consecutive wins and losses
    avg_consecutive_wins, max_consecutive_wins = calc_consecutive_wins(positions_from_pair)
    avg_consecutive_losses, max_consecutive_losses = calc_consecutive_losses(positions_from_pair)

    base_report_dict_item: dict = {
        "Pair name": pair_name,
        "Number of positions - total": total_number_of_positions,
        "Performance - total": total_performance,
        "Winrate - total": total_winrate,
        "Net profit - total": total_net_profit,
        "Gross profit - total": total_gross_profit,
        "Gross loss - total": total_gross_loss,
        "Largest profit in a trade - total": total_largest_profit_per_position,
        "Average profit per trade - total": total_average_profit_per_position,
        "Max drawdown - total": total_drawdown,
        "Average consecutive wins": avg_consecutive_wins,
        "Max consecutive wins": max_consecutive_wins,
        "Average consecutive losses": avg_consecutive_losses,
        "Max consecutive losses": max_consecutive_losses
    }

    base_report_list.append(base_report_dict_item)

base_report_df = pd.DataFrame.from_dict(base_report_list)

# Add the score column to the base_report dataframe
base_report_df["Score"] = calculate_score(base_report_df, weights)["Score"]

# Sort the columns by Score
base_report_df.sort_values(["Score"], ascending=False, inplace=True)

# Round the values to 2 decimal places
base_report_df = base_report_df.round(4)
