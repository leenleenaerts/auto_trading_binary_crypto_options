from py_clob_client.client import ClobClient


def filter_orders_by_market_id(orders: list[dict], market_id: str) -> list:
    filtered_orders = []
    for order in orders:
        if order["market"] == market_id:
            filtered_orders.append(order)
    return filtered_orders


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


def filter_by_exp_and_coin(data: list[dict], coin: str, expiration_date: str) -> list:
    filtered_data = []
    for market in data:
        if market["end_date_iso"] == expiration_date and coin.lower() in market["question"].lower():
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
