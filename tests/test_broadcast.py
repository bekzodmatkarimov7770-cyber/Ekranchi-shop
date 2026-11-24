"""/hammaga: admin xabari tanlangan mijozlarga bir marta yetib borishi."""
import types


def msg(chat_id, text=None, message_id=5):
    return types.SimpleNamespace(chat=types.SimpleNamespace(id=chat_id), text=text, message_id=message_id,
                                 from_user=types.SimpleNamespace(id=chat_id))


def cb(data, chat_id=777):
    return types.SimpleNamespace(id="cb1", data=data, from_user=types.SimpleNamespace(id=chat_id),
                                 message=types.SimpleNamespace(chat=types.SimpleNamespace(id=chat_id), message_id=9))


def seed_users(api):
    api.store_set("users", 1, {"phone": "+1", "role": "Optom"})
    api.store_set("users", 2, {"phone": "+2", "role": "Chakana"})
    api.store_set("users", 3, {"phone": "+3", "role": None})
    api.store_set("users", 777, {"phone": "+7", "role": "Optom"})   # admin o'ziga yubormaydi


def sent_to(api):
    return sorted(c.args[0] for c in api.bot.copy_message.call_args_list if c.args[0] != 777)


def test_only_admin_can_start(api):
    api.handle_broadcast_start(msg(42, "/hammaga"))
    assert api.bc_state() == {}
    assert not api._bc_waiting(msg(42, "salom"))


def test_broadcast_to_optom_only_once(api):
    seed_users(api)
    api.handle_broadcast_start(msg(777, "/hammaga"))
    assert api._bc_waiting(msg(777, "Yangi partiya keldi"))
    assert not api._bc_waiting(msg(777, "/stat"))
    api.handle_broadcast_draft(msg(777, "Yangi partiya keldi", message_id=55))
    assert api.bc_state()["step"] == "ready"
    api.handle_broadcast_choice(cb("bc:Optom"))
    assert sent_to(api) == [1]
    assert api.bc_state()["step"] == "done"
    api.handle_broadcast_choice(cb("bc:Optom"))          # Telegram qayta yuborsa ham takrorlanmaydi
    assert sent_to(api) == [1]


def test_broadcast_all_counts_failures(api):
    seed_users(api)
    def copy(uid, frm, mid):
        if uid == 2:
            raise Exception("Forbidden: bot was blocked by the user")
    api.bot.copy_message.side_effect = copy
    api.handle_broadcast_start(msg(777, "/hammaga"))
    api.handle_broadcast_draft(msg(777, "Aksiya", message_id=56))
    api.handle_broadcast_choice(cb("bc:all"))
    s = api.bc_state()
    assert (s["ok"], s["fail"], s["step"]) == (2, 1, "done")


def test_pause_and_resume(api, monkeypatch):
    seed_users(api)
    monkeypatch.setattr(api, "BC_BUDGET", -1)             # birinchi chaqiruvda vaqt darhol tugaydi
    api.handle_broadcast_start(msg(777, "/hammaga"))
    api.handle_broadcast_draft(msg(777, "Aksiya", message_id=57))
    api.handle_broadcast_choice(cb("bc:all"))
    assert api.bc_state()["step"] == "paused" and sent_to(api) == []
    monkeypatch.setattr(api, "BC_BUDGET", 40)
    api.handle_broadcast_choice(cb("bc:resume"))
    assert api.bc_state()["step"] == "done" and sent_to(api) == [1, 2, 3]


def test_non_admin_cannot_press(api):
    seed_users(api)
    api.bc_save({"step": "ready", "from": 777, "msg": 1})
    api.handle_broadcast_choice(cb("bc:all", chat_id=42))
    assert sent_to(api) == [] and api.bc_state()["step"] == "ready"
