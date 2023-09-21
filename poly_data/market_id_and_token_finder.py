from datetime import datetime
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType, FilterParams
from py_clob_client.order_builder.constants import BUY, SELL
from py_order_utils.model import POLY_GNOSIS_SAFE
from time import sleep
import requests
import sys
import math
import json

def filter_by_exp_and_coin(data: list[dict], coin: str, expiration_date: str) -> list:
    filtered_data = []
    for market in data:
        if market["end_date_iso"] == expiration_date and "1,600" in market["question"]:
            filtered_data.append(market)
    return filtered_data

def filter_tokens_by_outcome(tokens: list[dict], outcome: str = "Yes") -> str or None:
    for token in tokens:
        if token['outcome'] == outcome:
            return token['token_id']
    return None

def convert_date_format(date: str) -> str:
    try:
        return datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("Invalid date format")
        return None

def connect():
    host: str = "https://clob.polymarket.com"
    key: str = "xxxxxxxxxxxxxxxxxxxxxx"
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

def get_filtered_market(client: ClobClient, coin: str, expiration_date: str) -> list:
    data = client.get_markets()
    next_cursor = data["next_cursor"]
    data = data["data"]
    filtered_data = filter_by_exp_and_coin(data, coin, expiration_date)

    while next_cursor != "LTE=":
        data = client.get_markets(next_cursor=next_cursor)
        next_cursor = data["next_cursor"]
        data = data["data"]
        filtered_data.extend(filter_by_exp_and_coin(data, coin, expiration_date))

    return filtered_data

def filter_orders_by_market_id(orders: list[dict], market_id: str) -> list:
    filtered_orders = []
    for order in orders:
        if order["market"] == market_id:
            filtered_orders.append(order)
    return filtered_orders

coin = "ETH"
expiration_date = "09/22/2023"
expiration_time = datetime.strptime(expiration_date, "%m/%d/%Y").replace(hour=22)
expiration_date_poly = convert_date_format(expiration_date)

client = connect()

filtered_markets = get_filtered_market(client, coin, expiration_date_poly)
print(filtered_markets)
if len(filtered_markets) > 1:
    sys.exit("More than 1 market found")
elif len(filtered_markets) < 1:
        sys.exit("No market found")

for market in filtered_markets:
    yes_token = filter_tokens_by_outcome(market["tokens"], "Yes")
    no_token = filter_tokens_by_outcome(market["tokens"], "No")

print('market')
print(filtered_markets[0]["condition_id"])
print('yes')
print(yes_token)
print('no')
print(no_token)





