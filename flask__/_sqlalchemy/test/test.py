from datetime import datetime, timedelta

import requests

BASE_URL = 'http://localhost:5000/api/v2/'


def print_response(label, response):
    print(f"\n{label}:")
    print(f"URL: {response.url}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")


def test_api():
    # корректные POST-запросы (создание пользователей)
    valid_users = [
        {
            'surname': 'Pupsik',
            'name': 'Piotr',
            'age': 35,
            'position': 'developer',
            'speciality': 'Python',
            'address': 'module_4',
            'email': 'pupsik@mars.org',
            'hashed_password': 'pupsik999',
            'city_from': 'Kazan'
        },
        {
            'name': 'Maria',
            'surname': 'Petrova',
            'age': 24,
            'position': 'designer',
            'speciality': 'UI',
            'address': 'module_5',
            'email': 'maria@mars.org',
            'hashed_password': 'maria456',
            'city_from': 'Saint-Petersburg'
        },
        {
            'name': 'Otto',
            'surname': 'Heizenof',
            'age': 35,
            'position': 'manager',
            'speciality': 'managing',
            'address': 'module_5',
            'email': 'finland@mars.org',
            'hashed_password': 'ottotenis',
            'city_from': 'Helsinki'
        }
    ]

    created_ids = []
    for user_data in valid_users:
        response = requests.post(BASE_URL + 'users', json=user_data)
        print(f"Создание пользователя {user_data['name']}", response.json())
        if response.status_code == 200:
            created_ids.append(response.json().get('id'))

    # корректные GET-запросы
    response = requests.get(BASE_URL + 'users')
    print(response.json())

    # получение каждого созданного пользователя
    for user_id in created_ids:
        response = requests.get(f"{BASE_URL}users/{user_id}")
        print_response(f"Получение пользователя {user_id}", response)

    # корректные PUT-запросы (обновление данных)
    updates = [
        {'age': 29, 'position': 'senior engineer'},
        {'city_from': 'Volgograd', 'email': 'new_maria@mars.org'},
        {'speciality': 'top-manager', 'hashed_password': 'tabletennis'}
    ]

    for user_id, update_data in zip(created_ids, updates):
        response = requests.put(f"{BASE_URL}users/{user_id}", json=update_data)
        print_response(f"Обновление пользователя {user_id}", response)

    # корректные DELETE-запросы
    for user_id in created_ids:
        response = requests.delete(f"{BASE_URL}users/{user_id}")
        print_response(f"Удаление пользователя {user_id}", response)

    # некорректные POST-запросы
    test_cases = [
        ("Пустой запрос", {}),
        ("Только обязательные поля (без пароля)", {
            'surname': 'Сидоров',
            'name': 'Сидор',
            'email': 'sidorov@example.com'
        }),
        ("Неверный тип данных (age как строка)", {
            'surname': 'Сидоров',
            'name': 'Сидор',
            'age': 'тридцать',
            'email': 'sidorov@example.com',
            'hashed_password': 'pass123'
        }),
        ("Очень длинное имя", {
            'surname': 'О' * 1000,
            'name': 'Оченьдлинноеимя' * 50,
            'age': 30,
            'email': 'long@example.com',
            'hashed_password': 'pass123'
        }),
        ("Невалидный email", {
            'surname': 'Иванов',
            'name': 'Иван',
            'age': 30,
            'email': 'invalid-email',
            'hashed_password': 'pass123'
        })
    ]

    for label, data in test_cases:
        response = requests.post(BASE_URL, json=data)
        print(label, response.json())

    # некорректные GET-запросы
    test_cases = [
        ("Несуществующий ID", f"{BASE_URL}users/999999"),
        ("ID как строка", f"{BASE_URL}users/abc"),
        ("Отрицательный ID", f"{BASE_URL}users/-1"),
        ("Очень большой ID", f"{BASE_URL}users/99999999999999999999")
    ]

    for label, url in test_cases:
        response = requests.get(url)
        print_response(label, response)

    # некорректные PUT-запросы
    test_cases = [
        ("Пустой запрос", {}),
        ("Несуществующее поле", {'unknown_field': 'value'}),
        ("Неверный тип данных (age как строка)", {'age': 'двадцать'}),
        ("Очень длинное значение", {'city_from': 'А' * 1000}),
        ("Невалидный email", {'email': 'invalid-email'})
    ]

    for label, data in test_cases:
        response = requests.put(f"{BASE_URL}users/{created_ids[0]}", json=data)
        print_response(label, response)

    # некорректные DELETE-запросы
    test_cases = [
        ("Несуществующий ID", f"{BASE_URL}users/999999"),
        ("ID как строка", f"{BASE_URL}users/abc"),
        ("Отрицательный ID", f"{BASE_URL}users/-1")
    ]

    for label, url in test_cases:
        response = requests.delete(url)
        print_response(label, response)


