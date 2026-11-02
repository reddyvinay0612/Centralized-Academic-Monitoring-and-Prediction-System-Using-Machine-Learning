import api from './api';

export const notificationService = {
  /**
   * Fetch paginated notifications with optional unread filter
   */
  async getNotifications(params = {}) {
    const res = await api.get('/notifications', { params });
    return res.data;
  },

  /**
   * Get unread notification badge count
   */
  async getUnreadCount() {
    const res = await api.get('/notifications/unread-count');
    return res.data.unread_count;
  },

  /**
   * Mark individual notification as read
   */
  async markAsRead(notificationId) {
    const res = await api.patch(`/notifications/${notificationId}/read`);
    return res.data;
  },

  /**
   * Mark all notifications for current user as read
   */
  async markAllAsRead() {
    const res = await api.post('/notifications/read-all');
    return res.data;
  },

  /**
   * Broadcast notice or bulletin (Faculty / Admin / Principal)
   */
  async broadcastNotification(payload) {
    const res = await api.post('/notifications/broadcast', payload);
    return res.data;
  },

  /**
   * Dismiss or delete notification
   */
  async deleteNotification(notificationId) {
    const res = await api.delete(`/notifications/${notificationId}`);
    return res.data;
  },
};

export default notificationService;
