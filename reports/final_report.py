import pandas as pd
from line_profiler import profile

import constants
from reports.base_report_utils import *

positions_df: pd.DataFrame = pd.read_excel("./all_positions.xlsx")
positions_df.sort_values(["Entry time"], inplace=True)

base_report_df = pd.read_excel("report_outputs/BaseReport.xlsx")

all_pairs = [pair for pair in base_report_df["Pair name"].tolist() if pair not in constants.excluded_pairs]
if len(all_pairs) > constants.max_final_report_pairs:
    total_pair_list = all_pairs[:constants.max_final_report_pairs + 1]
else:
    total_pair_list = all_pairs

# The list containing rows of the final report, which show data on scenarios for choosing the first n pairs of base report as our selected pairs.
final_report_list = []

total_month_list = calc_total_months(positions_df)


def calculate_average_concurrent_positions(df):
    entry_times = df['Entry time'].to_numpy()
    exit_times = df['Exit time'].to_numpy()

    min_time = min(min(entry_times), min(exit_times))
    max_time = max(max(entry_times), max(exit_times))
    all_times = pd.date_range(start=min_time, end=max_time, freq='5min').to_numpy()

    concurrent_positions = []

    for time in all_times:
        # Count positions that are active at the current time
        active_positions = df[(entry_times <= time) & (exit_times > time)]
        concurrent_positions.append(len(active_positions))

    # Calculate the average number of concurrent positions
    average_concurrent_positions = sum(concurrent_positions) / len(concurrent_positions)
    return average_concurrent_positions


def calculate_average_loss_per_position(df):
    return df[df["Net profit"] < 0]["Net profit"].mean()


for pair_count in range(1, len(total_pair_list) + 1):
    print(f"FinalReport.xlsx: Pair count {pair_count}")
    current_pair_list = total_pair_list[:pair_count]
    positions_for_current_pairs = positions_df[
        (positions_df["Pair name"].isin(current_pair_list)) & (positions_df["Status"] != "ACTIVE") & (positions_df["Status"] != "ENTERED")]

    # Number of trades
    total_number_of_positions = len(positions_for_current_pairs)
    # If the file has no positions, skip to the next pair
    if total_number_of_positions == 0:
        continue

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

    # Missing months that the combination of pairs had no positions in
    missing_months = calc_missing_months(positions_for_current_pairs, total_month_list)

    # Average concurrent open positions
    average_concurrent_positions = calculate_average_concurrent_positions(positions_for_current_pairs)

    # Average loss per position
    average_loss_per_position = calculate_average_loss_per_position(positions_for_current_pairs)

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
        "Average loss per position - total": average_loss_per_position,
        "Total months": len(total_month_list),
        "Missing months": missing_months,
        "Average # of concurrent trades": average_concurrent_positions,
        "Average consecutive wins": avg_consecutive_wins,
        "Max consecutive wins": max_consecutive_wins,
        "Average consecutive losses": avg_consecutive_losses,
        "Max consecutive losses": max_consecutive_losses
    }

    final_report_list.append(base_report_dict_item)

final_report_df = pd.DataFrame.from_dict(final_report_list)

# This scaling factor works by forcing a set amount of engaged capital for every signal of the LAST row of the final report. Then, a scaling factor
# is calculated for all the other rows and all the affected numbers are multiplied by that.

# scaling_factor = constants.capital_per_trade / final_report_df["Capital used per trade"] * final_report_df.iloc[-1]["Number of positions - total"] / \
#                  final_report_df["Number of positions - total"]

# A pd.Series which represents the original, unscaled column in the FinalReport which contains the engaged capital from the backtests.
original_capital_per_trade = final_report_df["Capital used per trade"]

# Fixed product which basically represents the total capital, calculated from the desired capital per trade (given in constants.py) and the number of
# positions in the last row of FinalReport.
total_capital = final_report_df["Number of positions - total"].iloc[-1] * constants.capital_per_trade

# The product of every row's total # of positions and its engaged capital should equal the total capital. So the Capital used per trade for each row
# is corrected as follows:
final_report_df["Capital used per trade"] = total_capital / final_report_df["Number of positions - total"]

# The scaling factor for the other rows would be the ratio of the newly calculated capital to the original unscaled one.
scaling_factor = final_report_df["Capital used per trade"] / original_capital_per_trade

final_report_df["Net profit - total"] = final_report_df["Net profit - total"] * scaling_factor
final_report_df["Gross profit - total"] = final_report_df["Gross profit - total"] * scaling_factor
final_report_df["Gross loss - total"] = final_report_df["Gross loss - total"] * scaling_factor
final_report_df["Max drawdown - total"] = final_report_df["Max drawdown - total"] * scaling_factor
final_report_df["Largest profit in a trade - total"] = final_report_df["Largest profit in a trade - total"] * scaling_factor
final_report_df["Average profit per trade - total"] = final_report_df["Average profit per trade - total"] * scaling_factor