def test_jobs_api():
    users = [
        {'surname': 'Draft', 'name': 'Draft', 'age': 30, 'position': 'cap',
         'speciality': 'engineer', 'address': 'module_1',
         'email': 'draft@mars.org', 'hashed_password': 'cap', 'city_from': 'Mars'},
        {'surname': 'Draft1', 'name': 'Draft1', 'age': 30, 'position': 'cap',
         'speciality': 'engineer', 'address': 'module_1',
         'email': 'draft1@mars.org', 'hashed_password': 'cap', 'city_from': 'Mars'}
    ]

    user_ids = []
    for user in users:
        resp = requests.post(BASE_URL + 'users', json=user)
        if resp.status_code == 200:
            user_ids.append(resp.json()['id'])

    if len(user_ids) < 2:
        print("Не удалось создать тестовых пользователей!")
        return

    # корректные POST-запросы (создание работ)
    valid_jobs = [
        {
            'job': 'Deploy solar panels',
            'work_size': 15,
            'collaborators': f"{user_ids[1]}",
            'team_leader': user_ids[0],
            'is_finished': False,
            'start_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'job': 'Soil analysis',
            'work_size': 8,
            'collaborators': f"{user_ids[0]}, {user_ids[1]}",
            'team_leader': user_ids[1],
            'is_finished': True
        }
    ]

    created_ids = []
    for job_data in valid_jobs:
        response = requests.post(BASE_URL + 'jobs', json=job_data)
        print(f"Создание работы '{job_data['job']}'", response.json())
        if response.status_code == 200:
            created_ids.append(response.json().get('id'))

    response = requests.get(BASE_URL + 'jobs')
    print_response("GET /api/v2/jobs", response)

    # получение каждой созданной работы
    for jobs_id in created_ids:
        response = requests.get(f"{BASE_URL}jobs/{jobs_id}")
        print_response(f"Получение работы {jobs_id}", response)

    # корректные PUT-запросы (обновление данных)
    updates = [
        {'work_size': 20, 'is_finished': True},
        {'job': 'Advanced soil analysis', 'collaborators': f"{user_ids[1]}"}
    ]

    for job_id, update_data in zip(created_ids, updates):
        response = requests.put(f"{BASE_URL}jobs/{job_id}", json=update_data)
        print_response(f"Обновление работы {job_id}", response)

        response = requests.get(f"{BASE_URL}jobs/{job_id}")
        print_response(f"Проверка обновления {job_id}", response)

    # корректные DELETE-запросы
    for job_id in created_ids:
        response = requests.delete(f"{BASE_URL}jobs/{job_id}")
        print_response(f"Удаление работы {job_id}", response)

        response = requests.get(f"{BASE_URL}jobs/{job_id}")
        print_response(f"Проверка удаления {job_id}", response)

    # некорректные POST-запросы
    test_cases = [
        ("Пустой запрос", {}),
        ("Без обязательного поля job", {
            'work_size': 10,
            'collaborators': "1,2",
            'team_leader': 1
        }),
        ("Неверный тип work_size", {
            'job': 'Test job',
            'work_size': 'ten',
            'collaborators': "1",
            'team_leader': 1
        }),
        ("Несуществующий team_leader", {
            'job': 'Test job',
            'work_size': 10,
            'collaborators': "1",
            'team_leader': 999
        })
    ]

    for label, data in test_cases:
        response = requests.post(BASE_URL + 'jobs', json=data)
        print_response(label, response)

    # некорректные GET-запросы
    test_cases = [
        ("Несуществующий ID", f"{BASE_URL}jobs/999999"),
        ("ID как строка", f"{BASE_URL}jobs/abc"),
        ("Отрицательный ID", f"{BASE_URL}jobs/-1")
    ]

    for label, url in test_cases:
        response = requests.get(url)
        print_response(label, response)

    # некорректные PUT-запросы
    temp_job = {
        'job': 'Temporary job',
        'work_size': 5,
        'collaborators': f"{user_ids[0]}",
        'team_leader': user_ids[1]
    }
    resp = requests.post(BASE_URL + 'jobs', json=temp_job)
    temp_id = resp.json().get('id')

    test_cases = [
        ("Пустой запрос", {}),
        ("Несуществующее поле", {'unknown_field': 'value'}),
        ("Неверный тип is_finished", {'is_finished': 'yes'}),
        ("Очень длинное job", {'job': 'A' * 1000})
    ]

    for label, data in test_cases:
        response = requests.put(f"{BASE_URL}jobs/{temp_id}", json=data)
        print_response(label, response)

    requests.delete(f"{BASE_URL}jobs/{temp_id}")

    # некорректные DELETE-запросы
    test_cases = [
        ("Несуществующий ID", f"{BASE_URL}jobs/999999"),
        ("ID как строка", f"{BASE_URL}jobs/abc"),
        ("Отрицательный ID", f"{BASE_URL}jobs/-1")
    ]

    for label, url in test_cases:
        response = requests.delete(url)
        print_response(label, response)

    for user_id in user_ids:
        requests.delete(f"{BASE_URL}users/{user_id}")


if __name__ == '__main__':
    test_jobs_api()
    # test_api()
