import time
from collections import defaultdict, deque

# In-process join-burst detector. State resets on restart; per-group enablement is persistent.
_JOIN_LIMIT = 5
_WINDOW_SECONDS = 10
_RAID_SECONDS = 300
_joins = defaultdict(deque)
_raid_until = {}


def register_join(chat_id: int, joined_count: int = 1) -> bool:
    now = time.monotonic()
    events = _joins[chat_id]
    while events and now - events[0] > _WINDOW_SECONDS:
        events.popleft()
    for _ in range(max(1, joined_count)):
        events.append(now)
    if len(events) >= _JOIN_LIMIT:
        _raid_until[chat_id] = now + _RAID_SECONDS
    return is_raid_active(chat_id)


def is_raid_active(chat_id: int) -> bool:
    until = _raid_until.get(chat_id, 0)
    if until <= time.monotonic():
        _raid_until.pop(chat_id, None)
        return False
    return True
