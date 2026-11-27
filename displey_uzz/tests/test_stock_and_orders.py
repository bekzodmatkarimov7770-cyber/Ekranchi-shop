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
    assert order["pt"] == "Dona"
    assert order["total"] == 2 * before["retail"]
    assert order["items"][0]["p"] == before["retail"]
    assert api.get_catalog()[pid]["stock"] == before["stock"] - 2


def test_big_order_still_uses_retail_price(api):
    """Displey_Uzz: optom yo'q, 50+ dona olinsa ham narx dona narxida qoladi."""
    pid = pid_with_stock(api)
    p = api.get_catalog()[pid]
    q = min(60, p["stock"])
    api.handle_order(make_message(json.dumps({"i": [[pid, q]]})))
    order = next(iter(api.store_all("orders2").values()))
    assert order["pt"] == "Dona"
    assert order["total"] == q * p["retail"]


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


def test_order_items_show_brand_and_quality(api):
    """Admin buyurtmada qaysi ekran (brend, model, sifat/seriya) ekanini aniq ko'rishi kerak."""
    pid = pid_with_stock(api)
    cat = api.get_catalog()[pid]
    api.handle_order(make_message(json.dumps({"i": [[pid, 1]]})))
    order = next(iter(api.store_all("orders2").values()))
    it = order["items"][0]
    assert it["b"] == cat["brand"] and it["ty"] == cat["type"]
    label = api.item_label(it)
    assert cat["brand"] in label and cat["type"] in label
    caption = api.bot.send_document.call_args.kwargs["caption"]
    assert cat["type"] in caption and cat["brand"] in caption


def test_old_orders_get_quality_from_catalog(api):
    pid = pid_with_stock(api)
    cat = api.get_catalog()[pid]
    old = {"id": "E1", "items": [{"id": pid, "n": cat["name"], "oq": 1, "aq": 1, "p": 1}]}
    api.enrich_items(old)
    assert old["items"][0]["l"] == f"{cat['brand']} {cat['name'].rstrip(' /')} [{cat['type']}]"


def test_admin_back_button_works_with_order_id(api):
    """Admin buyurtma ekranida "Orqaga" bosganda (callback'da buyurtma raqami E1001) bot yiqilmasligi kerak."""
    import types as t
    pid = pid_with_stock(api)
    api.handle_order(make_message(json.dumps({"i": [[pid, 1]]})))
    oid = next(iter(api.store_all("orders2").values()))["id"]
    c = t.SimpleNamespace(id="cb", data=f"back_ord:{oid}", from_user=t.SimpleNamespace(id=777),
                          message=t.SimpleNamespace(chat=t.SimpleNamespace(id=777), message_id=5))
    api.handle_back_ord(c)
    txt = api.bot.edit_message_caption.call_args.kwargs.get("caption") or api.bot.edit_message_caption.call_args.args[0]
    assert "tg://user?id=42" in txt and "Rejim" not in txt
