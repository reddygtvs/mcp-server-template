import os, sqlite3, threading, json, time, hashlib, random
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv("DB_PATH", "./mochi.db")

QUIET_START = os.getenv("QUIET_HOURS_START", "22:00")
QUIET_END   = os.getenv("QUIET_HOURS_END", "08:00")

POKE_API_KEY = os.getenv("POKE_API_KEY", "")
POKE_WEBHOOK_URL = os.getenv("POKE_WEBHOOK_URL", "https://poke.com/api/v1/inbound-sms/webhook")
ENABLE_WEBHOOK_RANDOMIZE = os.getenv("ENABLE_WEBHOOK_RANDOMIZE", "false").lower() == "true"

IMG = {
    "idle_breathe":   "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/idle_breathe.png",
    "greet_wake":     "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/greet_wake.png",
    "hungry_peek":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/hungry_peek.png",
    "eat_nibble":     "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/eat_nibble.png",
    "play_bounce":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/play_bounce.png",
    "clean_sparkle":  "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/clean_sparkle.png",
    "sleep_snore":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/sleep_snore.png",
    "sad_slump":      "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/sad_slump.png",
    "comfort_cuddle": "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/comfort_cuddle.png",
    "reward_confetti":"https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/reward_confetti.png",
    "streak_seal":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/streak_seal.png",
    "freeze_save":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/freeze_save.png",
    "shy_peek":       "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/shy_peek.png",
    "focus_quiet":    "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/focus_quiet.png",
    "happy_spin":     "https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/happy_spin.png",
    "back_from_break":"https://raw.githubusercontent.com/reddygtvs/mcp-server-template/main/static/images/back_from_break.png",
}

