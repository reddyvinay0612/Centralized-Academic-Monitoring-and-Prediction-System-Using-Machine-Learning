import api from './api';

export const principalService = {
  /**
   * Fetch executive institutional KPI overview & risk distribution
   */
  async getOverview() {
    const res = await api.get('/principal/overview');
    return res.data.data;
  },

  /**
   * Fetch departmental comparative benchmarking matrix
   */
  async getDepartmentMatrix() {
    const res = await api.get('/principal/departments');
    return res.data.data;
  },

  /**
   * Fetch class / cohort drilldown data (optionally filtered by deptId)
   */
  async getClassCohorts(deptId = null) {
    const params = deptId ? { dept_id: deptId } : {};
    const res = await api.get('/principal/classes', { params });
    return res.data.data;
  },

  /**
   * Fetch college-wide student registry with multi-attribute filtering & risk scores
   */
  async getCollegeStudents(params = {}) {
    const res = await api.get('/principal/students', { params });
    return res.data;
  },

  /**
   * Download the Executive Institutional Academic Audit PDF
   */
  async downloadExecutiveReport() {
    const res = await api.get('/principal/report/executive', {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'PESITM_Executive_Institutional_Academic_Report.pdf');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    return true;
  },
};

export default principalService;
