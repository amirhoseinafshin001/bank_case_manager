from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for

from utils.backup import backup_database
from utils.backup import list_backups
from utils.backup import restore_db
from utils.backup import remove_backup
from utils.excel_utils import export_all_cases_to_excel
from utils.logger import logger



backup_bp = Blueprint("backup", __name__)


@backup_bp.route("/backups")
def backup_page():
    backups = list_backups()
    return render_template("backup.html", backups=backups)


@backup_bp.route("/create_backup")
def create_backup():
    try:
        backup_database()
        flash("بکاپ با موفقیت گرفته شد.", "success")
    except Exception as e:
        logger.error(f"endpoint create_backup: {e}")
        flash("خطایی رخ داده است", "danger")
    
    finally:
        backups = list_backups()
        return redirect(url_for("backup.backup_page", backups=backups))
    

@backup_bp.route("/restore_backup/<backup_file>")
def restore_backup(backup_file):
    try:
        restore_db(backup_file)
        flash("بکاپ با موفقیت جایگزین شد.", "success")
    except Exception as e:
        logger.error(f"endpoint restore_backup: {e}")
        flash("خطایی رخ داده است", "danger")
    
    finally:
        backups = list_backups()
        return redirect(url_for("backup.backup_page", backups=backups))


@backup_bp.route("/delete_backup/<backup_file>")
def delete_backup(backup_file):
    try:
        # backup_file = request.args.get("file")
        remove_backup(backup_file)
        flash("بکاپ با موفقیت حذف شد.", "success")
    except Exception as e:
        logger.error(f"endpoint delete_backup: {e}")
        flash("خطایی رخ داده است", "danger")
    
    finally:
        backups = list_backups()
        return redirect(url_for("backup.backup_page", backups=backups))


@backup_bp.route("/excel_backup")
def excel_backup():
    export_all_cases_to_excel()
    flash("بکاپ اکسل ایجاد شد.", "success")
    backups = list_backups()
    return redirect(url_for("backup.backup_page", backups=backups))
