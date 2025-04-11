from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import send_file
from flask import abort

from services.case_service import get_case
from services.case_service import create_case
from services.case_service import update_case
from services.referral_service import create_referral
from services.referral_service import end_referral
from services.referral_service import get_case_referrals
from schemas.case_schemas import CaseCreateSchema
from schemas.case_schemas import CaseUpdateSchema
from schemas.case_schemas import CaseResponseSchema
from schemas.referral_schemas import ReferralCreateSchema
from schemas import ValidationError
from utils.logger import logger
from utils.excel_utils import export_excel
from utils.date_utils import gregorian_to_jalali



cases_bp = Blueprint("cases", __name__, url_prefix="/cases")


@cases_bp.route("/new", methods=["GET", "POST"])
def create_case_view():
    if request.method == "POST":
        try:
            form = request.form.to_dict()
            form["region"] = int(form["region"])
            form["amount"] = int(form["amount"].replace("'", ""))
            
            data = CaseCreateSchema(**form)
            tracking_number = create_case(**data.model_dump())

            if tracking_number:
                flash("پرونده با موفقیت ساخته شد!", "success")
                return redirect(url_for("cases.case_detail", case_id=tracking_number, today=gregorian_to_jalali(datetime.now())))
            else:
                flash("خطا در ساخت پرونده.", "error")
        except Exception as e:
            logger.error(f"endpoint create_case_view: {e}")
            flash(f"Error: {e}", "error")

    return render_template("create_case.html")


@cases_bp.route("/<int:case_id>", methods=["GET", "POST"])
def case_detail(case_id):
    case = get_case(case_id)
    if not case:
        abort(404)

    if request.method == "POST":
        try:
            data = CaseUpdateSchema(**request.form)
            success = update_case(case_id, **data.model_dump())

            if success:
                flash("پرونده با موفقیت ویرایش شد!", "success")
                return redirect(url_for("cases.case_detail", tracking_number=case_id, today=gregorian_to_jalali(datetime.now())))
            else:
                flash("ویرایش پرونده ناموفق بود.", "error")
        except Exception as e:
            logger.error(f"endpoint case_detail: {e}")
            flash(f"Error: {e}", "error")

    case_data = CaseResponseSchema.model_validate(case)
    return render_template("case_detail.html", case=case_data, today=gregorian_to_jalali(datetime.now()))


@cases_bp.route("/<int:case_id>/referrals", methods=["POST"])
def create_case_referral(case_id):
    try:
        data = request.form.to_dict()
        data["case_id"] = case_id

        referral_data = ReferralCreateSchema.model_validate(data)
        referral = create_referral(**referral_data.model_dump())
        if referral:
            flash("ارجاع با موفقیت ثبت شد", "success")
        else:
            print(0)
            raise Exception()

    except ValidationError as e:
        logger.error(f"endpoint create_case_referral: (ValidationError from schemas) {e}")
        flash("داده‌های ورودی نامعتبر است", "danger")

    except Exception as e:
        logger.error(f"endpoint create_case_referral: {e}")
        flash("خطایی رخ داده است", "danger")
    
    finally:
        return redirect(url_for("cases.case_detail", case_id=case_id, today=gregorian_to_jalali(datetime.now())))


@cases_bp.route("/case/<int:case_id>/close", methods=["GET", "POST"])
def close_last_referral(case_id):
    try:
        last_referral = get_case_referrals(case_id)[-1]

        if not last_referral:
            flash("هیچ ارجاعی برای این پرونده ثبت نشده است.", "warning")
        elif last_referral.exit_date:
            flash("آخرین ارجاع این پرونده قبلاً بسته شده است.", "info")

        elif end_referral(case_id):
            flash("پرونده با موفقیت بسته شد.", "success")
        else:
            flash("خطایی رخ داده است", "danger")

    except Exception as e:
        logger.error(f"endpoint create_case_referral: {e}")
        flash("خطایی رخ داده است", "danger")

    finally:
        return redirect(url_for('cases.case_detail', case_id=case_id, today=gregorian_to_jalali(datetime.now())))


@cases_bp.route("/export_case/<int:tracking_number>/excel")
def export_case_excel(tracking_number):
    output, filename = export_excel(tracking_number)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
