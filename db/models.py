from enum import Enum
from typing import List
from datetime import datetime
from datetime import UTC
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime



class RegionCode(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EXCELLENT = 8 # by convention

class CaseType(Enum):
    FACILITY = "تسهیلات"
    APPRAISAL = "ارزیابی"
    REDEMPTION = "فک رهن"

class CollateralType(Enum):
    PROPERTY = "ملک"
    CHECK = "چک"
    CASH = "نقد"

class OperationType(Enum):
    ENTRY = "ورودی"
    EVALUATION = "کارشناسی"
    APPROVAL = "مصوبه"
    MANAGER = "رئیس حوزه"
    COMMISION = "کمیسیون"
    ARCHIVING = "بایگانی"



class Base(DeclarativeBase):
    pass



class Case(Base):
    __tablename__ = "cases"
    tracking_number: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    ) # شماره پیگیری
    national_id: Mapped[str] = mapped_column(
        String(12)
    ) # شناسه ملی
    applicant: Mapped[str] = mapped_column(
        String
    ) # متقاضی
    entry_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC)
    ) # تاریخ ورود
    branch: Mapped[str] = mapped_column(
        String(4)
    ) # کد شعبه
    region: Mapped[RegionCode] = mapped_column(
        SqlEnum(RegionCode),
        nullable=True
    ) # حوزه
    case_type: Mapped[CaseType] = mapped_column(
        SqlEnum(CaseType)
    ) # نوع درخواست
    amount: Mapped[int] = mapped_column(
        Integer # divided by 1'000'000 IRR
    ) # مبلغ
    collateral: Mapped[CollateralType] = mapped_column(
        SqlEnum(CollateralType)
    ) # وثیقه
    referral_list: Mapped[List["Referral"]] = relationship(
        back_populates="case",
        lazy="selectin"
    ) # ارجاع ها

    def __repr__(self):
        return f"<case {self.tracking_number}>"


class Referral(Base):
    __tablename__ = "referrals"
    id: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid4()),
        primary_key=True,
        unique=True
    ) # شماره (مربوط به ساز و کار برنامه)
    entry_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC)
    ) # تاریخ ارجاع
    exit_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    ) # تاریخ پایان مرحله
    operator: Mapped[str] = mapped_column(
        String
    ) # کاربر (کارمند مورد ارجاع)
    operation_type: Mapped[OperationType] = mapped_column(
        SqlEnum(OperationType)
    ) # نوع عملیات
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.tracking_number")
    ) # شماره پیگیری پرونده
    case: Mapped["Case"] = relationship(
        back_populates="referral_list"
    ) # پرونده

    def __repr__(self):
        return f"<ref {self.id[:4]}, {self.case.tracking_number}>"
