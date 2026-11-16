import time


def auth(api):
    return {"X-Admin-Token": api.make_admin_token()}


def test_admin_token(api):
    tok = api.make_admin_token()
    assert api.check_admin_token(tok)
    exp, sig = tok.split(".")
    assert not api.check_admin_token(f"{int(exp) + 1}.{sig}")          # muddatni o'zgartirib bo'lmaydi
    assert not api.check_admin_token(f"{exp}.{'0' * 40}")
    assert not api.check_admin_token(api.make_admin_token(days=-1))    # muddati o'tgan
    assert not api.check_admin_token("") and not api.check_admin_token("abc")


def test_admin_api_requires_token(client):
    assert client.get("/api/index?admin=data").status_code == 401
    assert client.get("/api/index?admin=data", headers={"X-Admin-Token": f"{int(time.time()) + 99}.bad"}).status_code == 401
    assert client.post("/api/index?admin=catalog_save", json={"changes": []}).status_code == 401


def test_admin_can_change_price_and_stock(api, client):
    pid = api.SEED_CATALOG[0]["id"]
    r = client.post("/api/index?admin=catalog_save", headers=auth(api),
                    json={"changes": [{"id": pid, "retail": 91000, "wholesale": 70000, "stock": 7}]})
    assert r.status_code == 200, r.get_json()
    p = api.get_catalog()[pid]
    assert (p["retail"], p["wholesale"], p["stock"]) == (91000, 70000, 7)


def test_admin_save_rejects_bad_values(api, client):
    pid = api.SEED_CATALOG[0]["id"]
    before = api.get_catalog()[pid]
    for change in ({"id": pid, "retail": 10, "wholesale": 20},       # optom chakanadan qimmat
                   {"id": pid, "retail": -5},
                   {"id": pid, "stock": -1},
                   {"id": pid, "img": "javascript:alert(1)"},
                   {"id": "yoq-id", "retail": 5}):
        r = client.post("/api/index?admin=catalog_save", headers=auth(api), json={"changes": [change]})
        assert r.status_code == 400, change
    assert api.get_catalog()[pid] == before


def test_admin_adds_new_product(api, client):
    r = client.post("/api/index?admin=catalog_save", headers=auth(api),
                    json={"changes": [{"id": "new", "brand": "Samsung", "type": "OLED", "name": "S99", "retail": 500000, "wholesale": 400000, "stock": 2}]})
    assert r.status_code == 200
    new = [p for p in api.get_catalog().values() if p["name"] == "S99"]
    assert len(new) == 1 and new[0]["stock"] == 2
    assert int(new[0]["id"]) > max(int(p["id"]) for p in api.SEED_CATALOG)


def test_webhook_rejects_wrong_secret(client):
    assert client.post("/api/index", json={"update_id": 1}).status_code == 403
    assert client.post("/api/index", json={"update_id": 1},
                       headers={"X-Telegram-Bot-Api-Secret-Token": "notogri"}).status_code == 403


def test_webhook_setup_needs_key(client):
    assert client.get("/ulash?key=notogri").status_code in (401, 403)


def test_shop_button_points_to_vercel(api):
    assert api.WEB_APP_URL.startswith("https://ekranchi-shop.vercel.app/market.html")
