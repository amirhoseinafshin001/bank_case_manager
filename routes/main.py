from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for

from services.case_service import filter_cases
from schemas.case_schemas import CaseResponseSchema
from utils.logger import logger
from config import Config



main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/search", methods=["GET"])
def search_cases():
    filters = {key: value for key, value in request.args.items() if value}
    cases = filter_cases(**filters)
    cases_data = [CaseResponseSchema.model_validate(case) for case in cases]
    return render_template("search_cases.html", cases=cases_data)


@main_bp.route("/logs")
def view_logs():
    try:
        with open(f'{Config.LOGS_DIR}app.log', 'r', encoding='utf-8') as log_file:
            logs = log_file.readlines()
    except FileNotFoundError:
        logs = ["فایل لاگ یافت نشد!"]
    except Exception as e:
        logs = [f"خطا در خواندن فایل لاگ: {str(e)}"]
    
    return render_template("logs.html", logs=logs)


@main_bp.route("/clear_logs", methods=["POST"])
def clear_logs():
    try:
        with open(f'{Config.LOGS_DIR}app.log', 'w', encoding='utf-8') as log_file:
            log_file.write("")
        flash("لاگ‌ها با موفقیت پاک شدند.", "success")
    except Exception as e:
        logger.error(f"خطا در پاک کردن لاگ‌ها: {e}")
        flash("خطا در پاک کردن لاگ‌ها", "danger")
    
    return redirect(url_for("main.view_logs"))
