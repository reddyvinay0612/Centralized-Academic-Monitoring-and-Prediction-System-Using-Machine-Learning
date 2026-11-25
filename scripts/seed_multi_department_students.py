"""
Seed multi-department student datasets into CAMPS-ML databases (both SQLite and MySQL).
"""

import os
import sys
import pandas as pd
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models.user import User
from backend.app.models.academic import Department, Class, Subject
from backend.app.models.people import Student, Teacher
from backend.app.models.grading import SemesterResult, Mark, Attendance

def seed_database(app):
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"\n[*] Processing Database: {db_uri}")
        
        master_path = os.path.join(project_root, 'data', 'processed', 'pesitm_multi_department_master.csv')
        df = pd.read_csv(master_path)
        print(f"[*] Loaded {len(df)} student records from {master_path}")
        
        # Ensure CE department exists
        ce_dept = Department.query.filter_by(dept_code='CE').first()
        if not ce_dept:
            ce_dept = Department(dept_code='CE', name='Computer Engineering')
            db.session.add(ce_dept)
            db.session.flush()
            print("  [+] Added Department: Computer Engineering (CE)")
            
        # Cache departments and classes
        dept_map = {d.dept_code.upper(): d for d in Department.query.all()}
        # Also map MECH -> ME, CIV -> CV
        dept_map['MECH'] = dept_map.get('ME')
        dept_map['CIV'] = dept_map.get('CV')
        dept_map['IS'] = dept_map.get('ISE')
        dept_map['EE'] = dept_map.get('EEE')
        dept_map['EC'] = dept_map.get('ECE')
        dept_map['AI'] = dept_map.get('AIML')
        dept_map['CG'] = dept_map.get('CSD')
        dept_map['CD'] = dept_map.get('CSD')
        
        class_cache = {}
        for code, dept in dept_map.items():
            if not dept:
                continue
            cls = Class.query.filter_by(dept_id=dept.dept_id, semester=6).first()
            if not cls:
                cls = Class(
                    class_name=f"6th {dept.dept_code}",
                    section="A",
                    semester=6,
                    academic_year="2025-26",
                    dept_id=dept.dept_id,
                    mentor_teacher_id=dept.hod_teacher_id
                )
                db.session.add(cls)
                db.session.flush()
                print(f"  [+] Created Class: 6th {dept.dept_code} (A) - ID {cls.class_id}")
            class_cache[code] = cls.class_id
            class_cache[dept.dept_code] = cls.class_id
            
        # Ensure default subjects exist for each department
        subject_cache = {}
        for dept_code, dept in dept_map.items():
            if not dept:
                continue
            subj = Subject.query.filter_by(dept_id=dept.dept_id, semester=6).first()
            if not subj:
                code_tag = dept.dept_code[:3].upper()
                subj = Subject.query.filter_by(subject_code=f"21{code_tag}61").first()
                if not subj:
                    subj = Subject(
                        subject_code=f"21{code_tag}61",
                        subject_name=f"Core Engineering in {dept.name}",
                        credits=4,
                        dept_id=dept.dept_id,
                        semester=6
                    )
                    db.session.add(subj)
                    db.session.flush()
            subject_cache[dept.dept_id] = subj.subject_id
            subject_cache[dept_code] = subj.subject_id
            
        # Precompute password hash once for performance
        default_pwd_hash = bcrypt.generate_password_hash("password123").decode('utf-8')
        
        created_users = 0
        updated_students = 0
        
        for _, row in df.iterrows():
            usn = str(row['USN']).strip().upper()
            name = str(row['Name']).strip()
            dept_tag = str(row.get('department', 'CSE')).strip().upper()
            class_id = class_cache.get(dept_tag, 1)
            
            # 1. User Account
            user = User.query.filter_by(username=usn).first()
            if not user:
                email = f"{usn.lower()}@pesitm.edu"
                user = User(
                    username=usn,
                    email=email,
                    role='student',
                    password_hash=default_pwd_hash,
                    active=True,
                    must_change_password=False
                )
                db.session.add(user)
                db.session.flush()
                created_users += 1
            elif not user.password_hash:
                user.password_hash = default_pwd_hash
                
            # 2. Student Profile
            student = Student.query.filter_by(usn=usn).first()
            if not student:
                student = Student(
                    user_id=user.user_id,
                    name=name,
                    usn=usn,
                    class_id=class_id,
                    academic_status='active',
                    fee_status='paid'
                )
                db.session.add(student)
                db.session.flush()
            else:
                student.name = name
                student.class_id = class_id
                if not student.user_id:
                    student.user_id = user.user_id
                    
            updated_students += 1
            
            # 3. Semester Results (Sem 1 to 6)
            for sem in range(1, 7):
                sgpa_col = f"Sem{sem}_SGPA"
                sgpa_val = row.get(sgpa_col)
                if pd.isna(sgpa_val) or sgpa_val is None or str(sgpa_val).strip() == '':
                    continue
                try:
                    sgpa_float = float(sgpa_val)
                except ValueError:
                    continue
                    
                # Calculate backlogs for this sem
                sem_backlogs = 0
                if sem == 6:
                    sem_backlogs = int(row.get('Sem6_failed_subjects', 0) or 0)
                else:
                    # Distribute prior failures
                    tot_prior = int(row.get('Sem1_5_failed_subjects', 0) or 0)
                    sem_backlogs = 1 if tot_prior > 0 and sem == 5 else 0
                    
                sr = SemesterResult.query.filter_by(student_id=student.student_id, semester=sem).first()
                if not sr:
                    sr = SemesterResult(
                        student_id=student.student_id,
                        semester=sem,
                        sgpa=round(sgpa_float, 2),
                        credits_earned=20,
                        backlogs=sem_backlogs
                    )
                    db.session.add(sr)
                else:
                    sr.sgpa = round(sgpa_float, 2)
                    sr.backlogs = sem_backlogs
                    
            # 4. Attendance Record
            subj_id = subject_cache.get(dept_tag) or subject_cache.get(1)
            if subj_id:
                int_pct = float(row.get('Sem5_internal_pct', 75.0) or 75.0)
                # Map internal pct to realistic class attendance 75-95%
                att_pct = min(98.0, max(65.0, round(int_pct + 5.0, 1)))
                att = Attendance.query.filter_by(student_id=student.student_id, subject_id=subj_id).first()
                if not att:
                    tot_cls = 50
                    att_cls = int(round((att_pct / 100.0) * tot_cls))
                    att = Attendance(
                        student_id=student.student_id,
                        subject_id=subj_id,
                        total_classes=tot_cls,
                        attended_classes=att_cls,
                        percentage=att_pct
                    )
                    db.session.add(att)
                else:
                    att.percentage = att_pct
                    att.attended_classes = int(round((att_pct / 100.0) * att.total_classes))
                    
            # 5. CIE Marks Record
            if subj_id:
                avg_ia = float(row.get('avg_ia', 20.0) or 20.0)
                mark = Mark.query.filter_by(student_id=student.student_id, subject_id=subj_id).first()
                ia_score = min(25.0, max(5.0, round(avg_ia, 1)))
                if not mark:
                    mark = Mark(
                        student_id=student.student_id,
                        subject_id=subj_id,
                        cie1=ia_score,
                        cie2=min(25.0, round(ia_score + 1.0, 1)),
                        cie3=max(5.0, round(ia_score - 1.0, 1)),
                        assignment_marks=9.0,
                        quiz_marks=4.5,
                        total_cie=round(ia_score + 9.0 + 4.5, 1)
                    )
                    db.session.add(mark)
                else:
                    mark.cie1 = ia_score
                    mark.total_cie = round(ia_score + 13.5, 1)
                    
        db.session.commit()
        print(f"[✓] Seeding completed for {db_uri}!")
        print(f"    - New User Accounts Created: {created_users}")
        print(f"    - Total Student Profiles Synced: {updated_students}")
        print(f"    - Total Students in DB: {Student.query.count()}")

if __name__ == '__main__':
    # 1. Seed SQLite
    app_sqlite = create_app('development')
    seed_database(app_sqlite)
    
    # 2. Seed MySQL if available
    try:
        app_mysql = create_app('mysql')
        seed_database(app_mysql)
    except Exception as e:
        print(f"[!] MySQL sync skipped or encountered: {e}")
