from typing import List

from db.database import Session
from db.models import Case
from db.models import RegionCode
from db.models import CaseType
from db.models import CollateralType
from utils.logger import logger
from utils.date_utils import jalali_to_gregorian


def create_case(
        national_id: str,
        applicant: str,
        entry_date_jalali: str,
        branch: str,
        region: int,
        case_type: str,
        amount: int,
        collateral: str
    ) -> int | None:
    try:
        entry_date = jalali_to_gregorian(entry_date_jalali)
        with Session() as session:
            case = Case(
                national_id = national_id,
                applicant = applicant,
                entry_date = entry_date,
                branch = branch,
                region = RegionCode(region),
                case_type = CaseType(case_type),
                amount=  (amount // 10000000),
                collateral = CollateralType(collateral)
            )
            session.add(case)
            session.commit()
        return case.tracking_number
    except Exception as e:
        logger.error(f"Error case_service.creat_case: {e}")
        return None


def get_case(tracking_number: int) -> Case | None:
    try:
        with Session() as session:
            return session.query(Case).filter(
                Case.tracking_number == tracking_number
            ).first()
    except Exception as e:
        logger.error(f"Error case_service.get_case: {e}")
        return None


def filter_cases(**filters) -> List[Case]:
    try:
        with Session() as session:
            cases = session.query(Case)
            if "national_id" in filters:
                cases = cases.filter(Case.national_id == filters["national_id"])
            if "applicant" in filters:
                cases = cases.filter(Case.applicant == filters["applicant"])
            if "branch" in filters:
                cases = cases.filter(Case.branch == filters["branch"])
            if "region" in filters:
                cases = cases.filter(Case.region == filters["region"])
            if "case_type" in filters:
                cases = cases.filter(Case.case_type == filters["case_type"])
            if "amount" in filters:
                cases = cases.filter(Case.amount == filters["amount"])
            if "collateral" in filters:
                cases = cases.filter(Case.collateral == filters["collateral"])
            if "date_range" in filters:
                start_jalali, end_jalali = filters["date_range"]
                start = jalali_to_gregorian(start_jalali)
                end = jalali_to_gregorian(end_jalali)
                cases = cases.filter(Case.entry_date.between(start, end))
            return cases.all()
    except Exception as e:
        logger.error(f"Error case_service.filter_cases: {e}")
        return []
