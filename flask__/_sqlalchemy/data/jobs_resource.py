from flask import jsonify
from flask_restful import Resource, abort

from . import db_session
from .jobs_parser import post_parser, put_parser
from .jobs import Jobs

import datetime


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Jobs {job_id} not found")


class JobsResource(Resource):
    def get(self, jobs_id):
        abort_if_job_not_found(jobs_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(jobs_id)
        return jsonify({'job': job.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators',
                  'start_date', 'end_date', 'is_finished'))})

    def delete(self, jobs_id):
        abort_if_job_not_found(jobs_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(jobs_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, jobs_id):
        args = put_parser.parse_args()
        abort_if_job_not_found(jobs_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(jobs_id)

        job.team_leader = args['team_leader']
        job.job = args['job']
        job.work_size = args['work_size']
        job.collaborators = args['collaborators']
        job.start_date = args['start_date']
        job.end_date = args['end_date']
        job.is_finished = args['is_finished']
        job.hazard_category_id = args['hazard_category_id']

        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators',
                  'start_date', 'end_date', 'is_finished')) for item in jobs]})

    def post(self):
        args = post_parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            start_date=args['start_date'] if args['start_date'] else datetime.datetime.now(),
            end_date=args['end_date'] if args['end_date'] else datetime.datetime.now(),
            is_finished=args['is_finished'],
            hazard_category_id=args['hazard_category_id']
        )
        session.add(job)
        session.commit()
        return jsonify({'id': job.id})
