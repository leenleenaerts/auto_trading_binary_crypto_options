# Import necessary modules
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import scipy as sc
import numpy as np


def get_book_summary_by_currency(currency, kind):
    url = "/api/v2/public/get_book_summary_by_currency"
    parameters = {
        'currency': currency,
        'kind': kind,
    }
    # send HTTPS GET request
    api_exchange_address = "https://www.deribit.com"
    json_response = requests.get((api_exchange_address + url + "?"), params=parameters)
    response_dict = json.loads(json_response.content)
    book_summary = response_dict["result"]

    return book_summary


# Function to get a list of call option names for a given coin and expiration time
def get_option_name(coin, expiration_time=None):

    # Request public API to get instrument data
    r = requests.get("https://deribit.com/api/v2/public/get_instruments?currency=" + coin + "&kind=option")
    result = json.loads(r.text)

    # Extract option names
    name = pd.json_normalize(result['result'])['instrument_name']
    name = list(name)

    name_list = []
    # Create a prefix for the option names based on the coin and expiration date
    if expiration_time:
        start = coin + "-" + expiration_time.strftime("%#d%b%y").upper()
        # Filter option names based on the option type and expiration_date
        for option in name:
            if option[-1] == "C" and start in option:
                name_list.append(option)

    # No expiration date given in funtion call
    else:
        for option in name:
                if option[-1] == "C":
                    name_list.append(option)
    return name_list


# Function to get list of option price data for a given coin and list of option names
def get_option_data(coin, exp_date, expiration_time):
    option_name = get_option_name(coin, exp_date)

    # Initialize data frame to store option price data
    coin_df = []

    # Loop to download data for each Option Name
    for i in range(len(option_name)):
        # Download option data -- requests and convert json to pandas
        r = requests.get('https://deribit.com/api/v2/public/get_order_book?instrument_name=' + option_name[i])
        result = json.loads(r.text)
        df = pd.json_normalize(result['result'])

        # Append data to data frame
        coin_df.append(df)

    # Finalize data frame
    coin_df = pd.concat(coin_df)

    # Remove data we don't need
    coin_df = coin_df[["instrument_name", "mark_price"]].copy()

    pricelist = coin_df.values.tolist()
    start = coin + "-" + expiration_time.strftime("%#d%b%y").upper()

    # Extract strike prices from option names and convert them to integers for easier processing
    for pair in pricelist:
        pair[0] = int(pair[0].split('-')[2])

    return pricelist


# Function to get the current price of the coin using the Deribit API
def get_coin_price(coin):
    msg = \
        {"jsonrpc": "2.0",
         "method": "public/get_index_price",
         "id": 42,
         "params": {
             "index_name": coin.lower() + "_usd"}
         }
    url = 'https://test.deribit.com/api/v2/public/get_index_price'
    response = requests.post(url, json=msg).json()
    return response["result"]["index_price"]


def find_probability(coin, expiration_time, strike):

    now = datetime.now()
    time_to_expiration = (expiration_time - datetime.now()).total_seconds() / (365 * 24 * 60 * 60)  # in years
    discount_rate = 0.0525

    # Get the current price of the coin
    price = get_coin_price(coin)

    if price == 0:
        print("Error: Unable to fetch the current price from Deribit API.")
        exit()

    book = get_book_summary_by_currency(coin, 'option')
    filtered_book = [{'instrument_name': item['instrument_name'], 'mark_price': item['mark_price']} for item in book]
    # Get all option dates for a given currency added to a list
    option_names = get_option_name(coin)
    # Create a list of expiration_dates
    dates = []
    # create a list of time to expirations in seconds
    time_to_expirations = []
    for name in option_names:
        date = name.split('-')[1]
        date = datetime.strptime(date, "%d%b%y")
        # Remove double dates and dates out of range
        if date not in dates:
            time_to_exp_date = (date + timedelta(hours=2) - now).total_seconds() / (365 * 24 * 60 * 60)
            time_dev = time_to_exp_date / time_to_expiration
            if 5 > time_dev > 0.1:
                dates.append(date)
                time_to_expirations.append(time_to_exp_date)

    if len(dates) < 3:
        print("Not enough data points to estimate probability")
        exit()

    # Calculate predicted probability of being ITM at expiration for all expiration dates and store probabilities in a list
    ITM_probabilities = []
    for exp_date in dates:
        date_string = exp_date.strftime("%e%b%y").upper()

        strikes, prices = [], []
        # Initialize lists to store relevant strike prices and option prices
        price_list = []
        for item in filtered_book:
            instrument_name = item['instrument_name']
            mark_price = item['mark_price']

            # Check if the target date is part of the instrument name
            if date_string.strip() == instrument_name.split('-')[1] and instrument_name[-1] == 'C':
                # Extract the strike number after the target date
                parts = instrument_name.split('-')
                if len(parts) >= 3:
                    strikes.append(int(parts[2]))
                    prices.append(mark_price * price)

        # Interpolate the option prices using a quadratic interpolation method
        Interpolation = sc.interpolate.interp1d(strikes, prices, kind='quadratic', fill_value='extrapolate')
        # Calculate the predicted option price at the given strike price and the probability of it expiring ITM
        # We create a binary option (call bull spread with an extremely small difference in strike prices: dstrike) paying out $ 1.00 if the coinprice is ATM/ITM at expiration.
        dstrike = price / 10000
        predicted_price_at_K = Interpolation(strike)
        probability_ITM = ((Interpolation(strike - dstrike / 2) - Interpolation(strike + dstrike / 2)) / dstrike) * np.exp(time_to_expiration * discount_rate)
        ITM_probabilities.append(probability_ITM)

    # Interpolate the option probabilities for different time to expirations using a quadratic interpolation method
    Interpolation = sc.interpolate.interp1d(time_to_expirations, ITM_probabilities, kind='quadratic',
                                            fill_value='extrapolate')

    # Calculate the predicted ITM probability at the given expiration time and strike price
    predicted_probability = Interpolation(time_to_expiration)
    price_yes = predicted_probability * np.exp(-time_to_expiration * discount_rate)

    # Print the results
    print(f"{coin} : $ {price:.2f} | strike: {strike} | {100 * predicted_probability:.2f} %")

    return predicted_probability

# Main function
if __name__ == "__main__":
    coin = "BTC"  # Example coin
    expiration_time = datetime(2023,9,22, 10)  # Example expiration time 2
    print(expiration_time)
    strikes = [26000,26500,27000,27500,28000,28500,29000]  # Example strike
    probs = []
    for s in strikes:
        p = find_probability(coin, expiration_time, s)
        probs.append(p)

    for i in range(len(strikes) - 1):
        for j in range(i+1,len(strikes)):
            print(f"{strikes[i]} - {strikes[j]} : {100 * (probs[i] - probs[j]):.2f} %")

    coin = "ETH"  # Example coin
    strikes = [1580,1600, 1620,1660,1700,1740]  # Example strike
    probs = []
    for s in strikes:
        p = find_probability(coin, expiration_time, s)
        probs.append(p)

    for i in range(len(strikes) - 1):
        for j in range(i+1,len(strikes)):
            print(f"{strikes[i]} - {strikes[j]} : {100 * (probs[i] - probs[j]):.2f} %")