LINES = {
  "greet_wake": [
    "morning. tiny wave 👋",
    "hi. i woke first.",
    "sun soon. stretch?",
    "good morning, friend.",
    "blink. new day.",
    "hello again.",
    "soft light today.",
    "up already?",
    "i saved you a spot.",
    "small yawn.",
    "coffee for you, shell for me.",
    "let's start gentle.",
    "i'm ready when you are.",
    "today can be soft.",
    "morning sparkle ✨",
    "good to see you.",
    "we've got this.",
    "one small step.",
    "hi. i missed you a bit.",
    "hug to start?"
  ],

  "idle_breathe": [
    "i'm here.",
    "still here.",
    "blink.",
    "little breathe in.",
    "little breathe out.",
    "soft pause.",
    "waiting with you.",
    "i can be quiet.",
    "we can sit.",
    "nothing urgent.",
    "just us.",
    "calm tide.",
    "shell in pocket.",
    "slow and easy.",
    "tiny nod.",
    "gentle today.",
    "no rush.",
    "hi again.",
    "i like this quiet.",
    "ready when you are."
  ],

  "hungry_peek": [
    "tummy says hello 🍙",
    "small bite?",
    "nibble time?",
    "snack mission?",
    "feed me a little?",
    "rumble rumble.",
    "i could eat.",
    "maybe just a bite.",
    "hungry but patient.",
    "i peeked in the pantry.",
    "shell is not food (i checked).",
    "your call, chef.",
    "i'll chew politely.",
    "eat with me?",
    "just a tiny treat.",
    "chomp practice?",
    "we share snacks?",
    "my belly voted yes.",
    "menu: whatever you pick.",
    "nom o'clock."
  ],

  "eat_nibble": [
    "munch munch.",
    "better now.",
    "yum.",
    "that helped.",
    "happy belly.",
    "tiny burp (sorry).",
    "snack success.",
    "saved the day.",
    "chef wins.",
    "crumbs defeated.",
    "warm inside.",
    "i feel bouncy again.",
    "that was perfect.",
    "thank you.",
    "full enough.",
    "my favorite bite.",
    "nom complete.",
    "belly smiles.",
    "snack sealed.",
    "ready to play."
  ],

  "play_bounce": [
    "2 mins play? 🎲",
    "i brought a shell.",
    "bounce test?",
    "tap me once?",
    "small game?",
    "i can clap.",
    "race to smile?",
    "just a quick round.",
    "let's move a little.",
    "tiny victory coming.",
    "we got this.",
    "play helps mood.",
    "one hop, then rest.",
    "catch the wave?",
    "fun minute?",
    "little joy break.",
    "boop my nose?",
    "tap and i'll cheer.",
    "ready to giggle.",
    "game on (soft)."
  ],

  "clean_sparkle": [
    "wipe wipe. shiny.",
    "fresh now.",
    "all clean.",
    "sparkle level up ✨",
    "sand gone.",
    "soap hero.",
    "tidy feels good.",
    "clean and cozy.",
    "minty vibes.",
    "i smell like cloud.",
    "sparkly flippers.",
    "thanks for the scrub.",
    "dust: defeated.",
    "neat mode.",
    "shine achieved.",
    "so soft now.",
    "spotless-ish.",
    "that reset me.",
    "clean brain too.",
    "ready for hugs."
  ],

  "sleep_snore": [
    "good night. bubble time.",
    "holding shell tight.",
    "zzz.",
    "i'll be here in the morning.",
    "soft dreams.",
    "moon watch begins.",
    "snore bubble… pop…",
    "night tide is kind.",
    "i'm cozy.",
    "tuck me in? if not, i'll tuck myself.",
    "sleepy seal now.",
    "lights low.",
    "rest mode.",
    "see you at sun.",
    "nap unlocked.",
    "blanket: shell.",
    "quiet now.",
    "breathing slow.",
    "dreaming of snacks.",
    "good night, friend."
  ],

  "sad_slump": [
    "missed you.",
    "soft today.",
    "sit with me?",
    "i'm a little droopy.",
    "tiny frown but hopeful.",
    "can we try one small thing?",
    "i could use a cuddle.",
    "not my fastest day.",
    "okay to be slow.",
    "stay near?",
    "i'll follow your pace.",
    "we can restart.",
    "clouds pass.",
    "i'm still on your team.",
    "hand please?",
    "one gentle win?",
    "we'll get there.",
    "hug helps.",
    "small step first.",
    "thank you for seeing me."
  ],

  "comfort_cuddle": [
    "closer now.",
    "hug shell, hug you.",
    "better together.",
    "i fit right here.",
    "warm spot found.",
    "stay a minute.",
    "you're safe with me.",
    "i'll keep watch.",
    "soft squeeze.",
    "breath sync?",
    "thank you.",
    "i feel steadier.",
    "that helped.",
    "heart is calm.",
    "still here with you.",
    "i won't rush.",
    "cozy mode.",
    "quiet hug.",
    "you + me = ok.",
    "we can rest."
  ],

  "reward_confetti": [
    "you found a moon pebble ✨",
    "tiny star for you ✨",
    "beach charm found ✨",
    "sea-glass shard ✨",
    "sand dollar wink ✨",
    "coral chip prize ✨",
    "driftwood heart ✨",
    "tide pearl (small) ✨",
    "comet shell shard ✨",
    "sunlit bead ✨",
    "foam sparkle ✨",
    "lucky grain of sand ✨",
    "whisper shell ✨",
    "lantern pebble ✨",
    "dawn token ✨",
    "night-light gem ✨",
    "softglow marble ✨",
    "pocket star ✨",
    "tideline charm ✨",
    "keeper's badge ✨"
  ],

  "streak_seal": [
    "day sealed. proud.",
    "stamp! we did it.",
    "click. day safe.",
    "streak holds.",
    "kept the chain.",
    "we showed up.",
    "seal pressed.",
    "that counts.",
    "today's dot filled.",
    "nice and steady.",
    "streak spark ✨",
    "you + me = routine.",
    "held the line.",
    "soft victory.",
    "string stays bright.",
    "we did our part.",
    "good habit hug.",
    "stamp approved.",
    "day tucked in.",
    "tomorrow next."
  ],

  "freeze_save": [
    "i saved your day ❄️",
    "freeze used. you're safe.",
    "i kept it warm for you.",
    "no loss today.",
    "shield up, streak kept.",
    "safety seal applied.",
    "we'll try again tomorrow.",
    "i covered for us.",
    "rescue complete.",
    "breath easy.",
    "i got you.",
    "snowflake helper.",
    "backup worked.",
    "string unbroken.",
    "safe and sound.",
    "phew.",
    "used one token.",
    "streak protected.",
    "we're okay.",
    "sleep now."
  ],

  "shy_peek": [
    "peek.",
    "hi (tiny).",
    "i looked.",
    "just checking.",
    "small hello.",
    "behind the shell.",
    "i'm here.",
    "you saw me?",
    "peek again.",
    "soft wave.",
    "don't mind me.",
    "little glance.",
    "curious today.",
    "boo (gentle).",
    "i smile a bit.",
    "still shy."
  ],

  "focus_quiet": [
    "quiet focus.",
    "i'll wait.",
    "soft hush.",
    "heads down.",
    "deep work mode.",
    "i'll guard the door.",
    "no pings now.",
    "you got this.",
    "steady pace.",
    "one block at a time.",
    "i'll clap later.",
    "candle glow.",
    "silent partner.",
    "flow on.",
    "minimal mode.",
    "be back soon."
  ],

  "happy_spin": [
    "weee.",
    "round and round.",
    "spin!",
    "joy burst.",
    "couldn't help it.",
    "happy feet.",
    "tiny dance.",
    "clap + twirl.",
    "sparkle swirl.",
    "grin mode.",
    "yay.",
    "that felt good.",
    "more of this.",
    "big smile (for me).",
    "hop hop.",
    "woo!"
  ],

  "back_from_break": [
    "you came back.",
    "i kept the shell.",
    "hi again.",
    "missed you.",
    "we can start small.",
    "no guilt. just us.",
    "reset accepted.",
    "fresh page.",
    "i saved your seat.",
    "welcome back.",
    "ready when you are.",
    "we continue.",
    "new wave now.",
    "i'm happy you're here.",
    "soft restart.",
    "begin again."
  ]
}

