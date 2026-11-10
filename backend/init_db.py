import os
import sys
from datetime import datetime, timedelta

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models import (
    User, Department, Course, AcademicYear, Semester, Section,
    Class, Subject, Timetable, Teacher, Parent, Student,
    ParentStudent, TeacherAssignment, Attendance, Mark, MarkHistory,
    SemesterResult, Assignment, Examination, Fee, FeePayment, AuditLog,
    Notification, Alert, Remark, ModelRun, Prediction, Explanation
)

def initialize_database(reset=False):
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        # Check reset flag from CLI arguments or environment variable
        if reset or '--reset' in sys.argv or os.environ.get('RESET_DB') == 'true':
            print("[*] Performing database clean reset: Dropping existing tables...")
            db.drop_all()
            print("[+] Previous tables dropped cleanly.")

        print("[*] Creating all 23 database tables via SQLAlchemy ORM...")
        db.create_all()
        print("[+] Tables created successfully.")

        # Check if users already exist
        if User.query.first():
            print("[!] Database already populated. To force a clean re-initialization, run with '--reset'.")
            return

        print("[*] Seeding benchmark institutional dataset for PESITM Shivamogga...")

        # --------------------------------------------------------------------------
        # 1. DEPARTMENTS (10 Engineering Branches + 4 Basic Science & Humanities)
        # --------------------------------------------------------------------------
        all_depts_data = [
            (1, 'CSE', 'Computer Science and Engineering'),
            (2, 'ISE', 'Information Science and Engineering'),
            (3, 'ECE', 'Electronics and Communications Engineering'),
            (4, 'CSD', 'Computer Science and Design'),
            (5, 'CIV', 'Civil Engineering'),
            (6, 'EEE', 'Electrical and Electronics Engineering'),
            (7, 'MECH', 'Mechanical Engineering'),
            (8, 'AIML', 'Artificial Intelligence and Machine Learning'),
            (9, 'CE', 'Computer Engineering'),
            (10, 'CSDS', 'Computer Science and Engineering(Data Science)'),
            (11, 'PHY', 'Physics'),
            (12, 'MATH', 'Mathematics'),
            (13, 'CHEM', 'Chemistry'),
            (14, 'HUM', 'Humanities'),
        ]
        created_depts = []
        for did, dcode, dname in all_depts_data:
            created_depts.append(Department(dept_id=did, dept_code=dcode, name=dname))
        db.session.add_all(created_depts)
        db.session.flush()

        dept_cse = created_depts[0]
        dept_ise = created_depts[1]
        dept_ece = created_depts[2]
        dept_csd = created_depts[3]

        # --------------------------------------------------------------------------
        # 2. EXECUTIVE USERS (Principal & Admin)
        # --------------------------------------------------------------------------
        pwd_hash = bcrypt.generate_password_hash('password123').decode('utf-8')

        principal_user = User(
            user_id=1,
            username='principal',
            email='principal@pesitm.edu',
            phone='+91 98450 00001',
            password_hash=pwd_hash,
            role='principal',
            active=True
        )
        admin_user = User(
            user_id=2,
            username='admin',
            email='admin@pesitm.edu',
            phone='+91 98450 00002',
            password_hash=pwd_hash,
            role='admin',
            active=True
        )
        db.session.add_all([principal_user, admin_user])
        db.session.flush()

        # --------------------------------------------------------------------------
        # 3. FACULTY & HODs (12 Teachers, 3 per department)
        # --------------------------------------------------------------------------
        teachers_data = [
            (1, 'Prof. Anita Rao', 'anita.rao', 'anita.rao@pesitm.edu', 'EMP-CSE-01', 'Associate Professor & HoD', 1, 'hod'),
            (2, 'Prof. Karthik Nair', 'karthik.nair', 'karthik.nair@pesitm.edu', 'EMP-CSE-02', 'Assistant Professor', 1, 'teacher'),
            (3, 'Dr. Sunil Kumar', 'sunil.kumar', 'sunil.kumar@pesitm.edu', 'EMP-CSE-03', 'Professor', 1, 'teacher'),
            (4, 'Dr. Manjunath Swamy', 'manjunath.swamy', 'manjunath.swamy@pesitm.edu', 'EMP-ISE-01', 'Professor & HoD', 2, 'hod'),
            (5, 'Prof. Deepa Patil', 'deepa.patil', 'deepa.patil@pesitm.edu', 'EMP-ISE-02', 'Assistant Professor', 2, 'teacher'),
            (6, 'Prof. Harish Gowda', 'harish.gowda', 'harish.gowda@pesitm.edu', 'EMP-ISE-03', 'Associate Professor', 2, 'teacher'),
            (7, 'Dr. Geetha K', 'geetha.k', 'geetha.k@pesitm.edu', 'EMP-ECE-01', 'Professor & HoD', 3, 'hod'),
            (8, 'Prof. Sneha Hegde', 'sneha.hegde', 'sneha.hegde@pesitm.edu', 'EMP-ECE-02', 'Assistant Professor', 3, 'teacher'),
            (9, 'Prof. Ramesh Babu', 'ramesh.babu', 'ramesh.babu@pesitm.edu', 'EMP-ECE-03', 'Associate Professor', 3, 'teacher'),
            (10, 'Dr. Vinayaka B', 'vinayaka.b', 'vinayaka.b@pesitm.edu', 'EMP-CSD-01', 'Associate Professor & HoD', 4, 'hod'),
            (11, 'Prof. Divya Shenoy', 'divya.shenoy', 'divya.shenoy@pesitm.edu', 'EMP-CSD-02', 'Assistant Professor', 4, 'teacher'),
            (12, 'Prof. Raghavendra S', 'raghavendra.s', 'raghavendra.s@pesitm.edu', 'EMP-CSD-03', 'Assistant Professor', 4, 'teacher'),
        ]

        curr_uid = 3
        created_teachers = []
        for tid, name, uname, email, empid, desig, did, role in teachers_data:
            u = User(
                user_id=curr_uid,
                username=uname,
                email=email,
                phone=f'+91 98450 {10000 + tid}',
                password_hash=pwd_hash,
                role=role,
                active=True
            )
            db.session.add(u)
            db.session.flush()

            t = Teacher(
                teacher_id=tid,
                user_id=curr_uid,
                name=name,
                employee_id=empid,
                designation=desig,
                dept_id=did,
                phone=f'+91 98450 {10000 + tid}'
            )
            created_teachers.append(t)
            curr_uid += 1

        db.session.add_all(created_teachers)
        db.session.flush()

        # Link HoDs in Department records
        dept_cse.hod_teacher_id = 1
        dept_ise.hod_teacher_id = 4
        dept_ece.hod_teacher_id = 7
        dept_csd.hod_teacher_id = 10
        db.session.flush()

        # --------------------------------------------------------------------------
        # 4. CLASSES (12 classes: 3rd, 5th, 7th Sem across 4 Departments)
        # --------------------------------------------------------------------------
        classes_data = [
            (1, '3rd Sem CSE', 'A', 3, '2024-25', 1, 2),
            (2, '5th Sem CSE', 'A', 5, '2024-25', 1, 1),
            (3, '7th Sem CSE', 'A', 7, '2024-25', 1, 3),
            (4, '3rd Sem ISE', 'A', 3, '2024-25', 2, 5),
            (5, '5th Sem ISE', 'A', 5, '2024-25', 2, 4),
            (6, '7th Sem ISE', 'A', 7, '2024-25', 2, 6),
            (7, '3rd Sem ECE', 'A', 3, '2024-25', 3, 8),
            (8, '5th Sem ECE', 'A', 5, '2024-25', 3, 7),
            (9, '7th Sem ECE', 'A', 7, '2024-25', 3, 9),
            (10, '3rd Sem CSD', 'A', 3, '2024-25', 4, 11),
            (11, '5th Sem CSD', 'A', 5, '2024-25', 4, 10),
            (12, '7th Sem CSD', 'A', 7, '2024-25', 4, 12),
        ]
        created_classes = [
            Class(class_id=cid, class_name=cname, section=sec, semester=sem,
                  academic_year=ay, dept_id=did, mentor_teacher_id=mid)
            for cid, cname, sec, sem, ay, did, mid in classes_data
        ]
        db.session.add_all(created_classes)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 5. SUBJECTS (12 VTU Subjects across 4 Departments)
        # --------------------------------------------------------------------------
        subjects_data = [
            (1, '21CS51', 'Machine Learning & Applications', 5, 4, 1),
            (2, '21CS52', 'Database Management Systems', 5, 4, 1),
            (3, '21CS53', 'Computer Networks & Cloud', 5, 3, 1),
            (4, '21IS51', 'Cloud Computing & Security', 5, 4, 2),
            (5, '21IS52', 'Software Engineering & Agile', 5, 4, 2),
            (6, '21IS53', 'Big Data Analytics', 5, 3, 2),
            (7, '21EC51', 'Digital Signal Processing', 5, 4, 3),
            (8, '21EC52', 'Embedded Systems & IoT', 5, 4, 3),
            (9, '21EC53', 'VLSI Design & Verification', 5, 3, 3),
            (10, '21CD51', 'UI/UX Design & HCI', 5, 4, 4),
            (11, '21CD52', 'Game Engineering & Graphics', 5, 4, 4),
            (12, '21CD53', 'Generative AI & Vision', 5, 3, 4),
        ]
        created_subjects = [
            Subject(subject_id=sid, subject_code=code, subject_name=sname,
                    semester=sem, credits=cr, dept_id=did)
            for sid, code, sname, sem, cr, did in subjects_data
        ]
        db.session.add_all(created_subjects)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 6. TEACHER ASSIGNMENTS (Role-Based Scoped Access)
        # --------------------------------------------------------------------------
        teacher_assignments = [
            TeacherAssignment(teacher_id=1, class_id=2, subject_id=1),
            TeacherAssignment(teacher_id=2, class_id=2, subject_id=2),
            TeacherAssignment(teacher_id=3, class_id=2, subject_id=3),
            TeacherAssignment(teacher_id=4, class_id=5, subject_id=4),
            TeacherAssignment(teacher_id=5, class_id=5, subject_id=5),
            TeacherAssignment(teacher_id=6, class_id=5, subject_id=6),
            TeacherAssignment(teacher_id=7, class_id=8, subject_id=7),
            TeacherAssignment(teacher_id=8, class_id=8, subject_id=8),
            TeacherAssignment(teacher_id=9, class_id=8, subject_id=9),
            TeacherAssignment(teacher_id=10, class_id=11, subject_id=10),
            TeacherAssignment(teacher_id=11, class_id=11, subject_id=11),
            TeacherAssignment(teacher_id=12, class_id=11, subject_id=12),
        ]
        db.session.add_all(teacher_assignments)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 7. TIMETABLES (Weekly schedules for all classes)
        # --------------------------------------------------------------------------
        timetable_entries = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = [
            ('09:00 AM', '10:00 AM'),
            ('10:00 AM', '11:00 AM'),
            ('11:15 AM', '12:15 PM'),
            ('02:00 PM', '03:00 PM'),
        ]
        for cid in range(1, 13):
            did = classes_data[cid-1][5]
            subjs = [(did-1)*3 + 1, (did-1)*3 + 2, (did-1)*3 + 3]
            t_ids = [(did-1)*3 + 1, (did-1)*3 + 2, (did-1)*3 + 3]

            for d_idx, day in enumerate(days):
                for s_idx, (st_time, end_time) in enumerate(time_slots):
                    s_id = subjs[(d_idx + s_idx) % 3]
                    t_id = t_ids[(d_idx + s_idx) % 3]
                    timetable_entries.append(
                        Timetable(
                            class_id=cid,
                            subject_id=s_id,
                            teacher_id=t_id,
                            day_of_week=day,
                            start_time=st_time,
                            end_time=end_time,
                            room_number=f"LH-{100 + cid}"
                        )
                    )
        db.session.add_all(timetable_entries)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 8. FEES (Annual Institutional Fee Structures)
        # --------------------------------------------------------------------------
        fee_entries = [
            Fee(
                class_id=cid,
                academic_year='2024-25',
                total_amount=85000.00,
                due_date=datetime(2025, 2, 28)
            )
            for cid in range(1, 13)
        ]
        db.session.add_all(fee_entries)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 9. PARENTS & GUARDIANS (200 Families)
        # --------------------------------------------------------------------------
        created_parents = []
        for p in range(1, 201):
            u = User(
                user_id=curr_uid,
                username=f"parent_{p:03d}",
                email=f"parent_{p:03d}@gmail.com",
                phone=f"+91 98800 {20000 + p}",
                password_hash=pwd_hash,
                role='parent',
                active=True
            )
            db.session.add(u)
            db.session.flush()

            par = Parent(
                parent_id=p,
                user_id=curr_uid,
                name=f"Guardian {p:03d}",
                phone=f"+91 98800 {20000 + p}",
                email=f"parent_{p:03d}@gmail.com",
                address="Shivamogga, Karnataka"
            )
            created_parents.append(par)
            curr_uid += 1

        db.session.add_all(created_parents)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 10. STUDENTS (240 Students, 20 per class)
        # --------------------------------------------------------------------------
        dept_codes = {1: 'CS', 2: 'IS', 3: 'EC', 4: 'CD'}
        names = ["Poorvi", "Rohan", "Vikram", "Abhishek", "Sneha", "Aditya", "Pooja", "Darshan",
                 "Ananya", "Kiran", "Varun", "Meghana", "Nikhil", "Bhavana", "Chirag", "Deepika",
                 "Gautam", "Harshitha", "Jayanth", "Keerthi"]
        surnames = ["V S", "Verma", "Aditya", "Kumar", "Rao", "Shetty", "Patil", "Gowda",
                    "Murthy", "Nayak", "Kashyap", "Acharya", "Hegde", "Bhat", "Deshmukh", "Joshi",
                    "Reddy", "Kulkarni", "Prasad", "Naik"]

        created_students = []
        parent_links = []
        fee_payments = []
        student_id = 1

        for cid in range(1, 13):
            did = classes_data[cid-1][5]
            dcode = dept_codes[did]
            for idx in range(20):
                sid = student_id
                usn = f"4PM21{dcode}{sid:03d}"
                uname = usn.lower()
                full_name = f"{names[idx]} {surnames[idx]}"
                is_fee_paid = (sid % 7 != 0)

                u = User(
                    user_id=curr_uid,
                    username=uname,
                    email=f"{uname}@pesitm.edu",
                    phone=f"+91 97400 {10000 + sid}",
                    password_hash=pwd_hash,
                    role='student',
                    active=True
                )
                db.session.add(u)
                db.session.flush()

                stu = Student(
                    student_id=sid,
                    user_id=curr_uid,
                    name=full_name,
                    usn=usn,
                    class_id=cid,
                    academic_status='active',
                    fee_status='paid' if is_fee_paid else 'pending'
                )
                created_students.append(stu)

                # Link to parent (parents 1..40 have 2 children, 41..200 have 1)
                pid = ((sid - 1) // 2) + 1 if sid <= 80 else 40 + (sid - 80)
                parent_links.append(ParentStudent(parent_id=pid, student_id=sid, relation='Parent'))

                # Fee payments
                if is_fee_paid:
                    fee_payments.append(FeePayment(
                        student_id=sid,
                        amount_paid=85000.00,
                        payment_date=datetime(2024, 9, 15),
                        payment_mode='Online/UPI',
                        transaction_reference=f"PESITM-TXN-{sid:04d}",
                        status='completed'
                    ))
                else:
                    fee_payments.append(FeePayment(
                        student_id=sid,
                        amount_paid=45000.00,
                        payment_date=datetime(2024, 9, 20),
                        payment_mode='NEFT / NetBanking',
                        transaction_reference=f"PESITM-TXN-{sid:04d}",
                        status='completed'
                    ))

                curr_uid += 1
                student_id += 1

        db.session.add_all(created_students)
        db.session.flush()
        db.session.add_all(parent_links)
        db.session.add_all(fee_payments)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 11. ATTENDANCE, MARKS & SEMESTER RESULTS
        # --------------------------------------------------------------------------
        att_entries = []
        marks_entries = []
        sem_entries = []

        for sid in range(1, 241):
            cid = ((sid - 1) // 20) + 1
            did = classes_data[cid-1][5]
            subj_start = (did - 1) * 3 + 1

            # Determine risk tier
            if sid % 12 == 2:
                att_pct = 58.0 + (sid % 10)
                cie_base = 18.0 + (sid % 5)
                sgpa_vals = [6.2, 5.8, 5.5, 5.3, 5.1]
            elif sid % 12 in (4, 8):
                att_pct = 74.0 + (sid % 4)
                cie_base = 28.0 + (sid % 6)
                sgpa_vals = [7.2, 7.0, 6.8, 6.9, 6.7]
            else:
                att_pct = 86.0 + (sid % 12)
                cie_base = 42.0 + (sid % 7)
                sgpa_vals = [8.4, 8.6, 8.5, 8.8, 9.0]

            for s_off in range(3):
                sub_id = subj_start + s_off
                tot = 48
                att = int(tot * (att_pct / 100.0))
                att_entries.append(Attendance(student_id=sid, subject_id=sub_id, total_classes=tot,
                                              attended_classes=att, percentage=att_pct))

                cie_part = round(cie_base / 2.5, 1)
                marks_entries.append(Mark(student_id=sid, subject_id=sub_id, cie1=cie_part, cie2=cie_part,
                                          cie3=cie_part, assignment_marks=4.5, quiz_marks=4.0, total_cie=cie_base))

            for sem in range(1, 6):
                sem_entries.append(SemesterResult(student_id=sid, semester=sem, sgpa=sgpa_vals[sem-1],
                                                  credits_earned=20, backlogs=2 if sid % 12 == 2 else 0))

        db.session.add_all(att_entries)
        db.session.add_all(marks_entries)
        db.session.add_all(sem_entries)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 12. MACHINE LEARNING ENGINE: MODEL RUNS, PREDICTIONS & SHAP EXPLANATIONS
        # --------------------------------------------------------------------------
        model_run = ModelRun(
            run_id=1,
            model_name='XGBoost_VTU_AcademicRiskClassifier',
            model_version='v2.4.1',
            algorithm='Extreme Gradient Boosting + TreeSHAP Local Attributions',
            accuracy=0.9420,
            precision_macro=0.9380,
            recall_macro=0.9410,
            f1_macro=0.9395,
            roc_auc=0.9780,
            regressor_r2=0.8920,
            trained_at=datetime.utcnow()
        )
        db.session.add(model_run)
        db.session.flush()

        predictions = []
        explanations = []
        alerts = []
        remarks = []

        for sid in range(1, 241):
            cid = ((sid - 1) // 20) + 1
            mid = classes_data[cid-1][6]  # mentor teacher id

            if sid % 12 == 2:
                # High Risk Tier
                r_level = 'high'
                r_score = 0.88
                outcome = 'Fail'
                p_sgpa = 5.10
                exp_tuples = [
                    ('attendance_pct', '58.0%', 0.4800, 1),
                    ('cie_top2_avg', '18.0 / 50', 0.3600, 2),
                    ('backlog_count', '2 Backlogs', 0.2500, 3),
                    ('prev_sgpa', '5.3 SGPA', 0.1800, 4)
                ]
                alerts.append(Alert(
                    student_id=sid,
                    risk_level='high',
                    reason='Critical Risk: Low attendance (<65%) and CIE-1 deficiency. Immediate mentor intervention advised.',
                    status='open'
                ))
                remarks.append(Remark(
                    student_id=sid,
                    teacher_id=mid,
                    remark_text='Student struggling with core algorithms and missed lab sessions. Assigned remedial classes on Saturdays.',
                    action_taken='Mandatory weekend tutorials and parent contacted.'
                ))
            elif sid % 12 in (4, 8):
                # Medium Risk Tier
                r_level = 'medium'
                r_score = 0.52
                outcome = 'Pass'
                p_sgpa = 6.70
                exp_tuples = [
                    ('attendance_pct', '74.0%', 0.2200, 1),
                    ('cie_top2_avg', '28.0 / 50', 0.1400, 2),
                    ('quiz_score', '6.5 / 10', -0.0800, 3),
                    ('prev_cgpa', '6.8 CGPA', -0.1200, 4)
                ]
                alerts.append(Alert(
                    student_id=sid,
                    risk_level='medium',
                    reason='Attendance Warning: Cumulative attendance is in the condonation border (70-74%).',
                    status='open'
                ))
                remarks.append(Remark(
                    student_id=sid,
                    teacher_id=mid,
                    remark_text='Advised student to attend all upcoming laboratory classes to clear attendance threshold.',
                    action_taken='Allocated peer study partner in classroom.'
                ))
            else:
                # Low Risk / Distinction Tier
                r_level = 'low'
                r_score = 0.12
                outcome = 'Pass'
                p_sgpa = 8.80
                exp_tuples = [
                    ('attendance_pct', '92.0%', -0.4500, 1),
                    ('cie_top2_avg', '44.0 / 50', -0.3800, 2),
                    ('prev_sgpa', '8.8 SGPA', -0.2900, 3),
                    ('backlog_count', '0 Backlogs', -0.1800, 4)
                ]
                if sid % 10 == 1:
                    remarks.append(Remark(
                        student_id=sid,
                        teacher_id=mid,
                        remark_text='Consistently exceptional performance in CIE tests. Recommended for VTU technical symposium.',
                        action_taken='Nominated for Department Hackathon Team.'
                    ))

            pred = Prediction(
                prediction_id=sid,
                student_id=sid,
                model_run_id=1,
                predicted_outcome=outcome,
                risk_score=r_score,
                risk_level=r_level,
                predicted_sgpa=p_sgpa,
                generated_at=datetime.utcnow()
            )
            predictions.append(pred)

            for feat, val, shp, rk in exp_tuples:
                explanations.append(Explanation(
                    prediction_id=sid,
                    feature_name=feat,
                    feature_value=val,
                    shap_value=shp,
                    rank_order=rk
                ))

        db.session.add_all(predictions)
        db.session.flush()
        db.session.add_all(explanations)
        db.session.add_all(alerts)
        db.session.add_all(remarks)
        db.session.flush()

        # --------------------------------------------------------------------------
        # 13. NOTIFICATIONS (Circulars for Students, Parents, Faculty)
        # --------------------------------------------------------------------------
        now = datetime.utcnow()
        notifications = [
            Notification(
                sender_id=1,
                recipient_user_id=s.user_id,
                student_id=s.student_id,
                title='VTU CIE-3 and Semester Examination Schedule',
                message='All students are hereby notified that CIE-3 evaluations and laboratory records verification will commence from 24th November.',
                channel='in_app',
                status='sent',
                created_at=now - timedelta(days=2)
            )
            for s in created_students[:40]
        ]
        # Parent circulars
        notifications.extend([
            Notification(
                sender_id=1,
                recipient_user_id=p.user_id,
                title='Parent-Teacher Interaction Meeting Notice',
                message='Dear Parent/Guardian, the Semester Mid-Term Academic Review meeting is scheduled for Saturday 10:00 AM in the Department Seminar Hall.',
                channel='in_app',
                status='sent',
                created_at=now - timedelta(days=1)
            )
            for p in created_parents[:40]
        ] or [])
        db.session.add_all(notifications)

        # --------------------------------------------------------------------------
        # 14. INITIAL AUDIT LOGS
        # --------------------------------------------------------------------------
        init_audit = AuditLog(
            user_id=2,
            role='admin',
            action='SYSTEM_DATABASE_INITIALIZED',
            target_type='Database',
            target_id=1,
            ip='127.0.0.1'
        )
        db.session.add(init_audit)

        db.session.commit()

        print("[+] Benchmark database successfully created & populated!")
        print("    =========================================================")
        print(f"    - Users:               {User.query.count()}")
        print(f"    - Teachers:            {Teacher.query.count()}")
        print(f"    - Departments:         {Department.query.count()}")
        print(f"    - Classes:             {Class.query.count()}")
        print(f"    - Subjects:            {Subject.query.count()}")
        print(f"    - Students:            {Student.query.count()}")
        print(f"    - Parents:             {Parent.query.count()}")
        print(f"    - Parent Links:        {ParentStudent.query.count()}")
        print(f"    - Attendance:          {Attendance.query.count()}")
        print(f"    - Marks:               {Mark.query.count()}")
        print(f"    - Sem Results:         {SemesterResult.query.count()}")
        print(f"    - Timetables:          {Timetable.query.count()}")
        print(f"    - Fees & Payments:     {Fee.query.count()} fees, {FeePayment.query.count()} payments")
        print(f"    - ML Predictions:      {Prediction.query.count()} with {Explanation.query.count()} SHAP attributions")
        print(f"    - Alerts & Remarks:    {Alert.query.count()} alerts, {Remark.query.count()} remarks")
        print(f"    - Notifications:       {Notification.query.count()}")
        print("    =========================================================")

if __name__ == '__main__':
    initialize_database()
