from datetime import datetime
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType, FilterParams
from py_clob_client.order_builder.constants import BUY, SELL
from py_order_utils.model import POLY_GNOSIS_SAFE
from time import sleep
import cme_interest
import requests
import sys
import math
import json

def create_order(client, price, size, side, token_id, order_type = OrderType.GTC):
    order_args = OrderArgs(
        price=price,
        size=size,
        side=side,
        token_id=token_id,
    )
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order, order_type)
    return resp

def connect():
    host: str = "https://clob.polymarket.com"
    key: str = "f87b828770be38e38d949eea27689e211f128cde0e1a3d4e1ebacf4dd92cd3a9"
    chain_id: int = POLYGON

    with open('creds.json') as creds_file:
        creds_data = creds_file.read()
    creds_json = json.loads(creds_data)
    creds = ApiCreds(
        api_key=creds_json["api_key"],
        api_secret=creds_json["api_secret"],
        api_passphrase=creds_json["api_passphrase"]
    )
    funder = creds_json["funder"]
    signature_type = POLY_GNOSIS_SAFE
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds, signature_type=signature_type, funder=funder)
    return client

# returns best bid and ask from competition (size >= 50) for yes shares
def current_spread(client, market, yes_token, no_token):
    orderbook = client.get_order_book(yes_token)
    size_my_yes_order, size_my_no_order = 0, 0
    price_my_yes_order, price_my_no_order = 0, 0
    top_ask, top_bid = 1, 0
    prev_orders = client.get_orders(FilterParams(market=market, ))

    for order in prev_orders:
        if order["outcome"] == "Yes":
            size_my_yes_order = float(order["original_size"]) - float(order["size_matched"])
            price_my_yes_order = float(order["price"])
        else:
            size_my_no_order = float(order["original_size"]) - float(order["size_matched"])
            price_my_no_order = float(order["price"])

    for order in orderbook.bids[::-1]:
        if float(order.price) == price_my_yes_order:
            if float(order.size) >= float(size_my_yes_order) + 20:
                top_bid = float(order.price)
                break
        else:
            if float(order.size) >= 20:
                top_bid = float(order.price)
                break

    for order in orderbook.asks[::-1]:
        if 1000 * float(order.price) == 1000 - 1000 * price_my_no_order:
            if float(order.size) >= float(size_my_no_order) + 20:
                top_ask = float(order.price)
                break
        else:
            if float(order.size) >= 20:
                top_ask = float(order.price)
                break
    return top_bid, top_ask

def FOK_order(client, buy_price_yes, buy_price_no, yes_token, no_token, size):
    orderbook = client.get_order_book(yes_token)
    for order in orderbook.bids[::-1]:
        if 1000 * float(order.price) >= (1000 - 1000 * buy_price_no):
            if float(order.size) > 1:
                rounded_size = round(float(order.size))
                create_order(client, 1 - float(order.price), rounded_size, BUY, no_token, order_type=OrderType.FOK)
                print(f"FOK no order sent - {rounded_size} shares for $ {1 - float(order.price)}")
                quit()
        else:
            break

    for order in orderbook.asks[::-1]:
        if float(order.price) <= buy_price_yes:
            if float(order.size) > 1:
                rounded_size = round(float(order.size))
                create_order(client, float(order.price), rounded_size, BUY, yes_token, order_type=OrderType.FOK)
                print(f"FOK yes order sent - {rounded_size} shares for $ {order.price}")
        else:
            break


def place_orders(client, market, size, yes_token, no_token, lower_bound, upper_bound, min_int, max_int, date_string, three_decimals=False,):
    while True:
        try:
            previous_orders = client.get_orders(FilterParams(market=market, ))

            try:
                probability = cme_interest.calculate_interest_rate_probability(date_string, min_int, max_int)
            except:
                client.cancel_orders([order["id"] for order in previous_orders])
                print("An error occurred in calculating our probability, all orders cancelled.")
                continue

            if probability > 1 or probability < 0:
                for order in previous_orders:
                    if order['asset_id'] == yes_token or order['asset_id'] == no_token:
                        client.cancel(order["id"])
                print(f"Probability calculated at {probability} is impossible. Orders canceled")
                continue

            if 'probability_old' in locals():
                if abs(probability - probability_old) > 0.02:
                    for order in previous_orders:
                        if order['asset_id'] == yes_token or order['asset_id'] == no_token:
                            client.cancel(order["id"])
                    print(f"Probability changed too much this iteration. Orders canceled")
                    quit()
                    probability_old = probability
                    continue

            probability_old = probability

            low_price, high_price = current_spread(client=client, market=market, yes_token=yes_token, no_token=no_token)

            if three_decimals:
                buy_price_yes_FOK = math.floor((probability - lower_bound) * 1000) / 1000
                buy_price_no_FOK = math.floor((1 - probability - upper_bound) * 1000) / 1000
                buy_price_yes_limit = math.floor(min((probability - lower_bound), low_price + 0.001001) * 1000) / 1000
                buy_price_no_limit = math.floor(min((1 - probability - upper_bound), 1 - high_price + 0.001001) * 1000) / 1000
            else:
                buy_price_yes_FOK = math.floor((probability - lower_bound) * 100) / 100
                buy_price_no_FOK = math.floor((1 - probability - upper_bound) * 100) / 100
                buy_price_yes_limit = math.floor(min((probability - lower_bound), low_price + 0.01001) * 100) / 100
                buy_price_no_limit = math.floor(min((1 - probability - upper_bound), 1 - high_price + 0.01001) * 100) / 100

            yes_trade = False
            no_trade = False

            for order in previous_orders:
                # cancel yes orders
                if order["side"] == BUY and order['asset_id'] == yes_token:
                    if float(order["price"]) != buy_price_yes_limit or float(order["size_matched"]) > 50:
                        client.cancel(order["id"])
                    else:
                        yes_trade = True
                        print(f"keeping yes price at $ {buy_price_yes_limit:.3f}")

                # cancel no orders
                if order["side"] == BUY and order['asset_id'] == no_token:
                    if float(order["price"]) != buy_price_no_limit or float(order["size_matched"]) > 50:
                        client.cancel(order["id"])
                    else:
                        no_trade = True
                        print(f"keeping no price at $ {buy_price_no_limit:.3f}")

            # Place FOK orders
            FOK_order(client=client, buy_price_yes=buy_price_yes_FOK, buy_price_no=buy_price_no_FOK, yes_token=yes_token, no_token=no_token, size=size)

            # Place limit orders
            if not yes_trade and buy_price_yes_limit > 0:
                create_order(client, buy_price_yes_limit, size, BUY, yes_token)
                print(f"yes order created at price $ {buy_price_yes_limit:.3f}")
            if not no_trade and buy_price_no_limit > 0:
                create_order(client, buy_price_no_limit, size, BUY, no_token)
                print(f"no order created at price $ {buy_price_no_limit:.3f}")

                sleep(60)
        except:
            print("Failed placing or canceling orders")
            try:
                client.cancel_all()
                print("All orders canceled.")
            except:
                print("Failed to cancel all orders.")
        print()