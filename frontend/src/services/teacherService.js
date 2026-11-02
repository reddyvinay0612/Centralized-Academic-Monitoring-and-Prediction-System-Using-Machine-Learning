import api from './api';

export const teacherService = {
  /**
   * Fetch all assigned classes and subject teaching units
   */
  async getAssignedClasses() {
    const res = await api.get('/teacher/classes');
    return res.data;
  },

  /**
   * Fetch student roster for a given assigned class with search and risk filters
   */
  async getClassRoster(classId, params = {}) {
    const res = await api.get(`/teacher/classes/${classId}/students`, { params });
    return res.data;
  },

  /**
   * Update student CIE marks with mandatory institutional audit trail reason
   */
  async updateMarks(marksId, marksData) {
    const res = await api.patch(`/teacher/marks/${marksId}`, marksData);
    return res.data;
  },

  /**
   * Fetch marks modification audit history
   */
  async getMarksHistory(marksId) {
    const res = await api.get(`/teacher/marks/${marksId}/history`);
    return res.data.data;
  },

  /**
   * Record attendance for an academic lecture session
   */
  async logAttendance({ classId, subjectId, date, attendanceList }) {
    const res = await api.post('/teacher/attendance', {
      class_id: classId,
      subject_id: subjectId,
      date,
      attendance_list: attendanceList,
    });
    return res.data;
  },

  /**
   * Upload batch CSV for marks or attendance
   */
  async uploadCsv(formData) {
    const res = await api.post('/teacher/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  /**
   * Transmit notice or warning to students and parents
   */
  async notifyStudents({ classId, studentIds, subject, message, sendToParent = true }) {
    const res = await api.post('/teacher/notify', {
      class_id: classId,
      student_ids: studentIds,
      subject,
      message,
      send_to_parent: sendToParent,
    });
    return res.data;
  },

  /**
   * Record faculty mentor guidance or remark
   */
  async addRemark({ studentId, remarkText, actionTaken }) {
    const res = await api.post('/teacher/remarks', {
      student_id: studentId,
      remark_text: remarkText,
      action_taken: actionTaken,
    });
    return res.data;
  },

  /**
   * Phase 10: Bulk/Matrix CIE Marks Entry with VTU top-2 average & mandatory justification
   */
  async bulkUpdateMarks(payload) {
    const res = await api.post('/teacher/marks/bulk', payload);
    return res.data;
  },

  /**
   * Phase 10: Download Marks CSV Template for class & subject
   */
  async downloadMarksTemplate(classId, subjectId) {
    const res = await api.get(`/teacher/classes/${classId}/subjects/${subjectId}/marks/template`, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Marks_Template_Class_${classId}_Subject_${subjectId}.csv`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    return true;
  },

  /**
   * Phase 10: Download Attendance CSV Template for class & subject
   */
  async downloadAttendanceTemplate(classId, subjectId) {
    const res = await api.get(`/teacher/classes/${classId}/subjects/${subjectId}/attendance/template`, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Attendance_Template_Class_${classId}_Subject_${subjectId}.csv`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    return true;
  },

  /**
   * Phase 10: Fetch comprehensive chronological audit history of all mark changes for class & subject
   */
  async getClassSubjectAuditHistory(classId, subjectId) {
    const res = await api.get(`/teacher/classes/${classId}/subjects/${subjectId}/audit-history`);
    return res.data.data;
  },

  /**
   * Phase 10: Override / adjust individual student attendance figure with justification reason
   */
  async updateAttendanceRecord(attendanceId, data) {
    const res = await api.patch(`/teacher/attendance/${attendanceId}`, data);
    return res.data;
  },
};

export default teacherService;
