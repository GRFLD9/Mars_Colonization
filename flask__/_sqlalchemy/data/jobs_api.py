from flask import Blueprint, make_response, jsonify, request

from . import db_session
from .jobs import Jobs

blueprint = Blueprint(
    'news_api',
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
        db_sess = db_session.create_session()

        # Создаем работу с дефолтными датами
        job = Jobs(
            job=request.json['job'],
            team_leader=request.json['team_leader'],
            work_size=request.json['work_size'],
            collaborators=request.json['collaborators'],
            is_finished=request.json['is_finished'],
            hazard_category_id=request.json['hazard_category_id'],
            # start_date и end_date будут автоматически заполнены
        )

        db_sess.add(job)
        db_sess.commit()

        return jsonify({
            'success': True,
            'id': job.id,
            'job': job.to_dict()
        }), 201

    except Exception as e:
        db_sess.rollback()
        return make_response(jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500)
