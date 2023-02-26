import csv


""" 
INSTRUCTIONS FROM https://ttlc.intuit.com/turbotax-support/en-us/help-article/cryptocurrency/create-csv-file-unsupported-source/L1yhp71Nt_US_en_US
NOTE: These instructions are obtained from TurboTax but they don't seem to be fully accurate.
      For instance, 'Convert' doesn't seem to be supported even though its in the list below. 

INSTRUCTIONS:
The column headers in your CSV file must match one of the accepted names, though it’s not case sensitive. We also recommend keeping them on the first row
Use one of the TurboTax-supported transaction types. If you're not sure what type the transaction is, use Other
Make sure every transaction has a value for the Date and Transaction Type. These are the only mandatory values for each transaction
If you don’t  know the market value of the digital asset for a transaction, leave it blank. TurboTax will automatically look up a price for your transaction
Negative numbers will cause the upload to fail
Limit your numbers to 8 decimal places  (for example 0.12345678)

HEADERS ARE:
Date,Type,Sent Asset,Sent Amount,Received Asset,Received Amount,Fee Asset,Fee Amount,Market Value Currency,Market Value,Description,Transaction Hash,Transaction ID

ALLOWED TYPES:
Buy: purchasing a digital asset like crypto or an NFT, with cash
Sale: selling your digital asset at a gain or loss
    Example: Tyler makes a profit by exchanging a crypto coin for cash. If Tyler used a crypto coin to obtain an NFT, it's considered a sale
Convert: using one type of crypto to buy another type of crypto
Transfer: moving your crypto or asset from one wallet or exchange to another. This isn't taxable
Income: receiving cryptocurrency from participating in various types of activities. This could include rewards from taking cryptocurrency courses or promotional airdrops. This would also include receiving payments in cryptocurrency from selling goods and services.
    Interest earned through these accounts: 
    Crypto interest
    Crypto lending  
    Crypto savings  
    Crypto liquidity pools
Expense: any transaction or fees you were charged while using an exchange’s services
Deposit: moving crypto into a wallet or account. The wallet can be either custodial or noncustodial, and is either a wallet you own or a wallet held by the exchange
Withdrawal: removing fiat (government-issued money) or crypto from a wallet or account. Withdrawals can also include sending crypto or fiat money to another person as payment or moving cryptocurrency to cold storage (offline cryptocurrency storage)
Mining: creating coins by validating transactions to be added to a blockchain network through proof-of-work protocols. The most common blockchain that uses proof of work is Bitcoin
Airdrop: using this distribution method where assets are delivered to wallets. They're often used as a marketing method (for example, to promote a token), but can also occur after a fork or token upgrade
Forking: changing a blockchain’s rules, where the new rules apply to tokens. Rule changes can result in monetary gains
Staking: earning rewards by committing your crypto holdings to validate and verify blockchain transactions through Proof of Stake protocols. The most common blockchains for staking are:
    Polkadot
    Cardano 
    Ethereum 2.0
Other: any other activity that can't be automatically categorized under the preceding transaction types
"""

DESIRED_HEADERS = [
    'Date','Type','Sent Asset','Sent Amount','Received Asset','Received Amount','Fee Asset','Fee Amount','Market Value Currency','Market Value','Description','Transaction Hash','Transaction ID'
]


# Put in all input kraken ledger files, oldest first. Make sure their dates do not overlap
INPUT_CSV_FILES = ['<your_input_file>.csv', '<your_input_file_2>.csv']

# Output formatted for TurboTax will be written to this file:
RESULT_FILE = '<result_file_name>.csv'


# Deposits and withdrawals to your own wallet are not taxable, they can be ignored as long as your buys are >= sales
# deposits + buys must be >= withdrawals + sales
IGNORE_DEPOSIT_WITHDRAW = False


def _convert_asset_name(asset):
    # Rename Kraken asset names to their commonly used names
    if asset == 'ZUSD':
        return 'USD'
    if asset == 'XETH':
        return 'ETH'
    if asset == 'XXBT':
        return 'BTC'
    if asset == 'XXDG':
        # treating Doge like an ISO recognized currency, very funny Kraken
        return 'DOGE' 
    return asset

def _convert_staking_asset_name(asset):
    if asset.endswith(".S"):
        # DOT.S => DOT
        return asset[:-2]
    if asset == "ETH2":
        return "ETH"
    return asset

def _to_str(val):
    # float|str => str
    if isinstance(val, float):
        return format(val, '.8f')
    return val


