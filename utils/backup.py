import os
import shutil
from datetime import datetime

from config import Config


def backup_database() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(Config.BACKUP_DIR, f"backup_{timestamp}.db")

    shutil.copy(Config.DB_PATH, backup_path)


def list_backups() -> list[str]:
    return sorted(os.listdir(Config.BACKUP_DIR), reverse=True)


def restore_db(backup_file: str) -> None:
    backup_path = os.path.join(Config.BACKUP_DIR, backup_file)
    shutil.copy(backup_path, Config.DB_PATH)


def remove_backup(backup_file: str):
    backup_path = os.path.join(Config.BACKUP_DIR, backup_file)
    os.remove(backup_path)
