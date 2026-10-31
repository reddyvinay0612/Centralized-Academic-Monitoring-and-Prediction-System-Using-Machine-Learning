"""
Integration Tests for Flask Routes, Authentication, and Role-Based Access Control (RBAC).
"""


def test_health_check_endpoint(client):
    """Verify system health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"


def test_unauthenticated_redirect_to_login(client):
    """Verify protected dashboards redirect unauthenticated guests to login."""
    res_admin = client.get("/admin/dashboard")
    assert res_admin.status_code == 302
    assert "/auth/login" in res_admin.headers["Location"]

    res_faculty = client.get("/faculty/dashboard")
    assert res_faculty.status_code == 302
    assert "/auth/login" in res_faculty.headers["Location"]

    res_student = client.get("/student/dashboard")
    assert res_student.status_code == 302
    assert "/auth/login" in res_student.headers["Location"]


def test_admin_login_and_access(client):
    """Verify Admin authentication and dashboard accessibility."""
    # Post login
    res = client.post("/auth/login", data={
        "email": "test.admin@camps.edu",
        "password": "AdminPass@123"
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"System Overview" in res.data or b"Active Students" in res.data


def test_api_predict_endpoint(client):
    """Verify REST API prediction endpoint returns structured JSON."""
    payload = {
        "Department": "CSD",
        "Gender": "Female",
        "Category": "General",
        "Fee_Status": "Pending",
        "Scholarship": 0,
        "Attendance_Percentage": 62.0,
        "CIE_IA1": 12.0,
        "CIE_IA2": 10.5,
        "CIE_IA3": 11.0,
        "Assignment_Score": 6.0,
        "Lab_Score": 6.0,
        "Total_CIE": 23.0,
        "Sem1_SGPA": 5.4,
        "Sem2_SGPA": 5.2,
        "Sem3_SGPA": 5.0,
        "Sem4_SGPA": 4.8,
        "Cumulative_CGPA": 5.1,
        "Active_Backlogs": 3,
        "10th_Percentage": 70.0,
        "12th_Percentage": 68.0,
        "Entrance_Rank": 45000,
        "Fee_Due_Amount": 30000.0
    }

    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["prediction"]["predicted_risk_level"] in ["High", "Medium", "Low"]
