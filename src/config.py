from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
SETTINGS_PATH = BASE_DIR / "user_settings.json"
DATA_DIR = BASE_DIR / "data"
OPERATIONS_DIR = DATA_DIR / "operations.xlsx"
LOGS_DIR.mkdir(exist_ok=True)
