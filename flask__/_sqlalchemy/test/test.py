from requests import post

print(post('http://localhost:5000/api/jobs', json={}).json())

print(post('http://localhost:5000/api/jobs',
           json={'title': 'Заголовок'}).json())

print(post('http://localhost:5000/api/jobs',
           json={'job': 'Weld the broken piece of gateway number 1 in space',
                 'work_size': 15,
                 'team_leader': 3,
                 'is_finished': False,
                 'hazard_category_id': 4,
                 'collaborators': '1, 2'}).json())
