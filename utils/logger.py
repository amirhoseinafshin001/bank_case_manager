import logging


logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,  # فقط INFO و بالاتر ذخیره میشه
    format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger("BankCaseManager")