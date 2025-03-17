from typing import Optional
from datetime import date

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer

from db.models import CaseType
from db.models import CollateralType
from db.models import RegionCode
from db.models import Case
from utils.date_utils import gregorian_to_jalali
from schemas.referral_schemas import ReferralResponseSchema


class CaseCreateSchema(BaseModel):
    "validate input from user"
    national_id: str = Field(min_length=10, max_length=12)
    applicant: str
    entry_date: str
    branch: str
    region: RegionCode
    case_type: CaseType
    amount: int = Field(gt=0)
    collateral: CollateralType


class CaseUpdateSchema(BaseModel):
    "validate and parse input from user"
    applicant: Optional[str] = None
    branch: Optional[str] = None
    region: Optional[RegionCode] = None
    case_type: Optional[CaseType] = None
    amount: Optional[int] = Field(None, gt=0)
    collateral: Optional[CollateralType] = None


class CaseResponseSchema(BaseModel):
    "parse DB model to user's expected response"
    tracking_number: int
    national_id: str
    applicant: str
    entry_date: date
    branch: str
    region: int
    case_type: str
    amount: int
    collateral: str
    referrals: list[ReferralResponseSchema]

    @field_serializer("entry_date")
    def convert_entry_date(self, value: date, _info) -> str:
        return gregorian_to_jalali(value)

    @classmethod
    def model_validate(cls, case: Case): # idk, gpt said that.
        case_dict = case.__dict__.copy()
        case_dict["region"] = case.region.value
        case_dict["case_type"] = case.case_type.value
        case_dict["collateral"] = case.collateral.value
        case_dict["referrals"] = [
            ReferralResponseSchema.model_validate(ref) for ref in case.referral_list
        ]
        case_dict["entry_date"] = gregorian_to_jalali(case.entry_date)
        return super().model_validate(case_dict)

    class Config:
        # to get the values directly from SQLAlchemy models.
        from_attributes = True
