from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from services.case_service import get_case
from services.case_service import create_case
from services.case_service import update_case
from services.referral_service import create_referral
from schemas.case_schemas import CaseCreateSchema
from schemas.case_schemas import CaseUpdateSchema
from schemas.case_schemas import CaseResponseSchema
from schemas.referral_schemas import ReferralCreateSchema
from schemas import ValidationError
from utils.logger import logger


cases_bp = Blueprint("cases", __name__, url_prefix="/cases")


@cases_bp.route("/new", methods=["GET", "POST"])
def create_case_view():
    if request.method == "POST":
        try:
            form = request.form.to_dict()
            form["region"] = int(form["region"])
            data = CaseCreateSchema(**form)
            tracking_number = create_case(**data.model_dump())

            if tracking_number:
                flash("Case created successfully!", "success")
                return redirect(url_for("cases.case_detail", case_id=tracking_number))
            else:
                flash("Failed to create case.", "error")
        except Exception as e:
            logger.error(f"endpoint create_case_view: {e}")
            flash(f"Error: {e}", "error")

    return render_template("create_case.html")


@cases_bp.route("/<int:case_id>", methods=["GET", "POST"])
def case_detail(case_id):
    case = get_case(case_id)
    if not case:
        flash("Case not found", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        try:
            data = CaseUpdateSchema(**request.form)
            success = update_case(case_id, **data.model_dump())

            if success:
                flash("Case updated successfully!", "success")
                return redirect(url_for("cases.case_detail", tracking_number=case_id))
            else:
                flash("Failed to update case.", "error")
        except Exception as e:
            logger.error(f"endpoint case_detail: {e}")
            flash(f"Error: {e}", "error")

    case_data = CaseResponseSchema.model_validate(case)
    return render_template("case_detail.html", case=case_data)


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
        return redirect(url_for("cases.case_detail", case_id=case_id))
