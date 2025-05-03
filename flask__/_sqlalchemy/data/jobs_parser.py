from datetime import datetime

from flask_restful import reqparse


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return datetime.fromisoformat(value)


post_parser = reqparse.RequestParser()
post_parser.add_argument('job', required=True)
post_parser.add_argument('work_size', type=int, required=True)
post_parser.add_argument('collaborators', required=True)
post_parser.add_argument('team_leader', type=int, required=True)
post_parser.add_argument('is_finished', type=bool, required=True)
post_parser.add_argument('hazard_category_id', type=int, required=False)
post_parser.add_argument('start_date', type=parse_datetime, required=False)
post_parser.add_argument('end_date', type=parse_datetime, required=False)

put_parser = reqparse.RequestParser()
put_parser.add_argument('job', required=False)
put_parser.add_argument('work_size', type=int, required=False)
put_parser.add_argument('collaborators', required=False)
put_parser.add_argument('team_leader', type=int, required=False)
put_parser.add_argument('is_finished', type=bool, required=False)
put_parser.add_argument('hazard_category_id', type=int, required=False)
put_parser.add_argument('start_date', type=parse_datetime, required=False)
put_parser.add_argument('end_date', type=parse_datetime, required=False)
