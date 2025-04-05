import logging
from config import Config



logging.basicConfig(
    filename=f"{Config.LOGS_DIR}app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger("BankCaseManager")
