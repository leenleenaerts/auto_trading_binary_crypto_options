import calculate_probability
from poly_order_functions import *

# Main function
if __name__ == "__main__":
    yes_token = "8168025378324596815664348056592173734009066733825596540382631119019419043401"
    no_token = "84982384761726386591789303123432103272353665524929488298571131682494752817962"
    market = "0x7bceda5c36f547d3becec394a917247af6b0553fbbb385e44a40228b0bd87807"

    coin = "BTC"
    expiration_date = "09/30/2023"
    expiration_hour = 22

    strike = 27000
    size = 100
    lower_bound = 0.04
    upper_bound = 0.04
    three_decimals = False

    expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=expiration_hour)
    client = connect()
    place_orders(client=client, market=market, coin=coin, size=size, expiration_time=expiration_time, strike=strike,
                 yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound,
                 three_decimals=three_decimals)