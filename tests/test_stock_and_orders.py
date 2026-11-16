import json

from conftest import make_message


def pid_with_stock(api, at_least=60):
    return next(p["id"] for p in api.SEED_CATALOG if p["stock"] >= at_least)


def test_reserve_takes_only_what_is_left(api):
    api.get_catalog()
    api.store_set("stock", "t1", 5)
    assert api.reserve_stock("t1", 3) == 3
    assert api.reserve_stock("t1", 10) == 2      # faqat qolgan 2 tasi
    assert api.reserve_stock("t1", 1) == 0
    assert api.store_get("stock", "t1") == 0     # manfiyga tushmaydi


def test_order_uses_server_prices_and_reserves_stock(api):
    pid = pid_with_stock(api)
    before = api.get_catalog()[pid]
    # mijoz soxta narx va summa yuborsa ham, ular hisobga olinmaydi
    api.handle_order(make_message(json.dumps({"n": "Ali", "d": "Taksi", "a": "Urganch", "i": [[pid, 2, 1]], "total": 1})))
    order = next(iter(api.store_all("orders2").values()))
    assert order["pt"] == "Chakana"
    assert order["total"] == 2 * before["retail"]
    assert order["items"][0]["p"] == before["retail"]
    assert api.get_catalog()[pid]["stock"] == before["stock"] - 2


def test_wholesale_price_from_threshold(api):
    pid = pid_with_stock(api)
    p = api.get_catalog()[pid]
    api.handle_order(make_message(json.dumps({"i": [[pid, api.WHOLESALE_MIN]]})))
    order = next(iter(api.store_all("orders2").values()))
    assert order["pt"] == "Optom"
    assert order["total"] == api.WHOLESALE_MIN * p["wholesale"]


def test_order_is_cut_to_available_stock(api):
    pid = pid_with_stock(api)
    api.get_catalog()
    api.store_set("stock", pid, 3)
    api.handle_order(make_message(json.dumps({"i": [[pid, 10]]})))
    order = next(iter(api.store_all("orders2").values()))
    assert order["qty"] == 3 and order["items"][0]["asked"] == 10
    assert api.get_catalog()[pid]["stock"] == 0


def test_bad_orders_are_ignored(api):
    for raw in ("not json", "[]", json.dumps({"i": [["99999999", 5]]}), json.dumps({"i": [["abc", 1], [1001, -3]]})):
        api.handle_order(make_message(raw))
    assert api.store_all("orders2") == {}


def test_cancel_returns_stock_once(api):
    pid = pid_with_stock(api)
    start = api.get_catalog()[pid]["stock"]
    api.handle_order(make_message(json.dumps({"i": [[pid, 4]]})))
    order = next(iter(api.store_all("orders2").values()))
    api.release_order_stock(order)
    api.release_order_stock(order)               # ikkinchi marta qaytarmaydi
    assert api.get_catalog()[pid]["stock"] == start
