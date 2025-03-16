"""
Run the tests one by one and clear the database each time.
"""
import pytest
from datetime import datetime

from db.database import Session
from db.models import Case, Referral, RegionCode, CaseType, CollateralType, OperationType
from services.case_service import create_case, get_case, filter_cases
from services.referral_service import create_referral, get_operator_referrals, end_referral
from utils.date_utils import jalali_to_gregorian


@pytest.fixture(scope="function")
def setup_database():
    session = Session()
    session.expire_on_commit = False
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_create_case(setup_database):
    case_id = create_case(
        national_id="123456789012",
        applicant="Ali Ahmadi",
        entry_date_jalali="1402-12-25",
        branch="1101",
        region=RegionCode.THREE,
        case_type=CaseType.FACILITY,
        amount=50000000,
        collateral=CollateralType.PROPERTY
    )

    assert case_id is not None

    session = setup_database
    case = session.query(Case).filter_by(tracking_number=case_id).first()
    
    assert case is not None
    assert case.national_id == "123456789012"
    assert case.applicant == "Ali Ahmadi"
    assert case.entry_date.date() == jalali_to_gregorian("1402-12-25")
    assert case.branch == "1101"
    assert case.region == RegionCode.THREE
    assert case.case_type == CaseType.FACILITY
    assert case.amount == 5
    assert case.collateral == CollateralType.PROPERTY


def test_get_case(setup_database):
    session = setup_database
    case = Case(
        national_id="987654321098",
        applicant="Sara Mohammadi",
        entry_date=datetime.utcnow(),
        branch="2202",
        region=RegionCode.SEVEN,
        case_type=CaseType.APPRAISAL,
        amount=10_000_000,
        collateral=CollateralType.CHECK
    )
    session.add(case)
    session.commit()

    fetched_case = get_case(case.tracking_number)
    
    assert fetched_case is not None
    assert fetched_case.national_id == "987654321098"
    assert fetched_case.applicant == "Sara Mohammadi"
    assert fetched_case.branch == "2202"
    assert fetched_case.region == RegionCode.SEVEN
    assert fetched_case.case_type == CaseType.APPRAISAL
    assert fetched_case.amount == 10_000_000
    assert fetched_case.collateral == CollateralType.CHECK


def test_filter_cases(setup_database):
    session = setup_database
    case_1 = Case(
        national_id="111111111111",
        applicant="Hasan Rezai",
        entry_date=datetime.utcnow(),
        branch="3303",
        region=RegionCode.FIVE,
        case_type=CaseType.REDEMPTION,
        amount=20_000_000,
        collateral=CollateralType.CASH
    )
    case_2 = Case(
        national_id="222222222222",
        applicant="Mehdi Gholami",
        entry_date=datetime.utcnow(),
        branch="4404",
        region=RegionCode.THREE,
        case_type=CaseType.FACILITY,
        amount=30_000_000,
        collateral=CollateralType.PROPERTY
    )
    session.add_all([case_1, case_2])
    session.commit()

    filtered_cases = filter_cases(region=RegionCode.FIVE)
    
    assert len(filtered_cases) == 1
    assert filtered_cases[0].national_id == "111111111111"
    assert filtered_cases[0].case_type == CaseType.REDEMPTION

    filtered_cases = filter_cases(collateral=CollateralType.PROPERTY)
    
    assert len(filtered_cases) == 1
    assert filtered_cases[0].national_id == "222222222222"


def test_create_referral(setup_database):
    session = setup_database
    case = Case(
        national_id="333333333333",
        applicant="Naser Karimi",
        entry_date=datetime.utcnow(),
        branch="5505",
        region=RegionCode.ONE,
        case_type=CaseType.APPRAISAL,
        amount=40_000_000,
        collateral=CollateralType.CHECK
    )
    session.add(case)
    session.flush()
    session.refresh(case)  # این خط را اضافه کنید

    result = create_referral(
        case_id=case.tracking_number,
        operator="Ali Manager",
        operation_type=OperationType.MANAGER,
        date_jalali="1402-12-25"
    )
    
    assert result is True

    referral = session.query(Referral).filter_by(case_id=case.tracking_number).first()
    
    assert referral is not None
    assert referral.operator == "Ali Manager"
    assert referral.operation_type == OperationType.MANAGER
    assert referral.entry_date.date() == jalali_to_gregorian("1402-12-25")


def test_get_operator_referrals(setup_database):
    session = setup_database
    case = Case(
        national_id="444444444444",
        applicant="Hamed Alavi",
        entry_date=datetime.utcnow(),
        branch="6606",
        region=RegionCode.TWO,
        case_type=CaseType.FACILITY,
        amount=15_000_000,
        collateral=CollateralType.CASH
    )
    session.add(case)
    session.commit()

    referral = Referral(
        entry_date=datetime.utcnow(),
        operator="Reza Employee",
        operation_type=OperationType.APPROVAL,
        case_id=case.tracking_number
    )
    session.add(referral)
    session.commit()

    operator_refs = get_operator_referrals("Reza Employee")
    
    assert len(operator_refs) == 1
    assert operator_refs[0].operator == "Reza Employee"
    assert operator_refs[0].operation_type == OperationType.APPROVAL


def test_end_referral(setup_database):
    session = setup_database
    case = Case(
        national_id="555555555555",
        applicant="Saeed Rahimi",
        entry_date=datetime.utcnow(),
        branch="7707",
        region=RegionCode.EXCELLENT,
        case_type=CaseType.REDEMPTION,
        amount=60_000_000,
        collateral=CollateralType.PROPERTY
    )
    session.add(case)
    session.commit()

    referral = Referral(
        entry_date=datetime.utcnow(),
        operator="Sina Supervisor",
        operation_type=OperationType.ARCHIVING,
        case_id=case.tracking_number
    )
    session.add(referral)
    session.commit()

    result = end_referral(case.tracking_number, jalali_end_date="1402-11-30")
    
    assert result is True

    updated_referral = session.query(Referral).filter_by(case_id=case.tracking_number).first()
    
    assert updated_referral.exit_date.date() == jalali_to_gregorian("1402-11-30")
