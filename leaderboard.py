from database import get_leaderboard, get_user_rank
from config import (
    LEADERBOARD_LIMIT,
    LEADERBOARD_PAGE_SIZE,
    QUALIFICATION_REFERRALS,
)


def get_leaderboard_page(page=0):
    """Return one page of leaderboard entries."""

    page = max(0, int(page))

    page_size = max(1, int(LEADERBOARD_PAGE_SIZE))
    total_limit = max(1, int(LEADERBOARD_LIMIT))

    total_pages = (total_limit + page_size - 1) // page_size
    page = min(page, total_pages - 1)

    offset = page * page_size

    remaining = total_limit - offset
    limit = min(page_size, remaining)

    users = get_leaderboard(limit=limit, offset=offset)

    entries = []

    for index, user in enumerate(users, start=offset + 1):
        verified_referrals = int(
            user.get("verified_referrals", 0) or 0
        )

        qualified = verified_referrals >= QUALIFICATION_REFERRALS

        first_name = (
            user.get("first_name") or "Unknown User"
        ).strip()

        last_name = (
            user.get("last_name") or ""
        ).strip()

        full_name = f"{first_name} {last_name}".strip()

        username = user.get("username")

        entries.append({
            "rank": index,
            "user_id": user["user_id"],
            "name": full_name,
            "username": (
                f"@{username.lstrip('@')}"
                if username
                else "Not Set"
            ),
            "coins": int(user.get("total_coins", 0) or 0),
            "verified_referrals": verified_referrals,
            "pending_referrals": int(
                user.get("pending_referrals", 0) or 0
            ),
            "qualified": qualified,
            "qualification_status": (
                "✅ Qualified"
                if qualified
                else "⏳ Not Qualified"
            ),
        })

    return {
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "entries": entries,
        "total_limit": total_limit,
    }


def format_leaderboard(page=0):
    """Create the text displayed on the leaderboard."""

    data = get_leaderboard_page(page)

    entries = data["entries"]

    if not entries:
        return (
            "🏆 <b>SF ARMY LEADERBOARD</b>\n\n"
            "No verified users are on the leaderboard yet."
        )

    lines = [
        "🏆 <b>SF ARMY LEADERBOARD</b>",
        "",
        f"📊 <b>Top {data['total_limit']} Users</b>",
        (
            f"📄 Page {data['page'] + 1}"
            f"/{data['total_pages']}"
        ),
        "",
    ]

    for user in entries:
        rank = user["rank"]

        if rank == 1:
            rank_icon = "🥇"
        elif rank == 2:
            rank_icon = "🥈"
        elif rank == 3:
            rank_icon = "🥉"
        else:
            rank_icon = f"<b>#{rank}</b>"

        name = escape_html(user["name"])
        username = escape_html(user["username"])
        user_id = user["user_id"]
        coins = user["coins"]
        referrals = user["verified_referrals"]

        if user["qualified"]:
            qualification = "✅ Qualified"
        else:
            qualification = "⏳ Not Qualified"

        lines.extend([
            (
                f"{rank_icon} <b>{name}</b>\n"
                f"   👤 {username}\n"
                f"   🆔 <code>{user_id}</code>\n"
                f"   🪙 <b>{coins:,} Coins</b>\n"
                f"   👥 Verified Referrals: {referrals}\n"
                f"   🎯 {qualification}"
            ),
            "",
        ])

    lines.extend([
        (
            f"📌 Qualification requires "
            f"{QUALIFICATION_REFERRALS} verified referrals."
        ),
        "",
        "🔄 Rankings are based on total coins.",
    ])

    return "\n".join(lines)


def escape_html(text):
    """Escape user-provided text for Telegram HTML messages."""

    text = str(text)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def get_user_leaderboard_details(user_id):
    """Return a user's current rank and qualification status."""

    rank = get_user_rank(user_id)

    data = get_leaderboard(limit=1000, offset=0)

    for user in data:
        if int(user["user_id"]) == int(user_id):
            verified_referrals = int(
                user.get("verified_referrals", 0) or 0
            )

            return {
                "rank": rank,
                "coins": int(user.get("total_coins", 0) or 0),
                "verified_referrals": verified_referrals,
                "qualified": (
                    verified_referrals >= QUALIFICATION_REFERRALS
                ),
            }

    return {
        "rank": rank,
        "coins": 0,
        "verified_referrals": 0,
        "qualified": False,
    }
