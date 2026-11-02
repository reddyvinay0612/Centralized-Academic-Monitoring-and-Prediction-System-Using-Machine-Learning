/**
 * Realistic Mock Academic Dataset for CAMPS-ML
 * PES Institute of Technology and Management (PESITM), Shivamogga - VTU
 * 60 Students with realistic multivariate correlations:
 * - Attendance < 75% + low CIE + backlogs >= 2 -> High Risk (>0.60)
 * - Borderline attendance (72-78%) + 1 backlog -> Medium Risk (0.35-0.60)
 * - High attendance (>85%) + high CIE + 0 backlogs -> Low Risk (<0.35)
 */

export const INITIAL_MODEL_INFO = {
  name: 'XGBoost Academic Risk Classifier + TreeSHAP',
  version: 'v1.0.0',
  algorithm: 'Extreme Gradient Boosting (XGBoost)',
  trainedAt: '2024-10-28T09:30:00Z',
  datasetNote: '50,000 synthetic records with noise + UCI 4,424 benchmark validation',
  accuracy: 0.98,
  precisionMacro: 0.976,
  recallMacro: 0.974,
  f1Macro: 0.9743,
  rocAuc: 0.9992,
  regressorR2: 0.9664,
  regressorMae: 0.278,
  institution: 'PESITM Shivamogga',
  department: 'Computer Science and Engineering',
};

export const INITIAL_USERS = [
  { id: 0, name: 'Dr. Chaitanya Kumar', username: 'principal', email: 'principal@pesitm.edu', role: 'principal', active: true, department: 'Principal Directorate' },
  { id: 1, name: 'Dr. C. G. Halesh', username: 'admin', email: 'admin@pesitm.edu', role: 'admin', active: true, department: 'CSE' },
  { id: 2, name: 'Prof. Anita Rao', username: 'anita.rao', email: 'anita.rao@pesitm.edu', role: 'teacher', active: true, department: 'CSE' },
  { id: 3, name: 'Prof. Karthik Nair', username: 'karthik.nair', email: 'karthik.nair@pesitm.edu', role: 'teacher', active: true, department: 'CSE' },
  { id: 4, name: 'Dr. Sunil Kumar', username: 'sunil.kumar', email: 'sunil.kumar@pesitm.edu', role: 'teacher', active: true, department: 'CSE' },
  { id: 5, name: 'Poorvi V S', username: 'poorvi', email: 'poorvi@pesitm.edu', role: 'student', active: true, usn: '4PM21CS000' },
  { id: 6, name: 'Rohan Verma', username: 'rohan', email: 'rohan@pesitm.edu', role: 'student', active: true, usn: '4PM21CS001' },
  { id: 7, name: 'Smt. Shailaja V (Parent of Poorvi)', username: 'parent.poorvi', email: 'parent.poorvi@gmail.com', role: 'parent', active: true, studentUsn: '4PM21CS000' },
  { id: 8, name: 'Sri. Suresh Verma (Parent of Rohan)', username: 'parent.rohan', email: 'parent.rohan@gmail.com', role: 'parent', active: true, studentUsn: '4PM21CS001' },
];

export const CLASSES = [
  { id: 1, name: '5th Semester CSE', section: 'A', semester: 5, academicYear: '2024-25', totalStudents: 32 },
  { id: 2, name: '5th Semester CSE', section: 'B', semester: 5, academicYear: '2024-25', totalStudents: 28 },
];

export const SUBJECTS = [
  { id: 1, code: '21CS51', name: 'Machine Learning & Applications', credits: 4, teacher: 'Prof. Anita Rao' },
  { id: 2, code: '21CS52', name: 'Database Management Systems', credits: 4, teacher: 'Prof. Karthik Nair' },
  { id: 3, code: '21CS53', name: 'Computer Networks & Cloud', credits: 3, teacher: 'Dr. Sunil Kumar' },
  { id: 4, code: '21CS54', name: 'Theory of Computation', credits: 3, teacher: 'Prof. Anita Rao' },
  { id: 5, code: '21CSL55', name: 'DBMS & Machine Learning Lab', credits: 2, teacher: 'Prof. Karthik Nair' },
];

