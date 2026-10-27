from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import CHANNELS


# ==============================
# USER MAIN MENU
# ==============================

def main_menu_keyboard():
    keyboard = [
        ["👤 My Profile", "🏆 Leaderboard"],
        ["🔗 My Referral Link", "🎁 Daily Bonus"],
        ["🎟️ Redeem Code", "🎁 Rewards"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


# ==============================
# REQUIRED CHAT JOIN BUTTONS
# ==============================

def required_chats_keyboard():
    keyboard = []

    for index, channel in enumerate(CHANNELS, start=1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"Join {index}: {channel['name']}",
                url=channel["url"],
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="✅ Verify Membership",
            callback_data="verify_membership",
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# ==============================
# VERIFICATION RETRY BUTTON
# ==============================

def verification_retry_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🔄 Check Again",
                callback_data="verify_membership",
            )
        ]
    ])


# ==============================
# PROFILE KEYBOARD
# ==============================

def profile_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🔗 My Referral Link",
                callback_data="my_referral_link",
            )
        ],
        [
            InlineKeyboardButton(
                text="🎁 Rewards",
                callback_data="rewards_coming_soon",
            )
        ],
    ])


# ==============================
# LEADERBOARD PAGINATION
# ==============================

def leaderboard_keyboard(page=0, total_pages=1):
    page = max(0, int(page))
    total_pages = max(1, int(total_pages))

    keyboard = []
    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data=f"leaderboard_page:{page - 1}",
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="leaderboard_current_page",
        )
    )

    if page < total_pages - 1:
        navigation.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=f"leaderboard_page:{page + 1}",
            )
        )

    keyboard.append(navigation)

    keyboard.append([
        InlineKeyboardButton(
            text="🔄 Refresh",
            callback_data=f"leaderboard_page:{page}",
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# ==============================
# REDEEM CODE KEYBOARD
# ==============================

def redeem_code_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_redeem",
            )
        ]
    ])


# ==============================
# ADMIN MAIN PANEL
# ==============================

def admin_panel_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="📢 Broadcast",
                callback_data="admin_broadcast",
            ),
            InlineKeyboardButton(
                text="📊 Dashboard",
                callback_data="admin_dashboard",
            ),
        ],
        [
            InlineKeyboardButton(
                text="💾 Backup & Recovery",
                callback_data="admin_backup_recovery",
            ),
            InlineKeyboardButton(
                text="👥 Manage Users",
                callback_data="admin_manage_users",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🪙 Coin Management",
                callback_data="admin_coin_management",
            ),
            InlineKeyboardButton(
                text="🎟️ Redeem Code Manager",
                callback_data="admin_redeem_manager",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📂 Backup History",
                callback_data="admin_backup_history",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==============================
# ADMIN BACK BUTTON
# ==============================

def admin_back_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⬅️ Back to Admin Panel",
                callback_data="admin_panel",
            )
        ]
    ])


# ==============================
# ADMIN USER MANAGEMENT
# ==============================

def admin_user_management_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔍 Find User",
                callback_data="admin_find_user",
            )
        ],
        [
            InlineKeyboardButton(
                text="🪙 Check Balance",
                callback_data="admin_check_balance",
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="admin_panel",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==============================
# ADMIN COIN MANAGEMENT
# ==============================

def admin_coin_management_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Add Coins",
                callback_data="admin_add_coins",
            ),
            InlineKeyboardButton(
                text="➖ Deduct Coins",
                callback_data="admin_deduct_coins",
            ),
        ],
        [
            InlineKeyboardButton(
                text="💰 Check Balance",
                callback_data="admin_check_balance",
            )
        ],
        [
            InlineKeyboardButton(
                text="📜 Transaction History",
                callback_data="admin_transaction_history",
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="admin_panel",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==============================
# ADMIN REDEEM CODE MANAGER
# ==============================

def admin_redeem_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Add Code",
                callback_data="admin_add_redeem_code",
            ),
            InlineKeyboardButton(
                text="🗑️ Delete Code",
                callback_data="admin_delete_redeem_code",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Available Codes",
                callback_data="admin_available_codes",
            )
        ],
        [
            InlineKeyboardButton(
                text="📜 Redemption History",
                callback_data="admin_redeem_history",
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="admin_panel",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==============================
# BACKUP & RECOVERY MENU
# ==============================

def backup_recovery_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="💾 Create Backup",
                callback_data="admin_create_backup",
            )
        ],
        [
            InlineKeyboardButton(
                text="♻️ Restore Backup",
                callback_data="admin_restore_backup",
            )
        ],
        [
            InlineKeyboardButton(
                text="📂 View Backup History",
                callback_data="admin_backup_history",
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="admin_panel",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==============================
# CONFIRMATION KEYBOARD
# ==============================

def confirmation_keyboard(action):
    action = str(action)

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="✅ Confirm",
                callback_data=f"confirm:{action}",
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_action",
            ),
        ]
    ])


# ==============================
# CANCEL KEYBOARD
# ==============================

def cancel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_action",
            )
        ]
    ])
