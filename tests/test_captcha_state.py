from app.handlers import group_tools


def test_expired_captcha_state_is_removed(monkeypatch):
    key = (-1001234567890, 12345)
    group_tools._pending_captchas[key] = (7, 200.0, 55)

    assert group_tools._pop_expired_captcha(*key, now=199.9) is False
    assert key in group_tools._pending_captchas

    assert group_tools._pop_expired_captcha(*key, now=200.0) is True
    assert key not in group_tools._pending_captchas
