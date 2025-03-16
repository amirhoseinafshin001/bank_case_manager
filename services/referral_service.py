from datetime import datetime
from datetime import UTC
from typing import List

from db.database import Session
from db.models import Referral
from db.models import Case
from utils.date_utils import jalali_to_gregorian
from utils.logger import logger


def create_referral(
        case_id: int, # tracking_number
        operator: str,
        operation_type: str,
        date_jalali: str = None,
    ) -> bool:
    try:
        date = jalali_to_gregorian(date_jalali)
        with Session() as session:
            ref = Referral(
                entry_date = date,
                operator = operator,
                operation_type = operation_type,
                case_id = case_id
            )
            session.add(ref)
            session.commit()
            session.refresh(ref)
        return True
    except Exception as e:
        logger.error(f"Error referral_service.creat_referral: {e}")
        return False


def get_operator_referrals(operator: str) -> List[Referral]:
    try:
        with Session() as session:
            return session.query(Referral).filter(
                Referral.operator == operator,
                Referral.exit_date == None
            ).all()
    except Exception as e:
        logger.error(f"Error referral_service.get_operator_referrals: {e}")
        return []


def end_referral(
        case_id: int,
        jalali_end_date: str = None
    ) -> bool:
    end_date = jalali_to_gregorian(jalali_end_date) if jalali_end_date else datetime.now(UTC)
    try:
        with Session() as session:
            session.query(Referral).filter(
                Referral.case_id == case_id,
                Referral.exit_date == None
            ).update({
                "exit_date": end_date
            })
            session.commit()
        return True
    except Exception as e:
        logger.error(f"Error referral_service.end_referral: {e}")
        return False
