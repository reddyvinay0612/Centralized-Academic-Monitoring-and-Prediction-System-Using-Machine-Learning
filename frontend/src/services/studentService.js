import api from './api';

export const studentService = {
  /**
   * Fetch authenticated student profile particulars
   */
  async getProfile(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/me', { params });
    return res.data.data;
  },

  /**
   * Fetch subject-wise and overall attendance metrics
   */
  async getAttendance(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/attendance', { params });
    return res.data.data;
  },

  /**
   * Fetch CIE marks, SGPA progression and CGPA
   */
  async getMarks(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/marks', { params });
    return res.data.data;
  },

  /**
   * Fetch class weekly lecture and laboratory timetable
   */
  async getTimetable(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/timetable', { params });
    return res.data.data;
  },

  /**
   * Fetch academic and institutional announcements
   */
  async getNotifications(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/notifications', { params });
    return res.data.data;
  },

  /**
   * Fetch faculty mentor guidance and observation remarks
   */
  async getRemarks(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/remarks', { params });
    return res.data.data;
  },

  /**
   * Fetch XGBoost ML risk prediction and SHAP explanation factors
   */
  async getPrediction(studentId = null) {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/prediction', { params });
    return res.data.data;
  },

  /**
   * Download official VTU Academic Performance Report PDF
   */
  async downloadReportPdf(studentId = null, usn = 'student') {
    const params = studentId ? { student_id: studentId } : {};
    const res = await api.get('/student/report/download', {
      params,
      responseType: 'blob'
    });

    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `PESITM_Report_${usn}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};

export default studentService;
