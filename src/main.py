import json
import argparse
import pandas as pd
from src.file_validation import validate_all
from src.load_data import load_all
from src.calculate import run_model


def get_last_day_of_month(today=None):
    if today is None:
        today = pd.Timestamp.today().normalize()  # današnji datum
    next_month = today + pd.offsets.MonthBegin(1)  # početak sledećeg meseca
    last_day = next_month - pd.Timedelta(days=1)  # jedan dan pre početka sledećeg meseca
    return last_day


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--date", help="Override calc_date (YYYY-MM-DD)")
    ap.add_argument("--auto-month-end", action="store_true", help="Koristi poslednji dan tekućeg meseca")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    print(config['mysql_connection'])
    # logika izbora datuma
    if args.date:
        config["calc_date"] = args.date
    elif args.auto_month_end:
        config["calc_date"] = str(get_last_day_of_month())

    print(f"[RUN] Pipeline start for {config['calc_date']}")
    validate_all(config)
    load_all(config)
    run_model(config)
    print("[RUN] Done.")


if __name__ == "__main__":
    main()
