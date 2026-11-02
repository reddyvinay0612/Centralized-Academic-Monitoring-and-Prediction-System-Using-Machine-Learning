import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models import (
    User, Department, Course, AcademicYear, Semester, Section,
    Class, Subject, Timetable, Teacher, Parent, Student,
    ParentStudent, TeacherAssignment, Attendance, Mark, MarkHistory,
    SemesterResult, Assignment, Examination, Fee, AuditLog,
    Notification, Alert, Remark, ModelRun, Prediction, Explanation
)

def initialize_database():
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        print("[*] Creating all database tables via SQLAlchemy ORM...")
        db.create_all()
        print("[+] Tables created successfully.")

        # Check if users already exist
        if User.query.first():
            print("[!] Database already populated. Skipping duplicate seeding.")
            return

        print("[*] Seeding benchmark institutional dataset...")
        # 1. Departments
        dept_cse = Department(dept_id=1, dept_code='CSE', name='Computer Science & Engineering')
        dept_ise = Department(dept_id=2, dept_code='ISE', name='Information Science & Engineering')
        dept_ece = Department(dept_id=3, dept_code='ECE', name='Electronics & Communication Engineering')
        dept_csd = Department(dept_id=4, dept_code='CSD', name='Computer Science & Design')
        db.session.add_all([dept_cse, dept_ise, dept_ece, dept_csd])
        db.session.flush()

        # 2. Executive Users: Principal & Admin
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

        # 3. Teachers & HoDs (12 teachers, 3 per dept)
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

        # Update HoD teacher IDs in departments
        dept_cse.hod_teacher_id = 1
        dept_ise.hod_teacher_id = 4
        dept_ece.hod_teacher_id = 7
        dept_csd.hod_teacher_id = 10
        db.session.flush()

        # 4. Classes (12 classes: Sem 3, 5, 7 across 4 depts)
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

        # 5. Subjects
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

        # 6. Teacher Classes (Scoped Access)
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

        # 7. Parents (200 parents)
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

        # 8. Students (240 students, 20 per class)
        dept_codes = {1: 'CS', 2: 'IS', 3: 'EC', 4: 'CD'}
        names = ["Poorvi", "Rohan", "Vikram", "Abhishek", "Sneha", "Aditya", "Pooja", "Darshan",
                 "Ananya", "Kiran", "Varun", "Meghana", "Nikhil", "Bhavana", "Chirag", "Deepika",
                 "Gautam", "Harshitha", "Jayanth", "Keerthi"]
        surnames = ["V S", "Verma", "Aditya", "Kumar", "Rao", "Shetty", "Patil", "Gowda",
                    "Murthy", "Nayak", "Kashyap", "Acharya", "Hegde", "Bhat", "Deshmukh", "Joshi",
                    "Reddy", "Kulkarni", "Prasad", "Naik"]

        created_students = []
        parent_links = []
        student_id = 1

        for cid in range(1, 13):
            did = classes_data[cid-1][5]
            dcode = dept_codes[did]
            for idx in range(20):
                sid = student_id
                usn = f"4PM21{dcode}{sid:03d}"
                uname = usn.lower()
                full_name = f"{names[idx]} {surnames[idx]}"

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
                    fee_status='paid' if sid % 7 != 0 else 'pending'
                )
                created_students.append(stu)

                # Link to parent (parents 1..40 have 2 children, 41..200 have 1)
                pid = ((sid - 1) // 2) + 1 if sid <= 80 else 40 + (sid - 80)
                parent_links.append(ParentStudent(parent_id=pid, student_id=sid, relation='Parent'))

                curr_uid += 1
                student_id += 1

        db.session.add_all(created_students)
        db.session.flush()
        db.session.add_all(parent_links)
        db.session.flush()

        # 9. Attendance, Marks & Semester Results
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
        db.session.commit()

        print("[+] Benchmark database successfully created & populated!")
        print(f"    - Users:          {User.query.count()}")
        print(f"    - Teachers:       {Teacher.query.count()}")
        print(f"    - Departments:    {Department.query.count()}")
        print(f"    - Classes:        {Class.query.count()}")
        print(f"    - Subjects:       {Subject.query.count()}")
        print(f"    - Students:       {Student.query.count()}")
        print(f"    - Parents:        {Parent.query.count()}")
        print(f"    - Parent Links:   {ParentStudent.query.count()}")
        print(f"    - Attendance:     {Attendance.query.count()}")
        print(f"    - Marks:          {Mark.query.count()}")
        print(f"    - Sem Results:    {SemesterResult.query.count()}")

if __name__ == '__main__':
    initialize_database()
