import os
import sqlite3
import shutil
from datetime import datetime

from config import (
    DATABASE_FILE,
    BACKUP_DIR,
    TIMEZONE,
    ADMIN_IDS,
)


def create_backup():
    """
    Create a consistent SQLite database backup.
    Returns the backup path on success, otherwise None.
    """
    try:
        if not os.path.exists(DATABASE_FILE):
            print("⚠️ Database file not found. Backup skipped.")
            return None

        os.makedirs(BACKUP_DIR, exist_ok=True)

        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(
            BACKUP_DIR,
            f"giveaway_backup_{timestamp}.db",
        )

        # SQLite backup API safely copies a live database.
        source = sqlite3.connect(DATABASE_FILE)
        destination = sqlite3.connect(backup_path)

        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

        if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
            print(f"✅ Database backup created: {backup_path}")
            return backup_path

        print("❌ Backup file is empty.")
        return None

    except Exception as error:
        print(f"❌ Backup failed: {error}")
        return None


def list_backups():
    """Return available database backups, newest first."""
    try:
        if not os.path.isdir(BACKUP_DIR):
            return []

        backups = []

        for filename in os.listdir(BACKUP_DIR):
            if (
                filename.startswith("giveaway_backup_")
                and filename.endswith(".db")
            ):
                path = os.path.join(BACKUP_DIR, filename)

                if os.path.isfile(path):
                    backups.append({
                        "filename": filename,
                        "path": path,
                        "size": os.path.getsize(path),
                        "modified": os.path.getmtime(path),
                    })

        backups.sort(
            key=lambda item: item["modified"],
            reverse=True,
        )

        return backups

    except Exception as error:
        print(f"❌ Could not list backups: {error}")
        return []


def restore_backup(backup_path):
    """
    Restore a selected backup after validating the SQLite database.
    Creates a safety backup before replacing the current database.
    """
    try:
        if not backup_path or not os.path.isfile(backup_path):
            return {
                "success": False,
                "message": "❌ Selected backup file was not found.",
            }

        # Only allow files inside the configured backup directory.
        backup_real = os.path.realpath(backup_path)
        backup_dir_real = os.path.realpath(BACKUP_DIR)

        if os.path.commonpath([backup_real, backup_dir_real]) != backup_dir_real:
            return {
                "success": False,
                "message": "⛔ Invalid backup path.",
            }

        if os.path.getsize(backup_real) == 0:
            return {
                "success": False,
                "message": "❌ The selected backup file is empty.",
            }

        # Validate the selected database before restoring it.
        check_db = sqlite3.connect(backup_real)

        try:
            integrity = check_db.execute("PRAGMA integrity_check").fetchone()

            if not integrity or integrity[0] != "ok":
                return {
                    "success": False,
                    "message": "❌ Backup validation failed. Restore cancelled.",
                }

            tables = check_db.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='users'"
            ).fetchone()

            if not tables:
                return {
                    "success": False,
                    "message": "❌ Backup does not contain the users table.",
                }
        finally:
            check_db.close()

        os.makedirs(os.path.dirname(DATABASE_FILE) or ".", exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # Keep a safety copy of the current database.
        safety_backup = create_backup()

        if os.path.exists(DATABASE_FILE) and not safety_backup:
            return {
                "success": False,
                "message": (
                    "❌ Safety backup could not be created. "
                    "Restore cancelled to protect current data."
                ),
            }

        # Restore to a temporary file first.
        temporary_path = DATABASE_FILE + ".restore_tmp"

        source = sqlite3.connect(backup_real)
        destination = sqlite3.connect(temporary_path)

        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

        # Validate the restored copy before replacing the active DB.
        validation = sqlite3.connect(temporary_path)

        try:
            integrity = validation.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if not integrity or integrity[0] != "ok":
                os.remove(temporary_path)
                return {
                    "success": False,
                    "message": "❌ Restored copy failed validation.",
                }
        finally:
            validation.close()

        # Replace the database file only after successful validation.
        os.replace(temporary_path, DATABASE_FILE)

        return {
            "success": True,
            "message": (
                "✅ <b>Database Restored Successfully!</b>\n\n"
                "The selected backup has been restored."
            ),
            "safety_backup": safety_backup,
        }

    except Exception as error:
        temporary_path = DATABASE_FILE + ".restore_tmp"

        if os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass

        print(f"❌ Restore failed: {error}")

        return {
            "success": False,
            "message": "❌ Restore failed. Check the hosting logs.",
        }


async def send_backup_to_admins(bot, backup_path):
    """Send the backup file to configured admins."""
    if not backup_path or not os.path.isfile(backup_path):
        return False

    sent_count = 0

    for admin_id in ADMIN_IDS:
        try:
            with open(backup_path, "rb") as backup_file:
                await bot.send_document(
                    chat_id=admin_id,
                    document=backup_file,
                    filename=os.path.basename(backup_path),
                    caption=(
                        "🗄️ <b>SF ARMY Database Backup</b>\n\n"
                        "Your scheduled database backup is ready."
                    ),
                    parse_mode="HTML",
                )

            sent_count += 1

        except Exception as error:
            print(f"⚠️ Could not send backup to admin {admin_id}: {error}")

    return sent_count > 0


async def scheduled_backup_job(context):
    """JobQueue callback for the scheduled daily backup."""
    backup_path = create_backup()

    if backup_path:
        await send_backup_to_admins(
            context.bot,
            backup_path,
        )
