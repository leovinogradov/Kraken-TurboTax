# Kraken-TurboTax
Simple python script for creating a TurboTax-compatible CSV from Kraken ledgers

# How to use:
Export ledger entries from Kraken.com
1. Go to History > Export
2. Select "Ledgers" as Export Type and "All fields" for Ledger fields
3. Download as CSV. Note: Kraken seems to only let you download one year at a time, so you may want to download multiple csvs, one per year

Type all input csv files in the list INPUT_CSV_FILES (oldest first, make sure ledger dates / transactions do not overlap)

Type the name of the result file to be generated in RESULT_FILE

Run the script (e.g. python3 turbotax.py on Mac or py turbotax.py on Windows)

# Disclaimer:
This script handles most transaction types (trades, staking, forks, deposits/withdrawals), but not all! For example, Airdrops (which are uncommon) are omitted.
Any skipped/ignored rows will be printed in the output. You should look these over and add them manually if needed.

Additionally, although this script populates the "Fee Amount" and "Fee Asset" columns from the TurboTax csv template, fees for some reason are not displayed in Turbotax UI after upload. I hope this is fixed in the future.

Final disclaimer: this is a simple script, designed for tax cases where you have too many transactions to enter by hand but not enough earnings/losses to warrant paying for a more robust tool.
For a more robust tool, look for something like CoinLedger
