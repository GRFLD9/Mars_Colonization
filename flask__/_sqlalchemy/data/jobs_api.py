from flask import Blueprint, make_response, jsonify

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
