import requests

for id_test in ['4pm23cs071', '4PM23CS071', ' 4PM23CS071 ', '4pm23cs071@pesitm.edu']:
    r = requests.post('http://localhost:5000/api/auth/login', json={'identifier': id_test, 'password': 'password123', 'expectedRole': 'student'})
    print(f'Test "{id_test}": status={r.status_code}, success={r.json().get("success")}')
