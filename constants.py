from dotenv import dotenv_values

params = dotenv_values(".env.params")

excluded_pairs = ["REEFUSDT"]

max_final_report_pairs = 30
capital_per_trade = 100
