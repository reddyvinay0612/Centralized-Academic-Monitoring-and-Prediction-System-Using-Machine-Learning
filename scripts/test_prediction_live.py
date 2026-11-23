import urllib.request
import json

for usn in ['4PM23CS071', '4PM23CS035']:
    url = f'http://127.0.0.1:5000/api/predict/pass-fail?usn={usn}'
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode('utf-8'))
        student = data.get('student', {})
        inputs = data.get('input_measures', {})
        pred = data.get('prediction_result', {})
        print('=' * 60)
        print(f"STUDENT: {student.get('name')} ({usn})")
        print(f"  Cumulative CGPA     : {inputs.get('cumulative_cgpa')}")
        print(f"  Active Backlogs     : {inputs.get('active_backlogs')}")
        print(f"  Attendance          : {inputs.get('attendance_percentage')}%")
        print(f"  Prediction Verdict  : {pred.get('prediction')}")
        print(f"  Pass Probability    : {pred.get('pass_probability')}%")
        print(f"  Risk Tier           : {pred.get('risk_tier')}")
        print(f"  Exam Eligibility    : {pred.get('exam_eligibility')}")
        print(f"  Detention Risk      : {pred.get('detention_risk')}")
        print('  Key Factors:')
        for f in pred.get('factors', []):
            print(f'    * {f}')
        print('  Regulatory Checks:')
        for reg_k, reg_v in pred.get('regulatory_checks', {}).items():
            print(f"    * {reg_k}: {reg_v}")
