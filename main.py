import pandas as pd
import os

# Create the report_outputs folder if it doesn't exist
if not os.path.exists('report_outputs'):
    print("Report output folder created.")
    os.makedirs('report_outputs')

print("Creating BaseReport.xlsx")
import reports.base_report as base_report

base_report_df: pd.DataFrame = base_report.base_report_df
base_report_df.to_excel("report_outputs/BaseReport.xlsx")

print("BaseReport.xlsx created.")

print("Creating FinalReport.xlsx")
import reports.final_report as final_report

final_report_df: pd.DataFrame = final_report.final_report_df
final_report_df.to_excel("report_outputs/FinalReport.xlsx")

print("FinalReport.xlsx created.")

print("Creating MonthlyReport.xlsx")
import reports.monthly_report as monthly_report

monthly_report_df: pd.DataFrame = monthly_report.monthly_report_df
monthly_report_df.to_excel("report_outputs/MonthlyReport.xlsx")

print("MonthlyReport.xlsx created.")

# Combine the dataframes horizontally
combined_report_df = pd.concat([final_report_df, monthly_report_df], axis=1)

# Save the combined dataframe to a new Excel file
combined_report_df.to_excel("report_outputs/CombinedReport.xlsx", index=False)

print("CombinedReport.xlsx created.")
