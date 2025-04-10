import os
import logging
from config import Config


    
if not os.path.exists(Config.LOGS_DIR):
    os.makedirs(Config.LOGS_DIR)


logging.basicConfig(
    filename=f"{Config.LOGS_DIR}app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger("BankCaseManager")