// Helper to generate deterministic students
function createStudentsList() {
  const students = [
    // Hero Student: Poorvi V S
    {
      id: 1,
      name: 'Poorvi V S',
      usn: '4PM21CS000',
      section: 'A',
      semester: 5,
      attendance: 92.5,
      internalMarks: 46.5,
      backlogs: 0,
      feePaid: true,
      sgpaHistory: [8.85, 8.92, 8.88, 9.05, 9.15],
      riskScore: 0.08,
      riskLevel: 'low',
      mentorId: 2,
      mentorName: 'Prof. Anita Rao',
      parentName: 'Smt. Shailaja V',
      phone: '+91 98800 11223',
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: 94 },
        { subject: 'DBMS', percentage: 91 },
        { subject: 'Computer Networks', percentage: 90 },
        { subject: 'Theory of Computation', percentage: 95 },
        { subject: 'ML & DBMS Lab', percentage: 90 },
      ],
      explanations: [
        { feature: 'High Attendance Rate', displayValue: '92.5%', shap: -0.42 },
        { feature: 'Prior Cumulative CGPA', displayValue: '8.95', shap: -0.38 },
        { feature: 'CIE Assessment Scores', displayValue: '46.5 / 50', shap: -0.29 },
        { feature: 'Zero Active Backlogs', displayValue: '0 arrears', shap: -0.22 },
      ],
      actions: [
        'Eligible for University Department Honors Program in Machine Learning.',
        'Encouraged to submit research project to VTU Student Project Programme (SPP).',
        'Appointed as peer mentor for Theory of Computation tutorial sessions.',
      ],
    },
    // High-Risk Student 1: Rohan Verma
    {
      id: 2,
      name: 'Rohan Verma',
      usn: '4PM21CS001',
      section: 'A',
      semester: 5,
      attendance: 58.0,
      internalMarks: 18.5,
      backlogs: 3,
      feePaid: false,
      sgpaHistory: [5.8, 5.4, 5.1, 4.8, 4.5],
      riskScore: 0.88,
      riskLevel: 'high',
      mentorId: 2,
      mentorName: 'Prof. Anita Rao',
      parentName: 'Sri. Suresh Verma',
      phone: '+91 98450 12345',
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: 55 },
        { subject: 'DBMS', percentage: 62 },
        { subject: 'Computer Networks', percentage: 54 },
        { subject: 'Theory of Computation', percentage: 60 },
        { subject: 'ML & DBMS Lab', percentage: 59 },
      ],
      explanations: [
        { feature: 'Active Arrears / Backlogs', displayValue: '3 subjects', shap: 0.48 },
        { feature: 'Severe Attendance Shortage', displayValue: '58.0% (<75%)', shap: 0.44 },
        { feature: 'Low CIE Assessment Total', displayValue: '18.5 / 50', shap: 0.35 },
        { feature: 'Unpaid Semester Dues', displayValue: 'Pending ₹35,000', shap: 0.12 },
      ],
      actions: [
        'Mandatory enrollment in Saturday remedial coaching for Theory of Computation.',
        'Parent counselling meeting scheduled with Head of Department.',
        'Complete compensatory laboratory makeup sessions to reach 75% attendance.',
      ],
    },
    // High-Risk Student 2: Vikram Aditya
    {
      id: 3,
      name: 'Vikram Aditya',
      usn: '4PM21CS003',
      section: 'B',
      semester: 5,
      attendance: 52.0,
      internalMarks: 15.0,
      backlogs: 4,
      feePaid: false,
      sgpaHistory: [5.2, 4.9, 4.7, 4.2, 4.0],
      riskScore: 0.94,
      riskLevel: 'high',
      mentorId: 3,
      mentorName: 'Prof. Karthik Nair',
      parentName: 'Sri. Raghunath Aditya',
      phone: '+91 98450 33445',
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: 50 },
        { subject: 'DBMS', percentage: 52 },
        { subject: 'Computer Networks', percentage: 48 },
        { subject: 'Theory of Computation', percentage: 55 },
        { subject: 'ML & DBMS Lab', percentage: 55 },
      ],
      explanations: [
        { feature: 'Critical Backlogs Accumulation', displayValue: '4 subjects', shap: 0.52 },
        { feature: 'Chronic Absenteeism', displayValue: '52.0%', shap: 0.46 },
        { feature: 'Declining SGPA Trajectory', displayValue: '4.00 projected', shap: 0.38 },
      ],
      actions: [
        'Immediate referral to Student Welfare Officer for academic probation counselling.',
        'Weekly progress monitoring by assigned faculty mentor.',
      ],
    },
    // Medium-Risk Student 1: Abhishek Kumar
    {
      id: 4,
      name: 'Abhishek Kumar',
      usn: '4PM21CS005',
      section: 'A',
      semester: 5,
      attendance: 73.5,
      internalMarks: 29.0,
      backlogs: 1,
      feePaid: true,
      sgpaHistory: [6.8, 6.7, 6.4, 6.2, 6.4],
      riskScore: 0.48,
      riskLevel: 'medium',
      mentorId: 2,
      mentorName: 'Prof. Anita Rao',
      parentName: 'Sri. Manoj Kumar',
      phone: '+91 98450 55667',
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: 72 },
        { subject: 'DBMS', percentage: 76 },
        { subject: 'Computer Networks', percentage: 74 },
        { subject: 'Theory of Computation', percentage: 71 },
        { subject: 'ML & DBMS Lab', percentage: 75 },
      ],
      explanations: [
        { feature: 'Borderline Attendance', displayValue: '73.5% (<75%)', shap: 0.24 },
        { feature: '1 Uncleared Backlog', displayValue: 'Maths IV', shap: 0.19 },
        { feature: 'Average CIE Marks', displayValue: '29.0 / 50', shap: -0.12 },
      ],
      actions: [
        'Attend 4 extra problem-solving sessions in Machine Learning to boost CIE.',
        'Fast-track preparation for Mathematics IV supplementary examination.',
      ],
    },
    // Low-Risk Student 1: Aditi Bhat
    {
      id: 5,
      name: 'Aditi Bhat',
      usn: '4PM21CS010',
      section: 'A',
      semester: 5,
      attendance: 94.0,
      internalMarks: 45.0,
      backlogs: 0,
      feePaid: true,
      sgpaHistory: [8.6, 8.7, 8.8, 8.9, 9.1],
      riskScore: 0.12,
      riskLevel: 'low',
      mentorId: 2,
      mentorName: 'Prof. Anita Rao',
      parentName: 'Sri. Ganesh Bhat',
      phone: '+91 98450 77889',
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: 96 },
        { subject: 'DBMS', percentage: 92 },
        { subject: 'Computer Networks', percentage: 94 },
        { subject: 'Theory of Computation', percentage: 93 },
        { subject: 'ML & DBMS Lab', percentage: 95 },
      ],
      explanations: [
        { feature: 'Exemplary Attendance', displayValue: '94.0%', shap: -0.40 },
        { feature: 'Strong SGPA Momentum', displayValue: '9.10', shap: -0.35 },
        { feature: 'High CIE Score', displayValue: '45.0 / 50', shap: -0.28 },
      ],
      actions: [
        'Nominated for departmental competitive coding team representation.',
        'Encouraged to pursue AWS/Cloud Computing professional certification.',
      ],
    },
  ];

  // Procedurally generate remaining 55 students with realistic spreads
  const firstNames = ['Varun', 'Kiran', 'Sneha', 'Deepika', 'Arjun', 'Simran', 'Pooja', 'Nikhil', 'Divya', 'Rahul', 'Ananya', 'Megha', 'Kavya', 'Pranav', 'Siddharth', 'Shreya', 'Tanvi', 'Manoj', 'Gautam', 'Aarav'];
  const lastNames = ['Sharma', 'Gowda', 'Nair', 'Patel', 'Bhat', 'Kulkarni', 'Reddy', 'Menon', 'Deshmukh', 'Hegde', 'Sen', 'Joshi', 'Iyer', 'Prasad', 'Rao', 'Shastry'];

  for (let i = 6; i <= 60; i++) {
    const fn = firstNames[(i * 3) % firstNames.length];
    const ln = lastNames[(i * 5) % lastNames.length];
    const sec = i % 2 === 0 ? 'A' : 'B';
    const usnNum = i.toString().padStart(3, '0');
    const usn = `4PM21CS${usnNum}`;

    // Correlate metrics
    let att, cie, backlogs, fee, riskScore, riskLevel, sgpaBase;
    if (i % 6 === 0) {
      // High risk (every ~6th student)
      att = +(55 + (i % 12)).toFixed(1);
      cie = +(16 + (i % 8)).toFixed(1);
      backlogs = (i % 3) + 2;
      fee = i % 12 === 0;
      riskScore = +(0.65 + (i % 25) * 0.01).toFixed(2);
      riskLevel = 'high';
      sgpaBase = 5.2;
    } else if (i % 3 === 0) {
      // Medium risk
      att = +(72 + (i % 6)).toFixed(1);
      cie = +(28 + (i % 8)).toFixed(1);
      backlogs = 1;
      fee = true;
      riskScore = +(0.38 + (i % 18) * 0.01).toFixed(2);
      riskLevel = 'medium';
      sgpaBase = 6.6;
    } else {
      // Low risk / Good standing
      att = +(86 + (i % 12)).toFixed(1);
      cie = +(38 + (i % 10)).toFixed(1);
      backlogs = 0;
      fee = true;
      riskScore = +(0.06 + (i % 22) * 0.01).toFixed(2);
      riskLevel = 'low';
      sgpaBase = 8.4;
    }

    const sgpaHistory = [
      +(sgpaBase - 0.3).toFixed(2),
      +(sgpaBase - 0.1).toFixed(2),
      +(sgpaBase).toFixed(2),
      +(sgpaBase + 0.1).toFixed(2),
      +(sgpaBase + 0.2).toFixed(2),
    ];

    students.push({
      id: i,
      name: `${fn} ${ln}`,
      usn,
      section: sec,
      semester: 5,
      attendance: Math.min(att, 98),
      internalMarks: Math.min(cie, 49),
      backlogs,
      feePaid: fee,
      sgpaHistory,
      riskScore: Math.min(riskScore, 0.96),
      riskLevel,
      mentorId: (i % 3) + 2,
      mentorName: i % 3 === 0 ? 'Prof. Anita Rao' : (i % 3 === 1 ? 'Prof. Karthik Nair' : 'Dr. Sunil Kumar'),
      parentName: `Parent of ${fn}`,
      phone: `+91 98450 ${10000 + i}`,
      subjectAttendance: [
        { subject: 'Machine Learning', percentage: Math.round(att - 2) },
        { subject: 'DBMS', percentage: Math.round(att + 1) },
        { subject: 'Computer Networks', percentage: Math.round(att) },
        { subject: 'Theory of Computation', percentage: Math.round(att - 3) },
        { subject: 'ML & DBMS Lab', percentage: Math.round(att + 2) },
      ],
      explanations: [
        { feature: 'Lecture Attendance', displayValue: `${att}%`, shap: riskLevel === 'high' ? 0.42 : -0.32 },
        { feature: 'Active Backlogs', displayValue: `${backlogs} courses`, shap: backlogs > 0 ? 0.38 : -0.25 },
        { feature: 'CIE Assessment Marks', displayValue: `${cie} / 50`, shap: cie < 25 ? 0.31 : -0.28 },
      ],
      actions: riskLevel === 'high'
        ? ['Attendance recovery program', 'Remedial internal tutoring']
        : ['Maintain regular participation', 'Academic honors coaching'],
    });
  }

  return students;
}

