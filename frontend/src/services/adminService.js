import api from './api';

export const adminService = {
  /**
   * System health & global entity stats
   */
  async getStats() {
    const res = await api.get('/admin/stats');
    return res.data.data;
  },

  /**
   * Fetch paginated & filtered user accounts
   */
  async getUsers(params = {}) {
    const res = await api.get('/admin/users', { params });
    return res.data;
  },

  /**
   * Create new user and associated role profile
   */
  async createUser(userData) {
    const res = await api.post('/admin/users', userData);
    return res.data;
  },

  /**
   * Update user details or toggle account active status
   */
  async updateUser(userId, data) {
    const res = await api.patch(`/admin/users/${userId}`, data);
    return res.data;
  },

  /**
   * Direct password override for an account
   */
  async resetUserPassword(userId, newPassword) {
    const res = await api.post(`/admin/users/${userId}/reset-password`, {
      new_password: newPassword,
    });
    return res.data;
  },

  /**
   * List academic departments
   */
  async getDepartments() {
    const res = await api.get('/admin/departments');
    return res.data.data;
  },

  /**
   * List all classes
   */
  async getClasses() {
    const res = await api.get('/admin/classes');
    return res.data.data;
  },

  /**
   * Create a new class division
   */
  async createClass(classData) {
    const res = await api.post('/admin/classes', classData);
    return res.data;
  },

  /**
   * List curriculum subjects
   */
  async getSubjects(params = {}) {
    const res = await api.get('/admin/subjects', { params });
    return res.data.data;
  },

  /**
   * Create a new subject
   */
  async createSubject(subjectData) {
    const res = await api.post('/admin/subjects', subjectData);
    return res.data;
  },

  /**
   * List faculty teaching allocations
   */
  async getAssignments() {
    const res = await api.get('/admin/assignments');
    return res.data.data;
  },

  /**
   * Create a teaching allocation
   */
  async createAssignment(data) {
    const res = await api.post('/admin/assignments', data);
    return res.data;
  },

  /**
   * Delete a teaching allocation
   */
  async deleteAssignment(assignmentId) {
    const res = await api.delete(`/admin/assignments/${assignmentId}`);
    return res.data;
  },

  /**
   * Map parent to student
   */
  async linkParentStudent(data) {
    const res = await api.post('/admin/parent-students', data);
    return res.data;
  },

  /**
   * Retrieve system audit trail logs
   */
  async getAuditLogs(params = {}) {
    const res = await api.get('/admin/audit-logs', { params });
    return res.data.data;
  },
};

export default adminService;
