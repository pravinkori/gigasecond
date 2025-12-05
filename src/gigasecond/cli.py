import argparse
from datetime import datetime
from .core import parse_dob, age_seconds, time_until_milestone, BILLION, milestone_datetime

def main(argv=None):
    parser = argparse.ArgumentParser(prog="billion-seconds")
    parser.add_argument("--dob", required=True, help="Date of birth (YYYY-MM-DD or YYYY-MM-DD HH:MM)")
    parser.add_argument("--billion", type=float, default=1.0, help="Which billion (1, 2, 1.5 etc.)")
    args = parser.parse_args(argv)

    dob = parse_dob(args.dob)
    seconds = int(args.billion * BILLION)
    now = datetime.now()
    print(f"DOB: {dob}")
    print(f"Age (seconds): {age_seconds(dob)}")
    print(f"Milestone ({seconds:,}) occurs on: {milestone_datetime(dob, seconds)}")
    remaining = time_until_milestone(dob, seconds, now)
    print(f"Time until milestone: {remaining}")
