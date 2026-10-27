from database import (
    get_user,
    register_user,
    add_pending_referral,
    verify_referral,
    get_referral_counts,
    get_referrals,
)
from helpers import (
    get_referral_link,
    parse_referral_parameter,
)
from config import REFERRAL_REWARD


def process_referral_start(
    user_id,
    username=None,
    first_name="",
    last_name="",
    start_parameter=None,
):
    """
    Registers a new user and records a valid referral as pending.

    No referral coins are awarded here.
    The reward is granted only after membership verification.
    """

    user_id = int(user_id)

    inviter_id = parse_referral_parameter(start_parameter)

    # Prevent self-referrals.
    if inviter_id == user_id:
        inviter_id = None

    existing_user = get_user(user_id)

    # Register the user if this is their first interaction.
    if not existing_user:
        register_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referred_by=inviter_id,
        )

        # Record the referral only if the inviter exists.
        if inviter_id is not None:
            inviter = get_user(inviter_id)

            if inviter:
                referral_added = add_pending_referral(
                    inviter_id=inviter_id,
                    referred_id=user_id,
                )

                if referral_added:
                    return {
                        "is_new_user": True,
                        "referral_started": True,
                        "inviter_id": inviter_id,
                        "referred_id": user_id,
                        "status": "pending",
                    }

        return {
            "is_new_user": True,
            "referral_started": False,
            "inviter_id": None,
            "referred_id": user_id,
            "status": "none",
        }

    # Existing users cannot generate another referral reward
    # by opening the same or another referral link.
    from database import update_user_profile

    update_user_profile(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )

    return {
        "is_new_user": False,
        "referral_started": False,
        "inviter_id": None,
        "referred_id": user_id,
        "status": "existing_user",
    }


def get_user_referral_link(bot_username, user_id):
    """Generate a user's personal referral link."""

    user = get_user(user_id)

    if not user:
        return None

    return get_referral_link(
        bot_username=bot_username,
        user_id=user_id,
    )


def get_user_referral_stats(user_id):
    """Return verified and pending referral counts."""

    counts = get_referral_counts(user_id)

    verified = counts["verified_referrals"]
    pending = counts["pending_referrals"]

    return {
        "verified_referrals": verified,
        "pending_referrals": pending,
        "total_referrals": verified + pending,
    }


def get_user_referral_history(user_id):
    """Return the user's referral history."""

    return get_referrals(user_id)


def complete_referral_verification(referred_id):
    """
    Call this only after ALL required chats have been checked
    and the referred user has successfully joined them.

    Returns the inviter and reward details when a pending referral
    is successfully verified. Returns None if there is no pending
    referral to reward.
    """

    referred_id = int(referred_id)

    user = get_user(referred_id)

    if not user:
        return None

    result = verify_referral(
        referred_id=referred_id,
        reward_amount=REFERRAL_REWARD,
    )

    return result


def get_referral_notification_details(inviter_id, referred_id):
    """
    Prepare details for the notification sent to the inviter
    when a new user starts through their referral link.
    """

    inviter_id = int(inviter_id)
    referred_id = int(referred_id)

    inviter = get_user(inviter_id)
    referred = get_user(referred_id)

    if not inviter or not referred:
        return None

    return {
        "inviter_id": inviter_id,
        "inviter_name": inviter.get("first_name") or "User",
        "referred_id": referred_id,
        "referred_name": referred.get("first_name") or "User",
        "referred_username": referred.get("username"),
        "status": "pending",
        "reward_coins": REFERRAL_REWARD,
    }


def get_referral_reward_amount():
    """Return the configured referral reward."""

    return REFERRAL_REWARD
