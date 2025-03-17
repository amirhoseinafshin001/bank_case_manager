from flask import Blueprint
from flask import render_template
from flask import request

from services.case_service import filter_cases
from schemas.case_schemas import CaseResponseSchema

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/search", methods=["GET"])
def search_cases():
    filters = {key: value for key, value in request.args.items() if value}
    cases = filter_cases(**filters)
    cases_data = [CaseResponseSchema.model_validate(case) for case in cases]
    return render_template("search_cases.html", cases=cases)
