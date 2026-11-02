import api from './api';

export const parentService = {
  /**
   * Fetch all children linked to the authenticated parent account
   */
  async getChildren() {
    const res = await api.get('/parent/children');
    return res.data;
  },

  /**
   * Fetch detailed academic summary, attendance, marks, fees for a specific child
   */
  async getChildSummary(childId) {
    const res = await api.get(`/parent/children/${childId}/summary`);
    return res.data.data;
  },

  /**
   * Send an inquiry message to the child's class mentor
   */
  async sendMessage({ studentId, subject, message }) {
    const res = await api.post('/parent/messages', {
      student_id: studentId,
      subject,
      message,
    });
    return res.data;
  },

  /**
   * Retrieve parent messaging communication history
   */
  async getMessages() {
    const res = await api.get('/parent/messages');
    return res.data.data;
  },

  /**
   * Download official VTU child academic report card PDF
   */
  async downloadChildReportPdf(childId, usn = 'child') {
    const res = await api.get(`/parent/children/${childId}/report`, {
      responseType: 'blob'
    });

    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `PESITM_ParentCopy_${usn}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};

export default parentService;
