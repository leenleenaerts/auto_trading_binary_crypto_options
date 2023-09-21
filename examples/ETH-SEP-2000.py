import calculate_probability
from poly_order_functions import *

# Main function
if __name__ == "__main__":
    yes_token = "81907801024000564954616092796768471700214599794068308524980740531806176223215"
    no_token = "28601896009848292737837970442888227527788768015752651484914905629056684518536"
    market = "0xa05d0a1714044e8777ff977d665aaf6dec1edf67c357c90168ceab9b5455cb79"

    coin = "ETH"
    expiration_date = "09/30/2023"
    expiration_hour = 22

    strike = 2000
    size = 1000
    lower_bound = 0.005
    upper_bound = 0.025
    three_decimals = True

    expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=expiration_hour)
    client = connect()
    place_orders(client=client, market=market, coin=coin, size=size, expiration_time=expiration_time, strike=strike,
                 yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound,
                 three_decimals=three_decimals)