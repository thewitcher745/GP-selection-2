# Financial Asset Reporting (Good Pair Selection)

This is the updated version of the initial GP-Selection.
This project generates various reports based on a list of positions formed on different financial assets over a certain time range. The reports
contain information on the various performance metrics of said coins, and how they performed when the N top pairs are combined.

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
    git clone https://github.com/thewitcher745/GP-selection-2.git
    cd GP-selection-2
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Place your positions data in an Excel file named `all_positions.xlsx` in the root directory. The filename can also be set using --pl runtime arg.

2. Run the main script to generate all the reports:
    ```sh
    python main.py
    ```

3. The generated reports will output to `BaseReport.xlsx`, `FinalReport.xlsx` and `MonthlyReport.xlsx`.

## Project Structure

- `main.py`: Entry point for generating reports.
- `constants.py`: File containing constants used in the reports, such as capital per trade, excluded pairs, and many more.
- `reports/base_report_utils.py`: Utility functions.
- `reports/gp_report.py`: Contains the logic for generating all reports.
- `all_positions.xlsx`: Input file containing the positions' data.

