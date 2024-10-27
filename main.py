import pandas as pd

import reports.base_report as base_report

base_report_df: pd.DataFrame = base_report.base_report_df

base_report_df.to_excel("BaseReport.xlsx")