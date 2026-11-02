import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_health_check_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'student' in data['portals']
    assert 'parent' in data['portals']
    assert 'teacher' in data['portals']
    assert 'admin' in data['portals']
    assert 'principal' in data['portals']

def test_system_info_endpoint(client):
    response = client.get('/api/system/info')
    assert response.status_code == 200
    data = response.get_json()
    assert data['rbac_enabled'] is True
    assert 'PES Institute of Technology' in data['college_name']
    assert set(data['available_roles']) == {'student', 'parent', 'teacher', 'admin', 'principal'}

def test_blueprint_registrations(client):
    blueprints = [
        '/api/auth/status',
        '/api/student/status',
        '/api/parent/status',
        '/api/teacher/status',
        '/api/admin/status',
        '/api/principal/status',
        '/api/notifications/status'
    ]
    for endpoint in blueprints:
        res = client.get(endpoint)
        assert res.status_code == 200, f"Failed on endpoint: {endpoint}"
        assert res.get_json()['status'] in ['active', 'scaffolded']
