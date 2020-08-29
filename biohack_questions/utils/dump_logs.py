import argparse
import datetime
import json
from pathlib import Path

from biohack_questions.src.mongoclient import get_logs_collection


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump user logs from the DB')
    parser.add_argument("start_date", type=str, help="start date of the period to dump (this day included, format YYYY-MM-DD)")
    parser.add_argument("end_date", type=str, help="end date of the period to dump (this day included, format YYYY-MM-DD)")
    parser.add_argument("--users", action="store", default='')

    args = parser.parse_args()

    start_time = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
    users = args.users.split(',') if args.users else None

    if start_time > end_time:
        raise ValueError('start_time > end_time')

    log_coll = get_logs_collection()
    q = {
        'date': {
            '$gte': start_time,
            '$lte': end_time,
        },
    }
    if users is not None:
        q['username'] = {
            '$in': users
        }

    result = []

    cursor = log_coll.find(q)
    for rec in cursor:
        rec['_id'] = str(rec['_id'])
        rec['date'] = str(rec['date'])
        result.append(rec)

    with open('%s/dump_%s_%s.txt' % (str(Path.home()), args.start_date, args.end_date), 'w') as wf:
        for d in result:
            wf.write(json.dumps(d) + '\n')
