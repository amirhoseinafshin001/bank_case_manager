from datetime import datetime
from datetime import UTC

from io import BytesIO
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles import Alignment

from db.database import Session
from db.models import Case
from db.models import OperationType
from utils.date_utils import gregorian_to_jalali
from services.case_service import get_case



def export_excel(t_num: int):
    case = get_case(t_num)
    if case is None:
        return False

    wb = Workbook()
    ws = wb.active
    ws.title = f"پرونده {t_num}"
    ws.sheet_view.rightToLeft = True

    headers = [
        "شماره پیگیری",
        "شناسه ملی",
        "متقاضی",
        "تاریخ ورود",
        "کد شعبه",
        "حوزه",
        "نوع درخواست",
        "مبلغ",
        "وثیقه"
    ]
    ws.append(headers)

    jalali_date = gregorian_to_jalali(case.entry_date)

    row = [
        case.tracking_number,
        case.national_id,
        case.applicant,
        jalali_date,
        case.branch,
        case.region.name if case.region else "",
        case.case_type.value,
        case.amount * 1_000_000,
        case.collateral.value
    ]
    ws.append(row)

    ws.append([])
    ws.append(["تاریخ ارجاع", "تاریخ پایان", "کاربر", "نوع عملیات"])
    
    for referral in case.referral_list:
        entry_date = gregorian_to_jalali(referral.entry_date)
        exit_date = gregorian_to_jalali(referral.exit_date) if referral.exit_date else ""
        
        ws.append([
            entry_date,
            exit_date,
            referral.operator,
            referral.operation_type.value
        ])

    persian_font = Font(name='B Nazanin', size=12, bold=True)
    right_alignment = Alignment(horizontal='right', vertical='center')
    for row in ws.iter_rows():
        for cell in row:
            cell.font = persian_font
            cell.alignment = right_alignment
        
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"case_{t_num} at {jalali_date.replace('/', '-')}.xlsx"

    return output, filename


def export_all_cases_to_excel() -> None:
    output_file = gregorian_to_jalali(datetime.now(UTC)) + ".xlsx"
    with Session() as session:
        cases = session.query(Case).all()
        data = []
        
        for case in cases:
            status = "در جریان"
            for referral in case.referral_list:
                if referral.operation_type == OperationType.APPROVAL and referral.exit_date is not None:
                    status = "پایان یافته"
                    break
            
            record = {
                "کد رهگیری": case.tracking_number,
                "شماره ملی": case.national_id,
                "نام متقاضی": case.applicant,
                "تاریخ ورود": gregorian_to_jalali(case.entry_date),
                "وضعیت": status,
                "کد شعبه": case.branch,
                "حوزه": case.region.name if case.region else None,
                "نوع درخواست": case.case_type.value,
                "مبلغ": case.amount * 1_000_000,  # تبدیل به ریال
                "وثیقه": case.collateral.value
            }
            
            for i, referral in enumerate(case.referral_list, start=1):
                record.update({
                    f"تاریخ ارجاع {i}": gregorian_to_jalali(referral.entry_date),
                    f"نوع عملیات ارجاع {i}": referral.operation_type.value,
                    f"کارمند ارجاع {i}": referral.operator,
                    f"تاریخ پایان ارجاع {i}": gregorian_to_jalali(referral.exit_date) if referral.exit_date else ""
                })
            
            data.append(record)
        
        df = pd.DataFrame(data)
        
        df.to_excel(output_file, index=False, engine='openpyxl')
