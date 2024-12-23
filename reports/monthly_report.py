# This report will contain profit numbers per month for the strategy. It has the same rows as the final report, aka the combinations of the top pairs
# of the base report, but the columns are different. The columns are the months, and the rows are the pairs. The values are the net profits for each
# month and pair combination. The report will be used to analyze the performance of the strategy over time.

import pandas as pd

from reports.base_report_utils import calc_sum_net_profit

excluded_pairs = ["REEFUSDT"]

positions_df: pd.DataFrame = pd.read_excel("./all_positions.xlsx")
positions_df.sort_values(["Entry time"], inplace=True)

base_report_df = pd.read_excel("./BaseReport.xlsx")

all_pairs = [pair for pair in base_report_df["Pair name"].tolist() if pair not in excluded_pairs]
if len(all_pairs) > 30:
    total_pair_list = all_pairs[:31]
else:
    total_pair_list = all_pairs

earliest_yearmonth = positions_df["Entry time"].min().strftime("%Y-%m")
latest_yearmonth = positions_df["Entry time"].max().strftime("%Y-%m")


monthly_report_list = []
for pair_count in range(1, len(total_pair_list) + 1):
    current_pair_list = total_pair_list[:pair_count]
    positions_for_current_pairs = positions_df[
        (positions_df["Pair name"].isin(current_pair_list)) & (positions_df["Status"] != "ACTIVE") & (positions_df["Status"] != "ENTERED")]

    # This is temporary - modifying the money engaged in each trade to be the same for all scenarios
    capital_per_trade = 150
    scaling_factor = capital_per_trade / float(positions_for_current_pairs["Capital used"].iloc[0])

    # Iterate over every month between earliest and latest, calculating the profit for it
    monthly_profit_dict = {
        "Pair count": pair_count
    }

    current_month = earliest_yearmonth
    while current_month <= latest_yearmonth:
        positions_for_current_month = positions_for_current_pairs[
            (positions_for_current_pairs["Entry time"].dt.strftime("%Y-%m") == current_month)]
        total_net_profit: float = calc_sum_net_profit(positions_for_current_month)

        monthly_profit_dict[current_month] = total_net_profit * scaling_factor
        current_month = (pd.to_datetime(current_month) + pd.DateOffset(months=1)).strftime("%Y-%m")

    monthly_report_list.append(monthly_profit_dict)

monthly_report_df = pd.DataFrame(monthly_report_list)