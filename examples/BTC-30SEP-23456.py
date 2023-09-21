import calculate_probability
from poly_order_functions import *

# Main function
if __name__ == "__main__":
    yes_token = "80072298785077085713714011267899485823303448408928020311127526826030183292540"
    no_token = "5075377821241532070539420613469205533076258034455158977219149660020819422199"
    market = "0x52880d7713a79334e38760fa98e1d95c90a184057dd0ccab6ff9f99fc50d2c6e"

    coin = "BTC"
    expiration_date = "09/30/2023"
    expiration_hour = 22

    strike = 23456.78
    size = 100
    lower_bound = 0.045
    upper_bound = 0.002
    three_decimals = False

    expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=expiration_hour)
    client = connect()
    place_orders(client=client, market=market, coin=coin, size=size, expiration_time=expiration_time, strike=strike,
                 yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound,
                 three_decimals=three_decimals)