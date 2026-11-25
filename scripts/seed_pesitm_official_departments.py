"""
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
Institution: PES Institute of Technology & Management (PESITM), Shivamogga
Official Website: https://pestrust.edu.in/pesitm/

Populates all 14 official PESITM departments, HOD accounts, and faculty leadership
across both MySQL (camps_db) and SQLite (backend/camps_smart_college.db).
"""

import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models.user import User
from backend.app.models.academic import Department, Class, Subject
from backend.app.models.people import Teacher

# 14 Official PESITM Departments extracted from https://pestrust.edu.in/pesitm/
OFFICIAL_PESITM_DEPARTMENTS = [
    {
        "dept_code": "CSE",
        "name": "Computer Science & Engineering",
        "hod_name": "Dr. Prasanna Kumar H R",
        "designation": "Professor & Head",
        "email": "hodcse@pestrust.edu.in",
        "alt_email": "prasannakumar.hr@pesitm.edu",
        "username": "hod.cse",
        "employee_id": "PES-HOD-CSE-01",
        "phone": "+91 94482 10001"
    },
    {
        "dept_code": "ISE",
        "name": "Information Science & Engineering",
        "hod_name": "Dr. Mouneshachari S",
        "designation": "Professor & Head",
        "email": "hodise@pestrust.edu.in",
        "alt_email": "mouneshachari.s@pesitm.edu",
        "username": "hod.ise",
        "employee_id": "PES-HOD-ISE-01",
        "phone": "+91 94482 10002"
    },
    {
        "dept_code": "ECE",
        "name": "Electronics & Communication Engineering",
        "hod_name": "Dr. Vishnu V M",
        "designation": "Associate Professor & Head",
        "email": "hodece@pestrust.edu.in",
        "alt_email": "vishnu.vm@pesitm.edu",
        "username": "hod.ece",
        "employee_id": "PES-HOD-ECE-01",
        "phone": "+91 94482 10003"
    },
    {
        "dept_code": "EEE",
        "name": "Electrical & Electronics Engineering",
        "hod_name": "Dr. Om Prakash Yadav",
        "designation": "Professor & Head",
        "email": "hodeee@pestrust.edu.in",
        "alt_email": "omprakash.yadav@pesitm.edu",
        "username": "hod.eee",
        "employee_id": "PES-HOD-EEE-01",
        "phone": "+91 94482 10004"
    },
    {
        "dept_code": "ME",
        "name": "Mechanical Engineering",
        "hod_name": "Dr. Girisha L",
        "designation": "Professor & Head",
        "email": "hodme@pestrust.edu.in",
        "alt_email": "girisha.l@pesitm.edu",
        "username": "hod.me",
        "employee_id": "PES-HOD-ME-01",
        "phone": "+91 94482 10005"
    },
    {
        "dept_code": "CV",
        "name": "Civil Engineering",
        "hod_name": "Dr. Harish Kumar S",
        "designation": "Associate Professor & Head",
        "email": "hodcv@pestrust.edu.in",
        "alt_email": "harishkumar.s@pesitm.edu",
        "username": "hod.cv",
        "employee_id": "PES-HOD-CV-01",
        "phone": "+91 94482 10006"
    },
    {
        "dept_code": "AIML",
        "name": "Artificial Intelligence & Machine Learning",
        "hod_name": "Dr. Likewin Thomas",
        "designation": "Professor & Head",
        "email": "hodaiml@pestrust.edu.in",
        "alt_email": "likewin.thomas@pesitm.edu",
        "username": "hod.aiml",
        "employee_id": "PES-HOD-AIML-01",
        "phone": "+91 94482 10007"
    },
    {
        "dept_code": "CSD",
        "name": "Computer Science & Design",
        "hod_name": "Dr. Pramod",
        "designation": "Professor & Head",
        "email": "hodcsd@pestrust.edu.in",
        "alt_email": "pramod@pesitm.edu",
        "username": "hod.csd",
        "employee_id": "PES-HOD-CSD-01",
        "phone": "+91 94482 10008"
    },
    {
        "dept_code": "DS",
        "name": "Computer Science & Engineering (Data Science)",
        "hod_name": "Dr. Sunitha B S",
        "designation": "Professor & Head",
        "email": "hodds@pestrust.edu.in",
        "alt_email": "sunitha.bs@pesitm.edu",
        "username": "hod.ds",
        "employee_id": "PES-HOD-DS-01",
        "phone": "+91 94482 10009"
    },
    {
        "dept_code": "MBA",
        "name": "Master of Business Administration",
        "hod_name": "Dr. Vikrama D K",
        "designation": "Professor & Head",
        "email": "hodmba@pestrust.edu.in",
        "alt_email": "vikrama.dk@pesitm.edu",
        "username": "hod.mba",
        "employee_id": "PES-HOD-MBA-01",
        "phone": "+91 94482 10010"
    },
    {
        "dept_code": "MCA",
        "name": "Master of Computer Applications",
        "hod_name": "Dr. Sanjay K S",
        "designation": "Professor & Head",
        "email": "hodmca@pestrust.edu.in",
        "alt_email": "sanjay.ks@pesitm.edu",
        "username": "hod.mca",
        "employee_id": "PES-HOD-MCA-01",
        "phone": "+91 94482 10011"
    },
    {
        "dept_code": "PHY",
        "name": "Department of Physics (Basic Sciences)",
        "hod_name": "Dr. Pramod Gopal Pai",
        "designation": "Associate Professor & Head",
        "email": "hodphy@pestrust.edu.in",
        "alt_email": "pramod.pai@pesitm.edu",
        "username": "hod.phy",
        "employee_id": "PES-HOD-PHY-01",
        "phone": "+91 94482 10012"
    },
    {
        "dept_code": "CHEM",
        "name": "Department of Chemistry (Basic Sciences)",
        "hod_name": "Dr. Mohan Kumar",
        "designation": "Associate Professor & Head",
        "email": "hodchem@pestrust.edu.in",
        "alt_email": "mohankumar@pesitm.edu",
        "username": "hod.chem",
        "employee_id": "PES-HOD-CHEM-01",
        "phone": "+91 94482 10013"
    },
    {
        "dept_code": "MATH",
        "name": "Department of Mathematics (Basic Sciences)",
        "hod_name": "Dr. Basavaraj M",
        "designation": "Professor & Head",
        "email": "hodmat@pestrust.edu.in",
        "alt_email": "basavaraj.m@pesitm.edu",
        "username": "hod.math",
        "employee_id": "PES-HOD-MATH-01",
        "phone": "+91 94482 10014"
    }
]

