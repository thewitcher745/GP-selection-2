import pandas as pd

import reports.base_report as base_report

base_report_df: pd.DataFrame = base_report.base_report_df
base_report_df.to_excel("BaseReport.xlsx")

print("BaseReport.xlsx created.")

import reports.final_report as final_report

final_report_df: pd.DataFrame = final_report.final_report_df
final_report_df.to_excel("FinalReport.xlsx")

print("FinalReport.xlsx created.")

import reports.monthly_report as monthly_report

monthly_report_df: pd.DataFrame = monthly_report.monthly_report_df
monthly_report_df.to_excel("MonthlyReport.xlsx")

print("MonthlyReport.xlsx created.")

# Combine the dataframes horizontally
combined_report_df = pd.concat([final_report_df, monthly_report_df], axis=1)

# Save the combined dataframe to a new Excel file
combined_report_df.to_excel("CombinedReport.xlsx", index=False)

print("CombinedReport.xlsx created.")


