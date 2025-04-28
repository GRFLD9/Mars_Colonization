from flask import Blueprint, make_response, jsonify, request
from datetime import datetime

from . import db_session
from .jobs import Jobs

blueprint = Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify({
        'jobs': [
            item.to_dict(only=(
                'id', 'team_leader', 'job', 'work_size',
                'collaborators', 'start_date', 'end_date',
                'is_finished', 'hazard_category_id'
            ))
            for item in jobs
        ]
    })


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['GET'])
def get_one_job(jobs_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(jobs_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'jobs': job.to_dict(only=(
                'id', 'team_leader', 'job', 'work_size',
                'collaborators', 'start_date', 'end_date',
                'is_finished', 'hazard_category_id'
            ))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    required_fields = ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished', 'hazard_category_id']

    if not all(key in request.json for key in required_fields):
        return make_response(jsonify({
            'error': 'Bad request',
            'required_fields': required_fields
        }), 400)

    try:
        start_date = None
        if 'start_date' in request.json:
            try:
                start_date = datetime.fromisoformat(request.json['start_date']) if isinstance(
                    request.json['start_date'], str) else request.json['start_date']
                if not isinstance(start_date, datetime):
                    raise ValueError
            except (ValueError, TypeError):
                return make_response(jsonify({
                    'error': 'Invalid start_date',
                    'message': 'Must be ISO format string or datetime object'
                }), 400)

        end_date = None
        if 'end_date' in request.json:
            try:
                end_date = datetime.fromisoformat(request.json['end_date']) if isinstance(request.json['end_date'],
                                                                                          str) else request.json[
                    'end_date']
                if not isinstance(end_date, datetime):
                    raise ValueError
            except (ValueError, TypeError):
                return make_response(jsonify({
                    'error': 'Invalid end_date',
                    'message': 'Must be ISO format string or datetime object'
                }), 400)
        db_sess = db_session.create_session()

        job = Jobs(
            job=request.json['job'],
            team_leader=request.json['team_leader'],
            work_size=request.json['work_size'],
            collaborators=request.json['collaborators'],
            is_finished=request.json['is_finished'],
            hazard_category_id=request.json['hazard_category_id'],
        )

        if start_date and end_date:
            job.start_date = start_date
            job.end_date = end_date

        db_sess.add(job)
        db_sess.commit()

        return jsonify({
            'success': True,
            'id': job.id,
            'job': job.to_dict(only=(
                'id', 'job', 'team_leader', 'work_size',
                'collaborators', 'is_finished', 'hazard_category_id'
            ))
        }), 201

    except Exception as e:
        db_sess.rollback()
        return make_response(jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500)


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['DELETE'])
def delete_news(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(jobs_id)
    if not jobs:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    db_sess = db_session.create_session()
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)

    job = db_sess.query(Jobs).get(job_id)

    if not job:
        return make_response(jsonify({'error': 'Job not found'}), 404)

    try:
        if 'job' in request.json:
            job.job = request.json['job']
        if 'team_leader' in request.json:
            job.team_leader = request.json['team_leader']
        if 'work_size' in request.json:
            job.work_size = request.json['work_size']
        if 'collaborators' in request.json:
            job.collaborators = request.json['collaborators']
        if 'is_finished' in request.json:
            job.is_finished = request.json['is_finished']
        if 'hazard_category_id' in request.json:
            job.hazard_category_id = request.json['hazard_category_id']
        if 'start_date' in request.json:
            try:
                if isinstance(request.json['start_date'], str):
                    job.start_date = datetime.fromisoformat(request.json['start_date'])
                else:
                    return make_response(jsonify({
                        'error': 'Invalid start_date format',
                        'expected': 'ISO format string or datetime object'
                    }), 400)
            except (ValueError, TypeError):
                return make_response(jsonify({
                    'error': 'Invalid start_date value',
                    'message': 'Must be a valid datetime'
                }), 400)

        if 'end_date' in request.json:
            try:
                if isinstance(request.json['end_date'], str):
                    job.end_date = datetime.fromisoformat(request.json['end_date'])
                else:
                    return make_response(jsonify({
                        'error': 'Invalid end_date format',
                        'expected': 'ISO format string or datetime object'
                    }), 400)
            except (ValueError, TypeError):
                return make_response(jsonify({
                    'error': 'Invalid end_date value',
                    'message': 'Must be a valid datetime'
                }), 400)

        db_sess.commit()

        return jsonify({
            'success': True,
            'job': job.to_dict(only=(
                'id', 'team_leader', 'job', 'work_size',
                'collaborators', 'is_finished', 'hazard_category_id'
            ))
        })

    except Exception as e:
        db_sess.rollback()
        return make_response(jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500)
