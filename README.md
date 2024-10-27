# Financial Asset Reporting Project

This project generates various reports based on a list of positions formed on different financial assets over a certain time range. Currently, only the `BaseReport` is implemented, which ranks different assets based on various metrics. Future iterations will include additional reports.

## Features

- **BaseReport**: Ranks financial assets based on multiple metrics such as performance, win rate, net profit, gross profit, gross loss, largest profit in a trade, average profit per trade, max drawdown, and consecutive wins/losses.

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

1. Place your positions data in an Excel file named `positions.xlsx` in the root directory.

2. Run the main script to generate the `BaseReport`:
    ```sh
    python main.py
    ```

3. The generated report will output to the `BaseReport.xlsx` file.

## Project Structure

- `main.py`: Entry point for generating reports.
- `reports/base_report.py`: Contains the logic for generating the `BaseReport`.
- `reports/base_report_utils.py`: Utility functions used in the `BaseReport`.
- `positions.xlsx`: Input file containing the positions' data.

## Future Work

- Implement additional reports to provide more insights into financial assets.
- Enhance the scoring mechanism to include more metrics and customizable weights.
