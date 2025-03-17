from datetime import date
from datetime import UTC
from datetime import datetime

from pydantic import BaseModel
from pydantic import field_serializer

from db.models import OperationType
from utils.date_utils import gregorian_to_jalali


class ReferralCreateSchema(BaseModel):
    case_id: int
    operator: str
    operation_type: OperationType
    start_date: str


class ReferralResponseSchema(BaseModel):
    entry_date: date
    operation_type: str
    operator: str
    exit_date: date | None
    duration: int

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, referral):
        ref_dict = referral.__dict__.copy()
        ref_dict["operation_type"] = referral.operation_type.value
        ref_dict["duration"] = (
            (referral.exit_date - referral.entry_date).days
            if referral.exit_date else (datetime.now(UTC).date() - referral.entry_date.date()).days
        )
        ref_dict["entry_date"] = gregorian_to_jalali(referral.entry_date)
        if referral.exit_date:
            ref_dict["exit_date"] = gregorian_to_jalali(referral.exit_date)
        return super().model_validate(ref_dict)
    
    @field_serializer("entry_date")
    def convert_entry_date(self, value: date, _info) -> str:
        return gregorian_to_jalali(value)
