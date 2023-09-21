from poly_order_functions_cme import *

# Main function
if __name__ == "__main__":
    yes_token = "70123190754218176276461522101850583945350866997322551252653457715680460590286"
    no_token = "112716164541014829079150856560443464883834773561535527138135944219634295662177"
    market = "0x2fa329f505aafb81f53e1bb4b77548101e409784811206285ce36ad10151e9ab"

    size = 15
    lower_bound = 0.03
    upper_bound = 0.04

    min_int = 525
    max_int = 550
    date_string = "Sep 2023"

    client = connect()
    place_orders(client=client, market=market, size=size, yes_token=yes_token, no_token=no_token, lower_bound=lower_bound, upper_bound=upper_bound, min_int=min_int, max_int=max_int, date_string=date_string)