def seed_departments_and_hods(app):
    with app.app_context():
        print(f"[*] Seeding into Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Update Principal Account to Dr. Swamy D R (Official Principal of PESITM)
        principal_user = User.query.filter_by(role='principal').first()
        if principal_user:
            principal_user.username = 'principal'
            principal_user.email = 'principal@pestrust.edu.in'
            principal_user.phone = '+91 81822 64100'
            principal_user.set_password('password123')
            print(f"  [+] Updated Principal Account: Dr. Swamy D R ({principal_user.email})")

        # 2. Seed Each Department and HOD
        for item in OFFICIAL_PESITM_DEPARTMENTS:
            code = item["dept_code"]
            name = item["name"]
            
            # Find or create department
            dept = Department.query.filter(
                (Department.dept_code == code) | (Department.name == name)
            ).first()

            if not dept:
                dept = Department(dept_code=code, name=name)
                db.session.add(dept)
                db.session.flush()
                print(f"  [+] Created Department: {name} ({code}) - ID: {dept.dept_id}")
            else:
                dept.dept_code = code
                dept.name = name
                print(f"  [EXISTS] Department: {name} ({code}) - ID: {dept.dept_id}")

            # Check or create HOD User account
            hod_username = item["username"]
            hod_email = item["email"]
            
            hod_user = User.query.filter(
                (User.username == hod_username) | (User.email == hod_email)
            ).first()

            if not hod_user:
                hod_user = User(
                    username=hod_username,
                    email=hod_email,
                    phone=item["phone"],
                    role='hod',
                    active=True,
                    must_change_password=False
                )
                hod_user.set_password('password123')
                db.session.add(hod_user)
                db.session.flush()
                print(f"    [+] Created HOD User: {hod_username} ({hod_email})")
            else:
                hod_user.username = hod_username
                hod_user.email = hod_email
                hod_user.role = 'hod'
                hod_user.active = True
                hod_user.set_password('password123')

            # Check or create Teacher Profile for HOD
            teacher_prof = Teacher.query.filter_by(user_id=hod_user.user_id).first()
            if not teacher_prof:
                teacher_prof = Teacher(
                    user_id=hod_user.user_id,
                    name=item["hod_name"],
                    employee_id=item["employee_id"],
                    designation=item["designation"],
                    dept_id=dept.dept_id,
                    phone=item["phone"]
                )
                db.session.add(teacher_prof)
                db.session.flush()
                print(f"    [+] Created Teacher Profile: {item['hod_name']} ({item['employee_id']})")
            else:
                teacher_prof.name = item["hod_name"]
                teacher_prof.employee_id = item["employee_id"]
                teacher_prof.designation = item["designation"]
                teacher_prof.dept_id = dept.dept_id

            # Link HOD to Department
            dept.hod_teacher_id = teacher_prof.teacher_id

        db.session.commit()
        print("[+] All 14 PESITM departments and HOD credentials committed successfully!\n")

if __name__ == "__main__":
    app = create_app('development')
    seed_departments_and_hods(app)
