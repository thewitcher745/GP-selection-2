import argparse
import os

from dotenv import dotenv_values

# Set up argument parser
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--pl', type=str, help='File name of the positions to process')
parser.add_argument('--position_type', type=str, help='Filter boxes by type (Short/long)')

# Parse arguments
args = parser.parse_args()

params = dotenv_values(".env.params")

excluded_pairs = [""]

max_final_report_pairs = 30
capital_per_trade = 100

# Set the positions file name from the argument
positions_file_name = f'./{args.pl}' if args.pl else "./all_positions.xlsx"
position_type = args.position_type if args.position_type else None

output_dir = f'report_outputs/{args.pl.replace('xlsx', '')}' if args.pl else "report_outputs/latest"
os.mkdir(output_dir)