def main():
    result_rows = []
    
    for input_filepath in INPUT_CSV_FILES:

        prev_rfid = ''
        prev_asset = ''
        prev_amount = 0
        prev_tx_type = ''
        prev_fee = 0
        prev_result = None

        with open(input_filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            row_num = 0
            for row in csv_reader:
                row_num += 1
                if row_num == 1:
                    print(f'Reading {input_filepath}')
                    print(f'Column names are {", ".join(row)}')
                    continue

                txid = row[0]
                rfid = row[1]
                time = row[2]
                tx_type = row[3]
                subtype = row[4]
                asset = _convert_asset_name(row[6])
                amount = round(float(row[7]), 8)
                fee = round(float(row[8]), 8)

                is_valid = True
                safe_to_ignore = False
                new_row = {}
                new_row["Date"] = time
                new_row["Transaction ID"] = txid
                new_row["Fee Amount"] = fee
                new_row["Fee Asset"] = asset

                if tx_type == "trade":
                    if rfid != prev_rfid:
                        # Handle trades 2 rows at a time, skip this row
                        safe_to_ignore = True
                        is_valid = False
                    else:
                        if "USD" in asset or "USD" in prev_asset:
                            # Treat USD trades as special case and only make one resulting row two rows in the original csv
                            new_row["Sent Asset"] = prev_asset
                            new_row["Sent Amount"] = abs(prev_amount)
                            new_row["Received Asset"] = asset
                            new_row["Received Amount"] = abs(amount)
                            if prev_fee and not fee:
                                # Fee can come comes from first (in this case previous) transaction
                                new_row["Fee Amount"] = prev_fee
                                new_row["Fee Asset"] = prev_asset
                            if "USD" in prev_asset and prev_amount < 0:
                                # Sold USD, gained crypto
                                new_row["Type"] = "Buy"
                                # Optional: set purchased value = to USD value
                                # new_row["Market Value Currency"] = "USD"
                                # new_row["Market Value"] = abs(prev_amount)
                            elif "USD" in asset and prev_amount < 0:
                                # Sold crypto, gained USD
                                new_row["Type"] = "Sale"
                                new_row["Market Value Currency"] = "USD"
                                new_row["Market Value"] = abs(amount)
                            else:
                                is_valid = False
                        elif "USD" not in asset:
                            # Non-USD trade (e.g. crypto for crypto trade)
                            if prev_amount < 0:
                                # Previous asset was 'sold', current one was 'bought'
                                new_row["Type"] = "Buy"

                                new_row["Sent Asset"] = prev_asset
                                new_row["Sent Amount"] = abs(prev_amount)
                                new_row["Received Asset"] = asset
                                new_row["Received Amount"] = abs(amount)

                                prev_result["Type"] = "Sale"

                                prev_result["Sent Asset"] = prev_asset
                                prev_result["Sent Amount"] = abs(prev_amount)
                                prev_result["Received Asset"] = asset
                                prev_result["Received Amount"] = abs(amount)
                                
                            else:
                                # Previous asset was 'bought', current one was 'sold'
                                # Not sure if kraken ledgers ever print transactions in this order but adding this to be safe
                                new_row["Type"] = "Sale"
                                new_row["Sent Asset"] = asset
                                new_row["Sent Amount"] = abs(prev_amount)
                                new_row["Received Asset"] = prev_asset
                                new_row["Received Amount"] = abs(amount)

                                prev_result["Type"] = "Buy"
                                prev_result["Received Asset"] = prev_asset
                                prev_result["Received Amount"] = abs(amount)
                                prev_result["Sent Asset"] = asset
                                prev_result["Sent Amount"] = abs(prev_amount)
                                
                            # Add old result as trade (new result will be added below)
                            cols = [_to_str(prev_result.get(header, "")) for header in DESIRED_HEADERS]
                            result_rows.append(cols)
                elif tx_type == "deposit" and txid and not IGNORE_DEPOSIT_WITHDRAW:
                    new_row["Type"] = "Deposit"
                    new_row["Received Asset"] = asset
                    new_row["Received Amount"] = abs(amount)
                    new_row["Fee Amount"] = fee
                    new_row["Fee Asset"] = asset
                elif tx_type == "withdrawal" and txid and not IGNORE_DEPOSIT_WITHDRAW:
                    # Withdrawal = sale to someone, Transfer = transfer to another wallet you own
                    # new_row["Type"] = "Withdrawal"
                    new_row["Type"] = "Transfer"
                    new_row["Sent Asset"] = asset
                    new_row["Sent Amount"] = abs(amount)
                    new_row["Fee Amount"] = fee
                    new_row["Fee Asset"] = asset
                elif tx_type == "staking":
                    new_row["Type"] = "Stake"
                    new_row["Received Asset"] = _convert_staking_asset_name(asset)
                    new_row["Received Amount"] = abs(amount)
                elif tx_type == "transfer" and subtype == "spotfromfutures" \
                     and prev_rfid == rfid and prev_tx_type == "deposit":
                    # This seems to be the patten when an asset is deposited after a fork
                    # TODO: handle airdrop as well
                    new_row["Type"] = "Fork"
                    new_row["Received Asset"] = asset
                    new_row["Received Amount"] = abs(amount)
                else:
                    is_valid = False

                if is_valid:
                    cols = [_to_str(new_row.get(header, "")) for header in DESIRED_HEADERS]
                    result_rows.append(cols)
                elif txid and not safe_to_ignore:
                    print(f"Skipping row {row_num}: {row}")

                prev_rfid = rfid
                prev_asset = asset
                prev_amount = amount
                prev_tx_type = tx_type
                prev_fee = fee
                prev_result = new_row

    # Save results
    with open(RESULT_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(DESIRED_HEADERS)
        writer.writerows(result_rows)


if __name__ == "__main__":
    main()