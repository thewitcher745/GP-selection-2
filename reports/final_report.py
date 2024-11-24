import pandas as pd

from reports.base_report_utils import *

excluded_pairs = ["REEFUSDT"]

positions_df: pd.DataFrame = pd.read_excel("./all_positions.xlsx")
positions_df.sort_values(["Entry time"], inplace=True)

base_report_df = pd.read_excel("./BaseReport.xlsx")
total_pair_list = [pair for pair in base_report_df["Pair name"].tolist() if pair not in excluded_pairs][:31]

# The list containing rows of the final report, which show data on scenarios for choosing the first n pairs of base report as our selected pairs.
final_report_list = []

for pair_count in range(1, len(total_pair_list)):
    current_pair_list = total_pair_list[:pair_count]
    positions_for_current_pairs = positions_df[
        (positions_df["Pair name"].isin(current_pair_list)) & (positions_df["Status"] != "ACTIVE") & (positions_df["Status"] != "ENTERED")]

    # Number of trades
    total_number_of_positions = len(positions_for_current_pairs)

    # The summation of the net profit for the list of trades
    total_net_profit: float = calc_sum_net_profit(positions_for_current_pairs)

    # The gross positive and negative trades
    total_gross_profit: float = positions_for_current_pairs[positions_for_current_pairs["Net profit"] > 0]["Net profit"].sum()
    total_gross_loss: float = positions_for_current_pairs[positions_for_current_pairs["Net profit"] < 0]["Net profit"].sum()

    total_largest_profit_per_position: float = positions_for_current_pairs[positions_for_current_pairs["Net profit"] > 0]["Net profit"].max()
    total_average_profit_per_position: float = total_net_profit / len(positions_for_current_pairs)

    # Performance means what percentage of months have had positive net profits.
    total_performance: float = calc_performance(positions_for_current_pairs)

    # Winrate represents what percentage of positions have had positive net profits.
    total_winrate: float = calc_winrate(positions_for_current_pairs)

    # Drawdown represents the maximum drawdown of the equity curve formed by the positions
    total_drawdown: float = calc_max_drawdown(positions_for_current_pairs)

    # Consecutive wins and losses
    avg_consecutive_wins, max_consecutive_wins = calc_consecutive_wins(positions_for_current_pairs)
    avg_consecutive_losses, max_consecutive_losses = calc_consecutive_losses(positions_for_current_pairs)

    base_report_dict_item: dict = {
        "Pair count": pair_count,
        "Capital used per trade": positions_for_current_pairs.iloc[0]["Capital used"],
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

    final_report_list.append(base_report_dict_item)

final_report_df = pd.DataFrame.from_dict(final_report_list)

# This scaling factor will scale all rows to make them more comparable. For example, if a row has 400 trades, the capital engaged in each trade will
# 1/4 of the top row with 100 trades. This scaling factor will ensure the total capital engaged in each scenario/row is the same. The columns that
# are affected by this scaling factor are the ones that depend on the capital engaged in each trade, namely capital used per trade, net profit, gross profit, gross loss,
# drawdowns and the largest and average profits per trade.
scaling_factor = final_report_df.iloc[0]["Number of positions - total"] / final_report_df["Number of positions - total"]
final_report_df["Capital used per trade"] = final_report_df["Capital used per trade"] * scaling_factor
final_report_df["Net profit - total"] = final_report_df["Net profit - total"] * scaling_factor
final_report_df["Gross profit - total"] = final_report_df["Gross profit - total"] * scaling_factor
final_report_df["Gross loss - total"] = final_report_df["Gross loss - total"] * scaling_factor
final_report_df["Max drawdown - total"] = final_report_df["Max drawdown - total"] * scaling_factor
final_report_df["Largest profit in a trade - total"] = final_report_df["Largest profit in a trade - total"] * scaling_factor
final_report_df["Average profit per trade - total"] = final_report_df["Average profit per trade - total"] * scaling_factor
