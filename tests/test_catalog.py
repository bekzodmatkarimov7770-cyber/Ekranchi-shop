import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Manba narx ro'yxatida nomi bo'sh kelgan mahsulotlar: nomi aniqlangach admin paneldan to'ldirib, bu yerdan o'chiring.
KNOWN_NAMELESS = {"1300"}


def test_seed_file_is_valid():
    seed = json.loads((ROOT / "catalog.seed.json").read_text(encoding="utf-8"))
    assert len(seed) > 100
    ids = [str(p["id"]) for p in seed]
    assert len(ids) == len(set(ids)), "ID lar takrorlanmasligi kerak"
    for p in seed:
        assert p["brand"] and p["type"], p
        assert p["name"] or str(p["id"]) in KNOWN_NAMELESS, p
        assert 0 < p["wholesale"] <= p["retail"], p
        assert isinstance(p["stock"], int) and p["stock"] >= 0


def test_api_uses_the_same_seed_file(api):
    seed = json.loads((ROOT / "catalog.seed.json").read_text(encoding="utf-8"))
    assert len(api.SEED_CATALOG) == len(seed)
    assert all(isinstance(p["id"], str) for p in api.SEED_CATALOG)


def test_catalog_is_not_duplicated_in_frontend():
    # katalog nusxasi sahifaga qaytib kirib qolmasin: yagona zaxira - catalog.seed.json
    assert "productsData" not in (ROOT / "data.js").read_text(encoding="utf-8")
    assert "productsData" not in (ROOT / "market.html").read_text(encoding="utf-8")


def test_no_cost_price_hints_in_public_files():
    for name in ("data.js", "market.html", "catalog.seed.json", "api/index.py"):
        assert "tannarx" not in (ROOT / name).read_text(encoding="utf-8").lower(), name


def test_catalog_seeds_database_once(api):
    cat = api.get_catalog()
    assert len(cat) == len(api.SEED_CATALOG)
    first = api.SEED_CATALOG[0]
    assert cat[first["id"]]["stock"] == first["stock"]
    # admin o'zgartirgan narx keyingi so'rovda seed bilan ustidan yozilmaydi
    api.store_set("catalog", first["id"], {**api.store_get("catalog", first["id"]), "retail": 999000})
    api._catalog_version_ok = False
    assert api.get_catalog()[first["id"]]["retail"] == 999000


def test_empty_seed_never_wipes_database(api, monkeypatch):
    api.get_catalog()
    api.store_set("meta", "catalog_version", "eski")
    monkeypatch.setattr(api, "SEED_CATALOG", [])
    api._catalog_version_ok = False
    assert len(api.get_catalog()) > 100


def test_price_version_updates_prices_but_keeps_stock(api, monkeypatch):
    api.get_catalog()
    pid = api.SEED_CATALOG[0]["id"]
    api.stock_add(pid, -10)
    left = api.get_catalog()[pid]["stock"]
    api.store_set("catalog", pid, {**api.store_get("catalog", pid), "retail": 1, "wholesale": 1})
    monkeypatch.setattr(api, "PRICE_VERSION", "yangi-narx")
    api._catalog_version_ok = False
    p = api.get_catalog()[pid]
    assert (p["retail"], p["wholesale"]) == (api.SEED_CATALOG[0]["retail"], api.SEED_CATALOG[0]["wholesale"])
    assert p["stock"] == left


def test_public_catalog_endpoint(api, client):
    pid = api.SEED_CATALOG[0]["id"]
    api.get_catalog()
    api.store_set("catalog", pid, {**api.store_get("catalog", pid), "active": False})
    r = client.get("/api/index?catalog=1")
    assert r.status_code == 200
    body = r.get_json()
    assert body["wholesale_min"] == api.WHOLESALE_MIN
    ids = {p["id"] for p in body["products"]}
    assert pid not in ids, "yashirilgan mahsulot mijozga ko'rinmasligi kerak"
    assert set(body["products"][0]) <= {"id", "brand", "type", "name", "retail", "wholesale", "stock", "img"}


def test_new_seed_products_are_added_without_touching_others(api):
    api.get_catalog()
    first, last = api.SEED_CATALOG[0], api.SEED_CATALOG[-1]
    api.stock_add(first["id"], -3)
    left = api.get_catalog()[first["id"]]["stock"]
    # bazada hali yo'q mahsulotni taqlid qilamiz
    if api.REDIS_URL:
        api._redis("HDEL", "catalog", last["id"]); api._redis("HDEL", "stock", last["id"])
    else:
        c = api._file_load("catalog"); c.pop(last["id"], None); api._file_save("catalog", c)
        st = api._file_load("stock"); st.pop(last["id"], None); api._file_save("stock", st)
    assert last["id"] not in api.store_all("catalog")
    api.store_set("catalog", first["id"], {**api.store_get("catalog", first["id"]), "retail": 999000})
    cat = api.get_catalog()
    assert cat[first["id"]]["retail"] == 999000, "admin narxi saqlanishi kerak"
    assert cat[last["id"]]["stock"] == last["stock"]
    assert cat[last["id"]]["retail"] == last["retail"]
    assert cat[first["id"]]["stock"] == left, "eski qoldiq o'zgarmasligi kerak"
