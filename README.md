# Financial Asset Reporting Project

This project generates various reports based on a list of positions formed on different financial assets over a certain time range. Currently, only
the `BaseReport` is implemented, which ranks different assets based on various metrics. Future iterations will include additional reports.

## Features

- **BaseReport**: Ranks financial assets based on multiple metrics such as performance, win rate, net profit, gross profit, gross loss, largest profit
  in a trade, average profit per trade, max drawdown, and consecutive wins/losses.
- **FinalReport**: Provides case study analysis of combining the N top pairs from BaseReport, along with metrics calculated from their combinations
- **MonthlyReport**: Provides month-by-month analysis of the same pair combinations from FinalReport, reporting profits for each N pairs combined per
  month.
- **CombinedReport**: Combines the outputs from Final and Monthly reports into one.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/financial-asset-reporting.git
    cd financial-asset-reporting
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Place your positions data in an Excel file named `all_positions.xlsx` in the root directory.

2. Run the main script to generate all the reports:
    ```sh
    python main.py
    ```

3. The generated reports will output to `BaseReport.xlsx`, `FinalReport.xlsx` and `MonthlyReport.xlsx`.

## Project Structure

- `main.py`: Entry point for generating reports.
- `constants.py`: File containing constants used in the reports, such as capital per trade, excluded pairs, and many more.
- `reports/base_report.py`: Contains the logic for generating the `BaseReport`.
- `reports/base_report_utils.py`: Utility functions used in the `BaseReport`.
- `reports/final_report.py`: Contains the logic for generating the `FinalReport`.
- `reports/monthly_report.py`: Contains the logic for generating the `MonthlyReport`. 
- `all_positions.xlsx`: Input file containing the positions' data.

## Future Work

- ??
