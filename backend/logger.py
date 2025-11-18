# logger.py
import datetime

def _ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_info(msg: str):
    print(f"[INFO { _ts() }] {msg}")

def log_warn(msg: str):
    print(f"[WARN { _ts() }] {msg}")

def log_error(msg: str):
    print(f"[ERROR { _ts() }] {msg}")
