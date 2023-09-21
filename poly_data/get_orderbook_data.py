from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType, FilterParams
from py_order_utils.model import POLY_GNOSIS_SAFE
import json

token = "96770643535559387395744446509062053833553289852215722608524092808919316842219"
market = "0x6704fd187f9558298b9e27279103a00a0f4892d47fb2068a9f3272bf8b3a2065"

def connect():
    host: str = "https://clob.polymarket.com"
    key: str = "xxxxxxxxxxxxxxxxxxxxx"
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

client = connect()

orderbook = client.get_order_book(token)

size_my_yes_order, size_my_no_order = 0, 0
price_my_yes_order, price_my_no_order = 0, 0
previous_orders = client.get_orders(FilterParams(market=market, ))

for order in previous_orders:
    if order["outcome"] == "Yes":
        size_my_yes_order = float(order["original_size"]) - float(order["size_matched"])
        price_my_yes_order = float(order["price"])
    else:
        size_my_no_order = float(order["original_size"]) - float(order["size_matched"])
        price_my_no_order = float(order["price"])

for order in orderbook.bids[::-1]:
    if float(order.price) == price_my_yes_order:
        if float(order.size) >= float(size_my_yes_order) + 50:
            top_bid = float(order.price)
            break
    else:
        if float(order.size) >= 50:
            top_bid = float(order.price)
            break

for order in orderbook.asks[::-1]:
    if float(order.price) == 1 - price_my_no_order:
        if float(order.size) >= float(size_my_no_order) + 50:
            top_ask = float(order.price)
            break
    else:
        if float(order.size) >= 50:
            top_ask = float(order.price)
            break
print(orderbook)
print(top_bid, top_ask)

