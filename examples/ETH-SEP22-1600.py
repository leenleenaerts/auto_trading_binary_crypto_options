import calculate_probability
from poly_order_functions import *

# Main function
if __name__ == "__main__":
    yes_token = "24442542437207114403326893209737383871767978259303433192462980981344338960947"
    no_token = "38299503838678785982522915893641645734360652046015187519829074730486528028339"
    market = "0x948e5795b54a8c59d75fa87a34d1c9c1acaee005feafb45bc3d9c43ca7437571"

    coin = "ETH"
    expiration_date = "09/22/2023"
    expiration_hour = 10

    strike = 1600
    size = 100
    lower_bound = 0.04
    upper_bound = 0.04
    three_decimals = False

    expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=expiration_hour)
    client = connect()
    place_orders(client=client, market=market, coin=coin, size=size, expiration_time=expiration_time, strike=strike,
                 yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound,
                 three_decimals=three_decimals)