export const STUDENTS = createStudentsList();

export const INITIAL_ALERTS = [
  {
    id: 1,
    studentId: 2,
    studentName: 'Rohan Verma',
    usn: '4PM21CS001',
    riskScore: 0.88,
    riskLevel: 'high',
    reason: 'Attendance 58% falls below mandatory 75% threshold with 3 uncleared backlogs.',
    status: 'open',
    emailSent: true,
    createdAt: '2024-10-30T10:15:00Z',
  },
  {
    id: 2,
    studentId: 3,
    studentName: 'Vikram Aditya',
    usn: '4PM21CS003',
    riskScore: 0.94,
    riskLevel: 'high',
    reason: 'Critical backlog accumulation (4 courses) with CIE internal test average of 15/50.',
    status: 'open',
    emailSent: true,
    createdAt: '2024-10-29T14:30:00Z',
  },
  {
    id: 3,
    studentId: 4,
    studentName: 'Abhishek Kumar',
    usn: '4PM21CS005',
    riskScore: 0.48,
    riskLevel: 'medium',
    reason: 'Attendance warning: 73.5% is borderline with CIE score dip in Machine Learning.',
    status: 'contacted',
    emailSent: true,
    createdAt: '2024-10-28T09:00:00Z',
  },
];

export const INITIAL_REMARKS = [
  {
    id: 1,
    studentId: 2,
    authorName: 'Prof. Anita Rao',
    text: 'Met student regarding attendance shortage. Rohan cited commuter delays and health recovery. Scheduled 2 Saturday remedial lab sessions.',
    createdAt: '2024-10-28T11:20:00Z',
  },
  {
    id: 2,
    studentId: 3,
    authorName: 'Prof. Karthik Nair',
    text: 'Contacted parent Sri. Raghunath Aditya. Recommended departmental peer tutor for Data Structures and Mathematics arrears.',
    createdAt: '2024-10-25T15:45:00Z',
  },
];