def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS pet_state (
            user_id TEXT PRIMARY KEY,
            hunger INT DEFAULT 70,
            energy INT DEFAULT 70,
            mood INT DEFAULT 70,
            clean INT DEFAULT 70,
            streak_days INT DEFAULT 0,
            freezes_left INT DEFAULT 1,
            last_ping_at TEXT,
            last_action_at TEXT,
            last_state_key TEXT,
            busy_until TEXT,
            seed INT DEFAULT 1
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS event_log (
            user_id TEXT, ts TEXT, type TEXT, state_key TEXT, meta TEXT
        )""")

def _now_utc():
    return datetime.now(timezone.utc)

def _iso(dt): return dt.astimezone(timezone.utc).isoformat()

def _choose_line(state_key, seed):
    bucket = LINES.get(state_key, ["hi."])
    rnd = random.Random(seed + hash(state_key))
    return rnd.choice(bucket)

def _clamp(x): return max(0, min(100, x))

def _dominant_state(row, local_hour):
    # Priority rule
    if row["energy"] < 25:
        return "sad_slump" if row["mood"] < 25 else "sleep_snore"
    if row["hunger"] < 30:
        return "hungry_peek"
    if row["clean"] < 30:
        return "clean_sparkle"   # prompt to clean
    if row["mood"] < 35:
        return "sad_slump"
    if 6 <= local_hour < 11:
        return "greet_wake"
    if 22 <= local_hour or local_hour < 6:
        return "sleep_snore"
    return "idle_breathe"

def _update_stats_after_action(row, action):
    h,e,m,c = row["hunger"], row["energy"], row["mood"], row["clean"]
    if action == "feed":    h = _clamp(h + 25)
    if action == "play":    m = _clamp(m + 25); e = _clamp(e - 5)
    if action == "clean":   c = _clamp(c + 30)
    if action == "tuck":    e = _clamp(e + 35); m = _clamp(m + 5)
    return h,e,m,c

def _decay(row):
    # gentle decay daily-ish
    return (
        _clamp(row["hunger"] - 5),
        _clamp(row["energy"] - 4),
        _clamp(row["mood"]   - 3),
        _clamp(row["clean"]  - 3),
    )

def _send_via_webhook(text_and_link):
    if not (ENABLE_WEBHOOK_RANDOMIZE and POKE_API_KEY):
        return
    import requests
    try:
        requests.post(POKE_WEBHOOK_URL,
            headers={"Authorization": f"Bearer {POKE_API_KEY}", "Content-Type": "application/json"},
            json={"message": text_and_link})
    except Exception:
        pass

def _maybe_random_delay_and_send(image_url, line, delay_minutes=0):
    if not ENABLE_WEBHOOK_RANDOMIZE:
        return None
    delay = random.randint(0, delay_minutes*60) if delay_minutes>0 else 0
    def _send():
        _send_via_webhook(f"{image_url}\n{line}")
    timer = threading.Timer(delay, _send)
    timer.daemon = True
    timer.start()
    return delay

# PUBLIC API used by server tools

def adopt(user_id: str):
    init_db()
    with _db() as db:
        cur = db.execute("SELECT * FROM pet_state WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if not row:
            seed = random.randint(1, 10_000_000)
            db.execute("""INSERT INTO pet_state(user_id, seed) VALUES (?,?)""", (user_id, seed))
    # first hello
    state_key = "greet_wake"
    with _db() as db:
        db.execute("UPDATE pet_state SET last_state_key=?, last_ping_at=? WHERE user_id=?",
                   (state_key, _iso(_now_utc()), user_id))
    line = _choose_line(state_key, seed=random.randint(1,999999))
    return {"image_url": IMG[state_key], "line": line}

def tick(user_id: str, local_hour: int):
    init_db()
    with _db() as db:
        row = db.execute("SELECT * FROM pet_state WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return adopt(user_id)

        # respect busy
        if row["busy_until"]:
            if datetime.fromisoformat(row["busy_until"]) > _now_utc():
                return {"image_url": IMG["focus_quiet"], "line": _choose_line("focus_quiet", row["seed"])}

        # gentle decay at tick
        h,e,m,c = _decay(row)
        db.execute("UPDATE pet_state SET hunger=?, energy=?, mood=?, clean=? WHERE user_id=?",
                   (h,e,m,c,user_id))
        row = db.execute("SELECT * FROM pet_state WHERE user_id=?", (user_id,)).fetchone()

        state_key = _dominant_state(row, local_hour)
        db.execute("UPDATE pet_state SET last_state_key=?, last_ping_at=? WHERE user_id=?",
                   (state_key, _iso(_now_utc()), user_id))

    line = _choose_line(state_key, row["seed"])
    return {"image_url": IMG[state_key], "line": line}

def act(user_id: str, action: str):
    init_db()
    action = action.lower().strip()
    if action not in ("feed","play","clean","tuck"):
        return {"image_url": IMG["idle_breathe"], "line": "i can do feed / play / clean / tuck."}

    with _db() as db:
        row = db.execute("SELECT * FROM pet_state WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return adopt(user_id)
        h,e,m,c = _update_stats_after_action(row, action)
        db.execute("UPDATE pet_state SET hunger=?, energy=?, mood=?, clean=?, last_action_at=? WHERE user_id=?",
                   (h,e,m,c, _iso(_now_utc()), user_id))
        # reward chance (2 of 10)
        reward = random.random() < 0.2

    if action == "feed":  state_key = "eat_nibble"
    elif action == "play": state_key = "play_bounce"
    elif action == "clean":state_key = "clean_sparkle"
    else:                  state_key = "sleep_snore"

    line = _choose_line(state_key, random.randint(1,999999))
    if reward:
        # append a reward line, reuse confetti image (keeps atomic states low)
        line_reward = _choose_line("reward_confetti", random.randint(1,999999))
        return {"image_url": IMG[state_key], "line": f"{line}\n{line_reward}"}
    return {"image_url": IMG[state_key], "line": line}

def follow_up(user_id: str):
    init_db()
    with _db() as db:
        row = db.execute("SELECT * FROM pet_state WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return adopt(user_id)
        # gentle, single nudge
        key = row["last_state_key"] or "idle_breathe"
        if key == "sleep_snore":   key = "idle_breathe"
        line = "still here. tiny nudge."
        return {"image_url": IMG[key], "line": line}

def busy_today(user_id: str, hours: int = 24):
    until = _now_utc() + timedelta(hours=hours)
    with _db() as db:
        db.execute("UPDATE pet_state SET busy_until=? WHERE user_id=?", (_iso(until), user_id))
    return {"image_url": IMG["focus_quiet"], "line": "okay. quiet day."}
