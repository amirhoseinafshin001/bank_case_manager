from typing import List
from datetime import datetime
from datetime import time

from sqlalchemy import func
from sqlalchemy.orm import aliased

from db.database import Session
from db.models import Case
from db.models import Referral
from db.models import RegionCode
from db.models import CaseType
from db.models import CollateralType
from utils.logger import logger
from utils.date_utils import jalali_to_gregorian


def create_case(
        national_id: str,
        applicant: str,
        entry_date: str,
        branch: str,
        region: int,
        case_type: str,
        amount: int,
        collateral: str
    ) -> int | None:
    try:
        entry_date = jalali_to_gregorian(entry_date)
        with Session() as session:
            case = Case(
                national_id = national_id,
                applicant = applicant,
                entry_date = entry_date,
                branch = branch,
                region = RegionCode(region),
                case_type = CaseType(case_type),
                amount=  (amount // 1_000_000),
                collateral = CollateralType(collateral)
            )
            session.add(case)
            session.commit()
            session.refresh(case)
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
                region = RegionCode(int(filters["region"]))
                cases = cases.filter(Case.region == region)
            if "case_type" in filters:
                cases = cases.filter(Case.case_type == filters["case_type"])
            if "amount" in filters:
                cases = cases.filter(Case.amount == filters["amount"])
            if "collateral" in filters:
                cases = cases.filter(Case.collateral == filters["collateral"])
            if "start_date" in filters and "end_date" in filters:
                start_jalali, end_jalali = filters["start_date"], filters["end_date"]
                start = jalali_to_gregorian(start_jalali)
                end = jalali_to_gregorian(end_jalali)
                start = datetime.combine(start, time.min)
                end = datetime.combine(end, time.max)
                cases = cases.filter(Case.entry_date.between(start, end))
            
            if "last_operator" in filters or "last_operation_type" in filters:
                latest_ref = aliased(Referral)
                subquery = (
                    session.query(
                        Referral.case_id, 
                        func.max(Referral.entry_date).label("latest_date")
                    )
                    .group_by(Referral.case_id)
                    .subquery()
                )
                cases = cases.outerjoin(
                    latest_ref, 
                    (latest_ref.case_id == Case.tracking_number) & 
                    (latest_ref.entry_date == subquery.c.latest_date)
                ).outerjoin(subquery, subquery.c.case_id == Case.tracking_number)
            if "last_operator" in filters:
                cases = cases.filter(
                    latest_ref.operator == filters["last_operator"],
                    latest_ref.exit_date == None
                )
            if "last_operation_type" in filters:
                cases = cases.filter(
                    latest_ref.operation_type == filters["last_operation_type"],
                    latest_ref.exit_date == None
                )

            if not filters:
                cases = (
                    cases.outerjoin(Referral)
                    .group_by(Case.tracking_number)
                    .order_by(func.max(Referral.entry_date))
                )

            return cases.all()
    except Exception as e:
        logger.error(f"Error case_service.filter_cases: {e}")
        return []


def update_case(case: Case) -> bool:
    try:
        with Session() as session:
            session.merge(case)  # update the case (idk, gpt said that)
            session.commit()
        return True
    except Exception as e:
        logger.error(f"Error case_service.update_case: {e}")
        return False
