import sqlite3
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from config import DATABASE_FILE, TIMEZONE


IST = TIMEZONE if isinstance(TIMEZONE, ZoneInfo) else ZoneInfo("Asia/Kolkata")


def current_time():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def current_date():
    return datetime.now(IST).strftime("%Y-%m-%d")


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_FILE, timeout=30)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_db() as db:
        db.execute("PRAGMA journal_mode = WAL")

        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT NOT NULL DEFAULT '',
                last_name TEXT NOT NULL DEFAULT '',
                total_coins INTEGER NOT NULL DEFAULT 0
                    CHECK(total_coins >= 0),
                verified INTEGER NOT NULL DEFAULT 0,
                joined_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                welcome_bonus_claimed INTEGER NOT NULL DEFAULT 0,
                daily_bonus_date TEXT,
                referred_by INTEGER,
                FOREIGN KEY (referred_by)
                    REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'verified', 'rejected')),
                started_at TEXT NOT NULL,
                verified_at TEXT,
                reward_coins INTEGER NOT NULL DEFAULT 0,
                reward_paid INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (inviter_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id),
                CHECK(inviter_id != referred_id)
            );

            CREATE INDEX IF NOT EXISTS idx_referrals_inviter
                ON referrals(inviter_id);

            CREATE INDEX IF NOT EXISTS idx_referrals_status
                ON referrals(status);

            CREATE TABLE IF NOT EXISTS required_chat_checks (
                user_id INTEGER NOT NULL,
                chat_id TEXT NOT NULL,
                is_member INTEGER NOT NULL DEFAULT 0,
                checked_at TEXT NOT NULL,
                PRIMARY KEY (user_id, chat_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS coin_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                admin_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE INDEX IF NOT EXISTS idx_transactions_user
                ON coin_transactions(user_id, id DESC);

            CREATE TABLE IF NOT EXISTS redeem_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE COLLATE NOCASE,
                reward_coins INTEGER NOT NULL DEFAULT 0
                    CHECK(reward_coins >= 0),
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active', 'disabled')),
                added_by INTEGER,
                added_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS redeem_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                redeemed_at TEXT NOT NULL,
                UNIQUE(code_id, user_id),
                FOREIGN KEY (code_id) REFERENCES redeem_codes(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE INDEX IF NOT EXISTS idx_redeem_history_user
                ON redeem_history(user_id);

            CREATE TABLE IF NOT EXISTS bot_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by INTEGER,
                status TEXT NOT NULL DEFAULT 'success',
                notes TEXT NOT NULL DEFAULT ''
            );
        """)


def register_user(user_id, username=None, first_name="", last_name="",
                 referred_by=None):
    """
    Registers a user or updates their profile.

    Returns:
        True  - new user created
        False - user already existed
    """

    user_id = int(user_id)

    if referred_by is not None:
        referred_by = int(referred_by)

        if referred_by == user_id:
            referred_by = None

    now = current_time()

    with get_db() as db:
        existing = db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if existing:
            db.execute("""
                UPDATE users
                SET username = ?,
                    first_name = ?,
                    last_name = ?,
                    last_seen = ?
                WHERE user_id = ?
            """, (username, first_name or "", last_name or "", now, user_id))

            return False

        if referred_by is not None:
            inviter_exists = db.execute(
                "SELECT user_id FROM users WHERE user_id = ?",
                (referred_by,)
            ).fetchone()

            if not inviter_exists:
                referred_by = None

        db.execute("""
            INSERT INTO users (
                user_id, username, first_name, last_name,
                total_coins, verified, joined_at, last_seen,
                welcome_bonus_claimed, daily_bonus_date, referred_by
            )
            VALUES (?, ?, ?, ?, 0, 0, ?, ?, 0, NULL, ?)
        """, (
            user_id, username, first_name or "", last_name or "",
            now, now, referred_by
        ))

        return True


def get_user(user_id):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (int(user_id),)
        ).fetchone()

        return dict(row) if row else None


def get_all_users():
    with get_db() as db:
        rows = db.execute("""
            SELECT *
            FROM users
            ORDER BY joined_at ASC
        """).fetchall()

        return [dict(row) for row in rows]


def update_user_profile(user_id, username=None, first_name="",
                        last_name=""):
    with get_db() as db:
        db.execute("""
            UPDATE users
            SET username = ?,
                first_name = ?,
                last_name = ?,
                last_seen = ?
            WHERE user_id = ?
        """, (
            username, first_name or "", last_name or "",
            current_time(), int(user_id)
        ))

        return db.total_changes > 0


def mark_user_verified(user_id):
    with get_db() as db:
        db.execute("""
            UPDATE users
            SET verified = 1,
                last_seen = ?
            WHERE user_id = ?
        """, (current_time(), int(user_id)))

        return db.total_changes > 0


def has_claimed_welcome_bonus(user_id):
    with get_db() as db:
        row = db.execute("""
            SELECT welcome_bonus_claimed
            FROM users
            WHERE user_id = ?
        """, (int(user_id),)).fetchone()

        return bool(row and row["welcome_bonus_claimed"])


def claim_welcome_bonus(user_id, amount):
    """
    Atomically grants the welcome bonus once.
    The calling code must verify required-chat membership first.
    """

    user_id = int(user_id)
    amount = int(amount)

    if amount < 0:
        raise ValueError("Bonus amount cannot be negative.")

    now = current_time()

    with get_db() as db:
        user = db.execute("""
            SELECT verified, welcome_bonus_claimed
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        if not user or not user["verified"]:
            return False

        if user["welcome_bonus_claimed"]:
            return False

        db.execute("""
            UPDATE users
            SET total_coins = total_coins + ?,
                welcome_bonus_claimed = 1
            WHERE user_id = ?
              AND verified = 1
              AND welcome_bonus_claimed = 0
        """, (amount, user_id))

        if db.execute("SELECT changes()").fetchone()[0] != 1:
            return False

        db.execute("""
            INSERT INTO coin_transactions (
                user_id, amount, transaction_type,
                description, created_at
            )
            VALUES (?, ?, 'welcome_bonus', ?, ?)
        """, (user_id, amount, "Welcome bonus", now))

        return True


def claim_daily_bonus(user_id, amount):
    """
    Grants the daily bonus once per India calendar day.
    The calling code must verify required-chat membership first.
    """

    user_id = int(user_id)
    amount = int(amount)
    today = current_date()

    if amount < 0:
        raise ValueError("Bonus amount cannot be negative.")

    with get_db() as db:
        user = db.execute("""
            SELECT verified, daily_bonus_date
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        if not user or not user["verified"]:
            return False

        if user["daily_bonus_date"] == today:
            return False

        db.execute("""
            UPDATE users
            SET total_coins = total_coins + ?,
                daily_bonus_date = ?
            WHERE user_id = ?
              AND verified = 1
              AND (
                  daily_bonus_date IS NULL
                  OR daily_bonus_date != ?
              )
        """, (amount, today, user_id, today))

        if db.execute("SELECT changes()").fetchone()[0] != 1:
            return False

        db.execute("""
            INSERT INTO coin_transactions (
                user_id, amount, transaction_type,
                description, created_at
            )
            VALUES (?, ?, 'daily_bonus', ?, ?)
        """, (user_id, amount, "Daily bonus", current_time()))

        return True


def add_pending_referral(inviter_id, referred_id):
    """
    Creates a pending referral.
    No coins are awarded at this stage.
    """

    inviter_id = int(inviter_id)
    referred_id = int(referred_id)

    if inviter_id == referred_id:
        return False

    now = current_time()

    with get_db() as db:
        inviter = db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (inviter_id,)
        ).fetchone()

        referred = db.execute(
            "SELECT user_id, referred_by FROM users WHERE user_id = ?",
            (referred_id,)
        ).fetchone()

        if not inviter or not referred:
            return False

        if referred["referred_by"] not in (None, inviter_id):
            return False

        existing = db.execute("""
            SELECT id
            FROM referrals
            WHERE referred_id = ?
        """, (referred_id,)).fetchone()

        if existing:
            return False

        db.execute("""
            INSERT INTO referrals (
                inviter_id, referred_id, status,
                started_at, reward_coins, reward_paid
            )
            VALUES (?, ?, 'pending', ?, 0, 0)
        """, (inviter_id, referred_id, now))

        db.execute("""
            UPDATE users
            SET referred_by = ?
            WHERE user_id = ?
              AND referred_by IS NULL
        """, (inviter_id, referred_id))

        return True


def verify_referral(referred_id, reward_amount):
    """
    Marks a referral verified and pays the inviter once.

    Call this only after the referred user has joined every required
    chat and their membership has been checked successfully.
    """

    referred_id = int(referred_id)
    reward_amount = int(reward_amount)

    if reward_amount < 0:
        raise ValueError("Reward amount cannot be negative.")

    now = current_time()

    with get_db() as db:
        referral = db.execute("""
            SELECT *
            FROM referrals
            WHERE referred_id = ?
        """, (referred_id,)).fetchone()

        if not referral or referral["status"] != "pending":
            return None

        inviter_id = referral["inviter_id"]

        referred_user = db.execute("""
            SELECT verified
            FROM users
            WHERE user_id = ?
        """, (referred_id,)).fetchone()

        inviter = db.execute("""
            SELECT user_id
            FROM users
            WHERE user_id = ?
        """, (inviter_id,)).fetchone()

        if not referred_user or not inviter:
            return None

        db.execute("""
            UPDATE users
            SET verified = 1,
                last_seen = ?
            WHERE user_id = ?
        """, (now, referred_id))

        db.execute("""
            UPDATE referrals
            SET status = 'verified',
                verified_at = ?,
                reward_coins = ?,
                reward_paid = 1
            WHERE id = ?
              AND status = 'pending'
        """, (now, reward_amount, referral["id"]))

        db.execute("""
            UPDATE users
            SET total_coins = total_coins + ?
            WHERE user_id = ?
        """, (reward_amount, inviter_id))

        db.execute("""
            INSERT INTO coin_transactions (
                user_id, amount, transaction_type,
                description, created_at
            )
            VALUES (?, ?, 'referral_reward', ?, ?)
        """, (
            inviter_id,
            reward_amount,
            f"Verified referral: {referred_id}",
            now
        ))

        return {
            "inviter_id": inviter_id,
            "referred_id": referred_id,
            "reward_coins": reward_amount,
            "verified_at": now
        }


def get_referral_counts(user_id):
    with get_db() as db:
        row = db.execute("""
            SELECT
                COUNT(CASE WHEN status = 'verified' THEN 1 END)
                    AS verified_referrals,
                COUNT(CASE WHEN status = 'pending' THEN 1 END)
                    AS pending_referrals
            FROM referrals
            WHERE inviter_id = ?
        """, (int(user_id),)).fetchone()

        return {
            "verified_referrals": row["verified_referrals"],
            "pending_referrals": row["pending_referrals"]
        }


def get_referrals(user_id):
    with get_db() as db:
        rows = db.execute("""
            SELECT
                r.*,
                u.username,
                u.first_name,
                u.last_name
            FROM referrals AS r
            JOIN users AS u ON u.user_id = r.referred_id
            WHERE r.inviter_id = ?
            ORDER BY r.started_at DESC
        """, (int(user_id),)).fetchall()

        return [dict(row) for row in rows]


def get_leaderboard(limit=50, offset=0):
    limit = max(1, min(int(limit), 1000))
    offset = max(0, int(offset))

    with get_db() as db:
        rows = db.execute("""
            SELECT
                u.user_id,
                u.username,
                u.first_name,
                u.last_name,
                u.total_coins,
                COUNT(
                    CASE WHEN r.status = 'verified' THEN 1 END
                ) AS verified_referrals,
                COUNT(
                    CASE WHEN r.status = 'pending' THEN 1 END
                ) AS pending_referrals
            FROM users AS u
            LEFT JOIN referrals AS r ON r.inviter_id = u.user_id
            WHERE u.verified = 1
            GROUP BY u.user_id
            ORDER BY u.total_coins DESC,
                     verified_referrals DESC,
                     u.user_id ASC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        return [dict(row) for row in rows]


def get_user_rank(user_id):
    user_id = int(user_id)

    with get_db() as db:
        user = db.execute("""
            SELECT total_coins
            FROM users
            WHERE user_id = ? AND verified = 1
        """, (user_id,)).fetchone()

        if not user:
            return None

        rank = db.execute("""
            SELECT COUNT(*) + 1 AS rank
            FROM users
            WHERE verified = 1
              AND total_coins > ?
        """, (user["total_coins"],)).fetchone()

        return rank["rank"]


def add_coins(user_id, amount, description="Admin coin addition",
              admin_id=None, transaction_type="admin_add"):
    user_id = int(user_id)
    amount = int(amount)

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_db() as db:
        user = db.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            return False

        db.execute("""
            UPDATE users
            SET total_coins = total_coins + ?
            WHERE user_id = ?
        """, (amount, user_id))

        db.execute("""
            INSERT INTO coin_transactions (
                user_id, amount, transaction_type,
                description, admin_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, amount, transaction_type,
            description, admin_id, current_time()
        ))

        return True


def deduct_coins(user_id, amount, description="Admin coin deduction",
                 admin_id=None, transaction_type="admin_deduct"):
    user_id = int(user_id)
    amount = int(amount)

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_db() as db:
        db.execute("""
            UPDATE users
            SET total_coins = total_coins - ?
            WHERE user_id = ?
              AND total_coins >= ?
        """, (amount, user_id, amount))

        if db.execute("SELECT changes()").fetchone()[0] != 1:
            return False

        db.execute("""
            INSERT INTO coin_transactions (
                user_id, amount, transaction_type,
                description, admin_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, -amount, transaction_type,
            description, admin_id, current_time()
        ))

        return True


def get_coin_transactions(user_id, limit=50):
    limit = max(1, min(int(limit), 1000))

    with get_db() as db:
        rows = db.execute("""
            SELECT *
            FROM coin_transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (int(user_id), limit)).fetchall()

        return [dict(row) for row in rows]


def add_redeem_code(code, reward_coins=0, added_by=None):
    code = str(code).strip()
    reward_coins = int(reward_coins)

    if not code:
        return False

    if reward_coins < 0:
        raise ValueError("Reward amount cannot be negative.")

    try:
        with get_db() as db:
            db.execute("""
                INSERT INTO redeem_codes (
                    code, reward_coins, status, added_by, added_at
                )
                VALUES (?, ?, 'active', ?, ?)
            """, (code, reward_coins, added_by, current_time()))

        return True

    except sqlite3.IntegrityError:
        return False


def delete_redeem_code(code):
    with get_db() as db:
        cursor = db.execute("""
            DELETE FROM redeem_codes
            WHERE code = ?
        """, (str(code).strip(),))

        return cursor.rowcount > 0


def get_redeem_codes(status=None):
    with get_db() as db:
        if status:
            rows = db.execute("""
                SELECT *
                FROM redeem_codes
                WHERE status = ?
                ORDER BY id DESC
            """, (status,)).fetchall()
        else:
            rows = db.execute("""
                SELECT *
                FROM redeem_codes
                ORDER BY id DESC
            """).fetchall()

        return [dict(row) for row in rows]


def redeem_code(user_id, code):
    """
    Atomically redeems a code and awards its configured coin value.
    A user cannot redeem the same code twice.
    """

    user_id = int(user_id)
    code = str(code).strip()
    now = current_time()

    with get_db() as db:
        user = db.execute("""
            SELECT verified
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        if not user or not user["verified"]:
            return {"success": False, "reason": "user_not_verified"}

        redeem = db.execute("""
            SELECT *
            FROM redeem_codes
            WHERE code = ? COLLATE NOCASE
              AND status = 'active'
        """, (code,)).fetchone()

        if not redeem:
            return {"success": False, "reason": "invalid_or_inactive_code"}

        already_redeemed = db.execute("""
            SELECT id
            FROM redeem_history
            WHERE code_id = ? AND user_id = ?
        """, (redeem["id"], user_id)).fetchone()

        if already_redeemed:
            return {"success": False, "reason": "already_redeemed"}

        try:
            db.execute("""
                INSERT INTO redeem_history (code_id, user_id, redeemed_at)
                VALUES (?, ?, ?)
            """, (redeem["id"], user_id, now))
        except sqlite3.IntegrityError:
            return {"success": False, "reason": "already_redeemed"}

        reward = redeem["reward_coins"]

        if reward > 0:
            db.execute("""
                UPDATE users
                SET total_coins = total_coins + ?
                WHERE user_id = ?
            """, (reward, user_id))

            db.execute("""
                INSERT INTO coin_transactions (
                    user_id, amount, transaction_type,
                    description, created_at
                )
                VALUES (?, ?, 'redeem_code', ?, ?)
            """, (
                user_id, reward,
                f"Redeemed code: {code}", now
            ))

        return {
            "success": True,
            "code": redeem["code"],
            "reward_coins": reward,
            "redeemed_at": now
        }


def get_redeem_history(user_id=None):
    with get_db() as db:
        if user_id is not None:
            rows = db.execute("""
                SELECT
                    h.*,
                    c.code,
                    c.reward_coins,
                    u.username,
                    u.first_name,
                    u.last_name
                FROM redeem_history AS h
                JOIN redeem_codes AS c ON c.id = h.code_id
                JOIN users AS u ON u.user_id = h.user_id
                WHERE h.user_id = ?
                ORDER BY h.id DESC
            """, (int(user_id),)).fetchall()
        else:
            rows = db.execute("""
                SELECT
                    h.*,
                    c.code,
                    c.reward_coins,
                    u.username,
                    u.first_name,
                    u.last_name
                FROM redeem_history AS h
                JOIN redeem_codes AS c ON c.id = h.code_id
                JOIN users AS u ON u.user_id = h.user_id
                ORDER BY h.id DESC
            """).fetchall()

        return [dict(row) for row in rows]


def set_setting(key, value):
    with get_db() as db:
        db.execute("""
            INSERT INTO bot_settings (setting_key, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_key)
            DO UPDATE SET setting_value = excluded.setting_value
        """, (str(key), str(value)))


def get_setting(key, default=None):
    with get_db() as db:
        row = db.execute("""
            SELECT setting_value
            FROM bot_settings
            WHERE setting_key = ?
        """, (str(key),)).fetchone()

        return row["setting_value"] if row else default


def record_chat_check(user_id, chat_id, is_member):
    with get_db() as db:
        db.execute("""
            INSERT INTO required_chat_checks (
                user_id, chat_id, is_member, checked_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, chat_id)
            DO UPDATE SET
                is_member = excluded.is_member,
                checked_at = excluded.checked_at
        """, (
            int(user_id), str(chat_id),
            1 if is_member else 0, current_time()
        ))


def get_chat_checks(user_id):
    with get_db() as db:
        rows = db.execute("""
            SELECT *
            FROM required_chat_checks
            WHERE user_id = ?
            ORDER BY chat_id
        """, (int(user_id),)).fetchall()

        return [dict(row) for row in rows]


def record_backup(backup_path, backup_type="automatic",
                  created_by=None, status="success", notes=""):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO backup_history (
                backup_path, backup_type, created_at,
                created_by, status, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(backup_path), str(backup_type), current_time(),
            created_by, str(status), str(notes)
        ))

        return cursor.lastrowid


def get_backup_history(limit=20):
    limit = max(1, min(int(limit), 1000))

    with get_db() as db:
        rows = db.execute("""
            SELECT *
            FROM backup_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def get_dashboard_stats():
    with get_db() as db:
        users = db.execute("""
            SELECT
                COUNT(*) AS total_users,
                SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END)
                    AS verified_users,
                COALESCE(SUM(total_coins), 0) AS total_coins
            FROM users
        """).fetchone()

        referrals = db.execute("""
            SELECT
                COUNT(CASE WHEN status = 'verified' THEN 1 END)
                    AS verified_referrals,
                COUNT(CASE WHEN status = 'pending' THEN 1 END)
                    AS pending_referrals
            FROM referrals
        """).fetchone()

        codes = db.execute("""
            SELECT
                COUNT(*) AS total_codes,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END)
                    AS active_codes
            FROM redeem_codes
        """).fetchone()

        redemptions = db.execute("""
            SELECT COUNT(*) AS total_redemptions
            FROM redeem_history
        """).fetchone()

        return {
            "total_users": users["total_users"] or 0,
            "verified_users": users["verified_users"] or 0,
            "total_coins": users["total_coins"] or 0,
            "verified_referrals": referrals["verified_referrals"] or 0,
            "pending_referrals": referrals["pending_referrals"] or 0,
            "total_codes": codes["total_codes"] or 0,
            "active_codes": codes["active_codes"] or 0,
            "total_redemptions": redemptions["total_redemptions"] or 0
        }


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
