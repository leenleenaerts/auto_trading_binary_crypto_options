import calculate_probability
from poly_order_functions import *

# Main function
if __name__ == "__main__":
    yes_token = "17026667753530285305564739302435826148603240635579023153510353052090782191125"
    no_token = "42640553165092037846347881679624913552188313575661128788898865694578369787637"
    market = "0xb677cc4c85331b682e124b86418bcabfde068aed4159f8078ece79cbf5b37e48"

    coin = "ETH"
    expiration_date = "12/31/2023"
    expiration_hour = 22

    strike = 2000
    size = 100
    lower_bound = 0.03
    upper_bound = 0.07
    probability_factor = 2

    expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=expiration_hour)
    client = connect()
    place_orders(client=client, market=market, coin=coin, size=size, expiration_time=expiration_time, strike=strike, yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound, probability_factor=probability_factor)