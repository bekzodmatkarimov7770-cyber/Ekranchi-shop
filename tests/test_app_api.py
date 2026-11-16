"""Ilova (APK) API: Telegram orqali kirish, buyurtma berish va buyurtmalar tarixi."""
import types

CID = 4242


def start_login(api, client):
    api.bot.get_me.return_value = types.SimpleNamespace(username="ekranchi_test_bot")
    api._bot_username = ""
    r = client.post("/api/index?app=login_start")
    assert r.status_code == 200
    return r.get_json()


def confirm_in_telegram(api, code, cid=CID):
    cb = types.SimpleNamespace(id="1", data=f"applogin:{code}",
                               from_user=types.SimpleNamespace(id=cid, first_name="Sardor", username="sardor"),
                               message=types.SimpleNamespace(chat=types.SimpleNamespace(id=cid), message_id=1))
    api.handle_app_login(cb)


def login(api, client, cid=CID):
    d = start_login(api, client)
    confirm_in_telegram(api, d["code"], cid)
    r = client.post("/api/index?app=login_check", json={"code": d["code"], "poll": d["poll"]})
    return r.get_json()["token"]


def test_login_flow(api, client):
    d = start_login(api, client)
    assert d["url"] == f"https://t.me/ekranchi_test_bot?start=app_{d['code']}"
    check = lambda: client.post("/api/index?app=login_check", json={"code": d["code"], "poll": d["poll"]})
    assert check().get_json() == {"pending": True}           # Telegramda hali tasdiqlanmagan
    confirm_in_telegram(api, d["code"])
    body = check().get_json()
    assert api.check_app_token(body["token"]) == str(CID)
    assert body["user"]["name"] == "Sardor"
    assert check().status_code == 410                        # kod bir marta ishlaydi


def test_start_link_asks_for_confirmation_first(api, client):
    d = start_login(api, client)
    msg = types.SimpleNamespace(text=f"/start app_{d['code']}", chat=types.SimpleNamespace(id=CID),
                                from_user=types.SimpleNamespace(id=CID, first_name="Sardor", username=None))
    api.handle_start(msg)
    # havolani ochishning o'zi kirish emas: mijoz tugmani bosib tasdiqlamaguncha sessiya ochilmaydi
    r = client.post("/api/index?app=login_check", json={"code": d["code"], "poll": d["poll"]})
    assert r.get_json() == {"pending": True}
    kb = api.bot.send_message.call_args.kwargs["reply_markup"]
    assert kb.keyboard[0][0].callback_data == f"applogin:{d['code']}"


def test_login_needs_poll_secret_and_fresh_code(api, client):
    d = start_login(api, client)
    confirm_in_telegram(api, d["code"])
    # kodni bilgan, lekin ilovaning maxfiy kalitini bilmagan odam sessiyani ololmaydi
    assert client.post("/api/index?app=login_check", json={"code": d["code"], "poll": "boshqa"}).status_code == 410
    assert client.post("/api/index?app=login_check", json={"code": "yoqkod123", "poll": d["poll"]}).status_code == 410
    d2 = start_login(api, client)
    rec = api.store_get("applogin", d2["code"]); rec["t"] -= (api.APP_LOGIN_TTL + 5) * 1000
    api.store_set("applogin", d2["code"], rec)
    confirm_in_telegram(api, d2["code"])
    assert client.post("/api/index?app=login_check", json={"code": d2["code"], "poll": d2["poll"]}).status_code == 410


def test_app_token(api):
    tok = api.make_app_token(CID)
    assert api.check_app_token(tok) == str(CID)
    cid, exp, sig = tok.split(".")
    assert api.check_app_token(f"999.{exp}.{sig}") is None        # boshqa mijoz nomiga o'tkazib bo'lmaydi
    assert api.check_app_token(api.make_app_token(CID, days=-1)) is None
    assert api.check_app_token(api.make_admin_token()) is None    # admin tokeni ilova tokeni emas
    assert not api.check_admin_token(tok)


def test_order_and_history_need_login(client):
    assert client.get("/api/index?app=me").status_code == 401
    assert client.post("/api/index?app=order", json={"i": [[1001, 1]]}).status_code == 401
    assert client.post("/api/index?app=order", json={"i": [[1001, 1]]}, headers={"X-App-Token": "1.2.3"}).status_code == 401


def test_order_from_app(api, client):
    tok = login(api, client)
    pid = next(p["id"] for p in api.SEED_CATALOG if p["stock"] >= 60)
    before = api.get_catalog()[pid]
    r = client.post("/api/index?app=order", headers={"X-App-Token": tok},
                    json={"n": "Sardor", "d": "BTS", "a": "Urganch", "i": [[int(pid), 3]], "ts": 1})
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    assert body["order"]["total"] == 3 * before["retail"] and body["need_phone"] is True
    saved = api.get_order(body["order"]["id"])
    assert saved["cid"] == str(CID) and saved["src"] == "app" and saved["tg_name"] == "Sardor"
    assert api.get_catalog()[pid]["stock"] == before["stock"] - 3
    assert api.bot.send_document.called                       # adminga xabar ketdi


def test_history_shows_only_own_orders(api, client):
    mine, other = login(api, client, CID), login(api, client, 777001)
    pid = next(p["id"] for p in api.SEED_CATALOG if p["stock"] >= 60)
    client.post("/api/index?app=order", headers={"X-App-Token": mine}, json={"i": [[int(pid), 1]]})
    client.post("/api/index?app=order", headers={"X-App-Token": other}, json={"i": [[int(pid), 2]]})
    me = client.get("/api/index?app=me", headers={"X-App-Token": mine}).get_json()
    assert len(me["orders"]) == 1 and me["orders"][0]["items"][0]["q"] == 1
    assert me["orders"][0]["status_label"] == "Yangi"
    assert "cid" not in me["orders"][0] and "note" not in me["orders"][0]   # ichki maydonlar chiqmaydi


def test_out_of_stock_order_is_refused(api, client):
    tok = login(api, client)
    pid = api.SEED_CATALOG[0]["id"]
    api.get_catalog(); api.store_set("stock", pid, 0)
    r = client.post("/api/index?app=order", headers={"X-App-Token": tok}, json={"i": [[int(pid), 5]]})
    assert r.status_code == 409 and api.store_all("orders2") == {}
