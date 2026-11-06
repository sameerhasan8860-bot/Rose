from app.services import anti_raid


def test_join_burst_activates_and_expires(monkeypatch):
    chat_id = -987654321
    anti_raid._joins.pop(chat_id, None)
    anti_raid._raid_until.pop(chat_id, None)
    clock = [100.0]
    monkeypatch.setattr(anti_raid.time, "monotonic", lambda: clock[0])

    for _ in range(4):
        assert anti_raid.register_join(chat_id) is False

    assert anti_raid.register_join(chat_id) is True
    assert anti_raid.is_raid_active(chat_id) is True

    clock[0] += 301
    assert anti_raid.is_raid_active(chat_id) is False
    anti_raid._joins.pop(chat_id, None)
    anti_raid._raid_until.pop(chat_id, None)
