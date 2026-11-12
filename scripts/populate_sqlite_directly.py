import os
import sys
import sqlite3

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

sqlite_path = os.path.join(project_root, "backend", "camps_smart_college.db").replace("\\", "/")
sqlite_uri = f"sqlite:///{sqlite_path}"

from backend.app import create_app
from backend.extensions import db
from scripts.ingest_all_pesitm_batches import (
    parse_batch_directory, get_subject_credits, run_pass_fail_prediction
)
from backend.app.models.user import User
from backend.app.models.academic import Department, Class, Subject
from backend.app.models.people import Student, Parent, Teacher, TeacherAssignment
from backend.app.models.grading import Mark, Attendance, SemesterResult
from backend.app.models.system import ModelRun, Prediction, Explanation
import random
import numpy as np
import math

def populate_sqlite():
    print(f"[*] Target SQLite URI: {sqlite_uri}")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    
    with app.app_context():
        engine = create_engine(sqlite_uri)
        db.session.remove()
        db.session.configure(bind=engine)
        
        print(f"[OK] Bound session to: {engine.url}")
        
        # 1. Department
        cse_dept = Department.query.filter_by(dept_code='CSE').first()
        if not cse_dept:
            cse_dept = Department(name="Computer Science & Engineering", dept_code="CSE")
            db.session.add(cse_dept)
            db.session.flush()
        print(f"[OK] Department: {cse_dept.name} (ID: {cse_dept.dept_id})")

        # 2. Classes
        class_6 = Class.query.filter_by(class_name='6th Sem CSE', section='A').first()
        if not class_6:
            class_6 = Class(
                class_name='6th Sem CSE',
                section='A',
                semester=6,
                academic_year='2025-26',
                dept_id=cse_dept.dept_id
            )
            db.session.add(class_6)
            db.session.flush()
            print(f"[CREATED] Class: 6th Sem CSE Section A (ID: {class_6.class_id})")
        else:
            print(f"[EXISTS] Class: 6th Sem CSE Section A (ID: {class_6.class_id})")

        class_8 = Class.query.filter_by(class_name='8th Sem CSE', section='A').first()
        if not class_8:
            class_8 = Class(
                class_name='8th Sem CSE',
                section='A',
                semester=8,
                academic_year='2025-26',
                dept_id=cse_dept.dept_id
            )
            db.session.add(class_8)
            db.session.flush()
            print(f"[CREATED] Class: 8th Sem CSE Section A (ID: {class_8.class_id})")
        else:
            print(f"[EXISTS] Class: 8th Sem CSE Section A (ID: {class_8.class_id})")

        # 3. Parse Both Batches
        b22_students, b22_subjects = parse_batch_directory("data/college_batches/22-26-Batch", "2022-2026")
        b23_students, b23_subjects = parse_batch_directory("data/college_batches/23-27-Batch", "2023-2027")

        print(f"[PARSED] 2022-26 Batch: {len(b22_students)} students")
        print(f"[PARSED] 2023-27 Batch: {len(b23_students)} students")

        # 4. Create Subjects
        all_sem_subjects = {}
        for sems in [b22_subjects, b23_subjects]:
            for sem_num, sub_list in sems.items():
                if sem_num not in all_sem_subjects:
                    all_sem_subjects[sem_num] = []
                for s in sub_list:
                    if not any(x['code'] == s['code'] for x in all_sem_subjects[sem_num]):
                        all_sem_subjects[sem_num].append(s)

        subject_cache = {}
        for sem_num, sub_list in all_sem_subjects.items():
            for s in sub_list:
                s_code = s['code']
                subj = Subject.query.filter_by(subject_code=s_code).first()
                if not subj:
                    subj = Subject(
                        subject_code=s_code,
                        subject_name=s['title'],
                        semester=sem_num,
                        credits=int(math.ceil(s['credits'])),
                        dept_id=cse_dept.dept_id
                    )
                    db.session.add(subj)
                    db.session.flush()
                subject_cache[s_code] = subj

        # 5. Teacher assignments
        teacher_anita = Teacher.query.join(User).filter(User.username == 'anita.rao').first()
        if not teacher_anita:
            teacher_anita = Teacher.query.first()
        if teacher_anita:
            subj_bcs601 = subject_cache.get('BCS601') or Subject.query.filter(Subject.semester == 6).first()
            if subj_bcs601:
                if not TeacherAssignment.query.filter_by(teacher_id=teacher_anita.teacher_id, class_id=class_6.class_id, subject_id=subj_bcs601.subject_id).first():
                    db.session.add(TeacherAssignment(teacher_id=teacher_anita.teacher_id, class_id=class_6.class_id, subject_id=subj_bcs601.subject_id))
            subj_bcs801 = subject_cache.get('BCS801') or Subject.query.filter(Subject.semester == 8).first()
            if subj_bcs801:
                if not TeacherAssignment.query.filter_by(teacher_id=teacher_anita.teacher_id, class_id=class_8.class_id, subject_id=subj_bcs801.subject_id).first():
                    db.session.add(TeacherAssignment(teacher_id=teacher_anita.teacher_id, class_id=class_8.class_id, subject_id=subj_bcs801.subject_id))

        # 6. Model Run
        model_run = ModelRun.query.order_by(ModelRun.run_id.desc()).first()
        if not model_run:
            model_run = ModelRun(
                model_name='CAMPS_XGBoost_PassFail_Classifier',
                model_version='v3.0',
                algorithm='XGBoost + SMOTE + TreeSHAP',
                accuracy=0.9128,
                precision_macro=0.8438,
                recall_macro=0.9000,
                f1_macro=0.8710,
                roc_auc=0.9802,
                regressor_r2=0.8850
            )
            db.session.add(model_run)
            db.session.flush()

        batches_to_process = [
            (b22_students, class_8, 8),
            (b23_students, class_6, 6)
        ]

        added_students = 0
        added_users = 0

        for students_dict, target_cls, max_sem in batches_to_process:
            for usn, s_info in students_dict.items():
                name = s_info['name'] or f"Student {usn}"
                email = f"{usn.lower()}@pesitm.edu"
                p_user_name = f"parent_{usn.lower()}"
                p_email = f"parent_{usn.lower()}@pesitm.edu"
                p_phone = f"984{random.randint(1000000, 9999999)}"

                # Student user
                st_user = User.query.filter_by(username=usn).first()
                if not st_user:
                    st_user = User(username=usn, email=email, role='student')
                    st_user.set_password('password123')
                    db.session.add(st_user)
                    db.session.flush()
                    added_users += 1

                # Parent user
                pr_user = User.query.filter_by(username=p_user_name).first()
                if not pr_user:
                    pr_user = User(username=p_user_name, email=p_email, role='parent')
                    pr_user.set_password('password123')
                    db.session.add(pr_user)
                    db.session.flush()
                    added_users += 1

                # Parent profile
                parent_rec = Parent.query.filter_by(user_id=pr_user.user_id).first()
                if not parent_rec:
                    parent_rec = Parent(
                        user_id=pr_user.user_id,
                        name=f"Parent of {name}",
                        phone=p_phone,
                        email=p_email,
                        address="Shivamogga, Karnataka"
                    )
                    db.session.add(parent_rec)
                    db.session.flush()

                # Student profile
                student_rec = Student.query.filter_by(usn=usn).first()
                if not student_rec:
                    student_rec = Student(
                        user_id=st_user.user_id,
                        name=name,
                        usn=usn,
                        class_id=target_cls.class_id,
                        academic_status='active',
                        fee_status='paid'
                    )
                    db.session.add(student_rec)
                    db.session.flush()
                    added_students += 1
                else:
                    student_rec.class_id = target_cls.class_id
                    if not student_rec.name and name:
                        student_rec.name = name

                # Parent-student link
                ps_link = db.session.execute(
                    db.text("SELECT * FROM parent_students WHERE parent_id = :p AND student_id = :s"),
                    {'p': parent_rec.parent_id, 's': student_rec.student_id}
                ).fetchone()
                if not ps_link:
                    db.session.execute(
                        db.text("INSERT INTO parent_students (parent_id, student_id, relation) VALUES (:p, :s, 'Parent')"),
                        {'p': parent_rec.parent_id, 's': student_rec.student_id}
                    )

                # Semesters & Marks
                sems_data = s_info['semesters']
                all_sgpas = []
                total_credits = 0.0
                weighted_gp = 0.0
                active_backlogs = 0

                for s_num, s_details in sems_data.items():
                    sgpa = s_details['sgpa']
                    backlogs = s_details['backlogs']
                    all_sgpas.append(sgpa)
                    active_backlogs += backlogs
                    credits_earned = int(s_details['total_credits']) - (backlogs * 3)

                    total_credits += s_details['total_credits']
                    weighted_gp += (sgpa * s_details['total_credits'])

                    sr = SemesterResult.query.filter_by(student_id=student_rec.student_id, semester=s_num).first()
                    if not sr:
                        sr = SemesterResult(
                            student_id=student_rec.student_id,
                            semester=s_num,
                            sgpa=sgpa,
                            credits_earned=max(0, credits_earned),
                            backlogs=backlogs
                        )
                        db.session.add(sr)
                    else:
                        sr.sgpa = sgpa
                        sr.credits_earned = max(0, credits_earned)
                        sr.backlogs = backlogs

                    for subj_item in s_details['subjects']:
                        s_obj = subject_cache.get(subj_item['code'])
                        if not s_obj:
                            continue

                        internal_val = subj_item['internal']
                        c1 = round(min(25.0, internal_val * 0.46), 1)
                        c2 = round(min(25.0, internal_val * 0.48), 1)
                        c3 = round(min(25.0, internal_val * 0.44), 1)
                        assign = round(min(10.0, internal_val * 0.16), 1)
                        quiz = round(min(10.0, max(0.0, internal_val - ((c1 + c2) / 2.0) - assign)), 1)
                        total_cie = round(min(50.0, internal_val), 1)

                        existing_m = Mark.query.filter_by(student_id=student_rec.student_id, subject_id=s_obj.subject_id).first()
                        if not existing_m:
                            db.session.add(Mark(
                                student_id=student_rec.student_id,
                                subject_id=s_obj.subject_id,
                                cie1=c1, cie2=c2, cie3=c3,
                                assignment_marks=assign, quiz_marks=quiz,
                                total_cie=total_cie
                            ))

                        existing_att = Attendance.query.filter_by(student_id=student_rec.student_id, subject_id=s_obj.subject_id).first()
                        att_pct = round(min(98.0, max(58.0, 50.0 + (internal_val * 0.95))), 1)
                        total_classes = 40
                        attended_classes = int(round((att_pct / 100.0) * total_classes))

                        if not existing_att:
                            db.session.add(Attendance(
                                student_id=student_rec.student_id,
                                subject_id=s_obj.subject_id,
                                total_classes=total_classes,
                                attended_classes=attended_classes,
                                percentage=att_pct
                            ))

                # Prediction
                cgpa = round(weighted_gp / total_credits, 2) if total_credits > 0 else (all_sgpas[-1] if all_sgpas else 7.0)
                s1_sgpa = sems_data.get(1, {}).get('sgpa', cgpa)
                s2_sgpa = sems_data.get(2, {}).get('sgpa', cgpa)
                s3_sgpa = sems_data.get(3, {}).get('sgpa', cgpa)
                s4_sgpa = sems_data.get(4, {}).get('sgpa', cgpa)

                latest_sem = max(sems_data.keys()) if sems_data else 1
                latest_subjects = sems_data.get(latest_sem, {}).get('subjects', [])
                avg_internal = np.mean([sub['internal'] for sub in latest_subjects]) if latest_subjects else 35.0

                ia1 = round(min(25.0, avg_internal * 0.46), 1)
                ia2 = round(min(25.0, avg_internal * 0.48), 1)
                ia3 = round(min(25.0, avg_internal * 0.44), 1)
                assign = round(min(10.0, avg_internal * 0.16), 1)
                lab = round(min(20.0, avg_internal * 0.38), 1)
                att_est = round(min(98.0, max(58.0, 50.0 + (avg_internal * 0.95))), 1)

                pred_res = run_pass_fail_prediction(
                    ia1=ia1, ia2=ia2, ia3=ia3,
                    assignment=assign, lab=lab,
                    sem1_sgpa=s1_sgpa, sem2_sgpa=s2_sgpa, sem3_sgpa=s3_sgpa, sem4_sgpa=s4_sgpa,
                    cgpa=cgpa, backlogs=active_backlogs, attendance=att_est
                )

                fail_prob = pred_res['fail_probability'] / 100.0
                risk_lvl = 'low' if fail_prob < 0.25 else ('high' if fail_prob > 0.50 else 'medium')
                pred_sgpa = round(min(10.0, max(3.5, cgpa + (0.2 if pred_res['prediction'] == 'PASS' else -0.5))), 2)

                existing_pred = Prediction.query.filter_by(student_id=student_rec.student_id).first()
                if not existing_pred:
                    pred_record = Prediction(
                        student_id=student_rec.student_id,
                        model_run_id=model_run.run_id,
                        predicted_outcome='Pass' if pred_res['prediction'] == 'PASS' else 'Fail',
                        risk_score=fail_prob,
                        risk_level=risk_lvl,
                        predicted_sgpa=pred_sgpa
                    )
                    db.session.add(pred_record)
                    db.session.flush()

                    for r_idx, f_text in enumerate(pred_res.get('factors', [])[:4], 1):
                        db.session.add(Explanation(
                            prediction_id=pred_record.prediction_id,
                            feature_name=f"Driver #{r_idx}",
                            feature_value=str(f_text)[:45],
                            shap_value=-0.15 if 'Positive' in f_text or 'Strong' in f_text else 0.18,
                            rank_order=r_idx
                        ))

        db.session.commit()
        print("\n" + "="*70)
        print("SQLITE POPULATION COMPLETE!")
        print(f"Added {added_students} new student records to SQLite!")
        print(f"Added {added_users} new user accounts to SQLite!")
        print(f"Total students in SQLite now: {Student.query.count()}")
        print(f"Total users in SQLite now: {User.query.count()}")
        print("="*70)

if __name__ == "__main__":
    populate_sqlite()
