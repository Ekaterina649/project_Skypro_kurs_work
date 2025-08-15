from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
SETTINGS_PATH = Path(__file__).resolve().parent.parent / "user_settings.json"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LOGS_DIR.mkdir(exist_ok=True)