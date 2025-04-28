# Пример добавления города для пользователя
from requests import put

# добавляем/обновляем город для пользователя с id=1
response = put('http://localhost:5000/api/users/1', json={
    'city_from': 'Москва'
}).json()
print(response)