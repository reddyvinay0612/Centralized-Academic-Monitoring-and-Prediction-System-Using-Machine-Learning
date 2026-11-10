import os
import sys

# Ensure root directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.app.models.academic import Department

ALL_BRANCHES = [
    # Engineering Disciplines
    ('CIV', 'Civil Engineering'),
    ('CSE', 'Computer Science and Engineering'),
    ('EEE', 'Electrical and Electronics Engineering'),
    ('ECE', 'Electronics and Communications Engineering'),
    ('ISE', 'Information Science and Engineering'),
    ('MECH', 'Mechanical Engineering'),
    ('AIML', 'Artificial Intelligence and Machine Learning'),
    ('CE', 'Computer Engineering'),
    ('CSDS', 'Computer Science and Engineering(Data Science)'),
    ('CSD', 'Computer Science and Design'),
    # Basic Science and Humanities
    ('PHY', 'Physics'),
    ('MATH', 'Mathematics'),
    ('CHEM', 'Chemistry'),
    ('HUM', 'Humanities'),
]

def add_all_branches():
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        print("=" * 70)
        print("PESITM - SYNCHRONIZING ALL ACADEMIC BRANCHES & DEPARTMENTS")
        print("=" * 70)
        
        added = 0
        existing = 0
        
        for code, name in ALL_BRANCHES:
            dept = Department.query.filter_by(dept_code=code).first()
            if not dept:
                # Also check by name
                dept = Department.query.filter_by(name=name).first()
                
            if not dept:
                new_dept = Department(dept_code=code, name=name)
                db.session.add(new_dept)
                added += 1
                print(f"[+] Added new branch: [{code}] {name}")
            else:
                dept.dept_code = code
                dept.name = name
                existing += 1
                print(f"[*] Verified existing branch: [{code}] {name} (ID: {dept.dept_id})")
                
        db.session.commit()
        print("=" * 70)
        print(f"SUCCESS: {added} new branches inserted, {existing} verified.")
        print(f"Total Academic Departments in Database: {Department.query.count()}")
        print("=" * 70)

if __name__ == '__main__':
    add_all_branches()
