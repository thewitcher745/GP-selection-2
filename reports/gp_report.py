import pandas as pd

import constants
from reports.base_report_utils import *


class Report:
    def __init__(self, all_positions_file='./all_positions.xlsx', mode='ALL_PAIRS'):
        print('Reading from', all_positions_file)
        self.positions_df: pd.DataFrame = pd.read_excel(all_positions_file)

        if constants.position_type:
            self.positions_df = self.positions_df[self.positions_df['Type'] == constants.position_type.lower()].reset_index()

        self.positions_df.sort_values(["Entry time"], inplace=True)

        # Filters
        # Pair name filter
        self.pair_names = self.positions_df['Pair name'].to_numpy()
        self.net_profits = self.positions_df['Net profit'].to_numpy()
        self.statuses = self.positions_df['Status'].to_numpy()

        if mode == "LIMITED_PAIRS":
            self.pair_list = pd.read_csv("pair_list.csv").pairs.tolist()
        elif mode == "ALL_PAIRS":
            self.pair_list = self.positions_df["Pair name"].unique().tolist()

        self.base_report_df: pd.DataFrame = self.create_base_report()
        self.final_report_df: pd.DataFrame = self.create_final_report()
        self.monthly_report_df: pd.DataFrame = self.create_monthly_report()
        self.combined_report_df: pd.DataFrame = self.create_combined_report()

        self.base_report_df.to_excel(f"{constants.output_dir}/BaseReport.xlsx")
        self.final_report_df.to_excel(f"{constants.output_dir}/FinalReport.xlsx")
        self.monthly_report_df.to_excel(f"{constants.output_dir}/MonthlyReport.xlsx")
        self.combined_report_df.to_excel(f"{constants.output_dir}/CombinedReport.xlsx", index=False)

    def create_base_report(self) -> pd.DataFrame:
        # The list which contains items that have data related to each pair. Each item is a dict and the list finally converts into a python dataframe.
        base_report_list: list[dict] = []

        total_month_list = calc_total_months(self.positions_df)

        for pair_name in self.pair_list:
            # The positions that have pair_name as their first column, and have been actually entered
            positions_from_pair: pd.DataFrame = self.positions_df[
                (self.pair_names == pair_name) &
                (self.statuses != "ACTIVE") &
                (self.statuses != "ENTERED")
                ]

            pair_net_profits = positions_from_pair["Net profit"].to_numpy()

            # Number of trades
            total_number_of_positions = len(positions_from_pair)
            # If the file has no positions, skip to the next pair
            if total_number_of_positions == 0:
                continue

            # The summation of the net profit for the list of trades
            total_net_profit: float = sum(pair_net_profits)

            # The gross positive and negative trades
            total_gross_profit: float = sum(pair_net_profits[np.where(pair_net_profits > 0)])
            total_gross_loss: float = sum(pair_net_profits[np.where(pair_net_profits < 0)])

            try:
                total_largest_profit_per_position: float = pair_net_profits[np.where(pair_net_profits > 0)].max()
            except:
                total_largest_profit_per_position = 0

            total_average_profit_per_position: float = total_net_profit / len(positions_from_pair)

            # Missing months
            missing_months = calc_missing_months(positions_from_pair, total_month_list)

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
                "Total months": len(total_month_list),
                "Missing months": missing_months,
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

        # Adjust the scores for missing months
        base_report_df = adjust_score_for_missing_months(base_report_df)

        # Sort the columns by Score
        base_report_df.sort_values(["Score"], ascending=False, inplace=True)

        # Round the values to 2 decimal places
        base_report_df = base_report_df.round(4)

        print('Base report created.')

        return base_report_df

    @profile
    def create_final_report(self):
        # The list containing rows of the final report, which show data on scenarios for choosing the first n pairs of base report as our selected pairs.
        final_report_list = []

        total_month_list = calc_total_months(self.positions_df)

        def calculate_average_concurrent_positions(df):
            entry_times = df['Entry time'].to_numpy()
            exit_times = df['Exit time'].to_numpy()

            min_time = min(min(entry_times), min(exit_times))
            max_time = max(max(entry_times), max(exit_times))
            all_times = pd.date_range(start=min_time, end=max_time, freq='5min').to_numpy()

            concurrent_positions = np.zeros(len(all_times))

            for i, time in enumerate(all_times):
                # Count positions that are active at the current time
                concurrent_positions[i] = np.sum((entry_times <= time) & (exit_times > time))

            # Calculate the average number of concurrent positions
            average_concurrent_positions = np.mean(concurrent_positions)
            return average_concurrent_positions

        def calculate_average_loss_per_position(df):
            return df[df["Net profit"] < 0]["Net profit"].mean()

        if len(self.pair_list) > constants.max_final_report_pairs:
            sorted_pair_list = self.base_report_df["Pair name"][:constants.max_final_report_pairs].tolist()
        else:
            sorted_pair_list = self.base_report_df["Pair name"].tolist()

        for pair_count in range(1, len(sorted_pair_list) + 1):
            print(f"FinalReport.xlsx: Pair count {pair_count}")
            current_pair_list = sorted_pair_list[:pair_count]
            positions_for_current_pairs = self.positions_df[
                (np.isin(self.pair_names, current_pair_list)) & (self.statuses != "ACTIVE") & (self.statuses != "ENTERED")]

            # Number of trades
            total_number_of_positions = len(positions_for_current_pairs)
            # If the file has no positions, skip to the next pair
            if total_number_of_positions == 0:
                continue

            pair_net_profits = positions_for_current_pairs["Net profit"].to_numpy()

            # The summation of the net profit for the list of trades
            total_net_profit: float = calc_sum_net_profit(positions_for_current_pairs)

            # The gross positive and negative trades
            total_gross_profit: float = positions_for_current_pairs[positions_for_current_pairs["Net profit"] > 0]["Net profit"].sum()
            total_gross_loss: float = positions_for_current_pairs[positions_for_current_pairs["Net profit"] < 0]["Net profit"].sum()

            try:
                total_largest_profit_per_position: float = pair_net_profits[np.where(pair_net_profits > 0)].max()
            except:
                total_largest_profit_per_position = 0

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

        print('Final report created.')

        return final_report_df

    def create_monthly_report(self):
        if len(self.pair_list) > constants.max_final_report_pairs:
            sorted_pair_list = self.base_report_df["Pair name"][:constants.max_final_report_pairs].tolist()
        else:
            sorted_pair_list = self.base_report_df["Pair name"].tolist()

        earliest_yearmonth = self.positions_df["Entry time"].min().strftime("%Y-%m")
        latest_yearmonth = self.positions_df["Exit time"].max().strftime("%Y-%m")

        monthly_report_list = []

        # Same scaling calculations from FinalReport
        total_capital = self.final_report_df["Number of positions - total"].iloc[-1] * constants.capital_per_trade
        original_capital_per_trade = self.positions_df["Capital used"].iloc[0]

        for pair_count in range(1, len(sorted_pair_list) + 1):
            print(f"MonthlyReport.xlsx: Pair count {pair_count}")
            current_pair_list = sorted_pair_list[:pair_count]
            positions_for_current_pairs = self.positions_df[
                (np.isin(self.pair_names, current_pair_list)) & (self.statuses != "ACTIVE") & (self.statuses != "ENTERED")]

            scaling_factor = self.final_report_df[self.final_report_df["Pair count"] == pair_count]["Capital used per trade"].iloc[
                                 0] / original_capital_per_trade

            # Iterate over every month between earliest and latest, calculating the profit for it
            monthly_profit_dict = {
                "Pair count": pair_count
            }

            current_month = earliest_yearmonth
            while current_month <= latest_yearmonth:
                positions_for_current_month = positions_for_current_pairs[
                    (positions_for_current_pairs["Exit time"].dt.strftime("%Y-%m") == current_month)]
                total_net_profit: float = calc_sum_net_profit(positions_for_current_month)

                monthly_profit_dict[current_month] = total_net_profit * scaling_factor
                current_month = (pd.to_datetime(current_month) + pd.DateOffset(months=1)).strftime("%Y-%m")

            monthly_report_list.append(monthly_profit_dict)

        print('Monthly report created.')

        return pd.DataFrame(monthly_report_list)

    def create_combined_report(self):
        return pd.concat([self.final_report_df, self.monthly_report_df.drop(columns=["Pair count"])], axis=1)
