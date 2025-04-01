import pandas as pd
from utils.date_utils import jalali_to_gregorian
from db.models import Case, Referral
from db.database import Session



def import_cases_from_excel(file_path):
    df = pd.read_excel(file_path)

    with Session() as session:
        for _, row in df.iterrows():
            case = Case(
                applicant=row["متقاضی"],
                region=row["حوزه"],
                branch=row["کد شعبه"],
                tracking_number=row["شماره نامه"],
                entry_date=jalali_to_gregorian(row["تاریخ ورود"]),
                contract=row["عقد"],
                amount=row["مبلغ درخواست"],
                case_type=row["نوع درخواست"],
                status=row["وضعیت"]
            )
            session.add(case)
            session.flush() # 'cuz we need case id

            for stage in range(1, 16):
                user_col = f"نام کاربر یا کارشناس مرحله {stage}"
                date_col = f"تاریخ مرحله {stage}"
                desc_col = f"توضیحات مرحله {stage}"

                if pd.notna(row[user_col]):
                    referral = Referral(
                        case_id=case.id,
                        operator=row[user_col],
                        entry_date=jalali_to_gregorian(row[date_col]) if pd.notna(row[date_col]) else None,
                        notes=row[desc_col] if pd.notna(row[desc_col]) else None
                    )
                    session.add(referral)

        session.commit()
