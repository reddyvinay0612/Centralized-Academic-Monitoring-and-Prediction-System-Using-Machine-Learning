import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  Bell,
  CheckCheck,
  Trash2,
  RefreshCw,
  Mail,
  MessageSquare,
  AlertTriangle,
  Clock,
  X,
  User,
  GraduationCap
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import notificationService from '@/services/notificationService';

export default function NotificationCenter({ isOpen, onClose, onUnreadCountChange }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const res = await notificationService.getNotifications({ unread_only: unreadOnly });
      setNotifications(res.data || []);
      if (onUnreadCountChange) {
        onUnreadCountChange(res.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, unreadOnly]);

  const handleMarkAsRead = async (id, e) => {
    e?.stopPropagation();
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, status: 'read', read_at: new Date().toISOString() } : n))
      );
      if (onUnreadCountChange) {
        const count = await notificationService.getUnreadCount();
        onUnreadCountChange(count);
      }
    } catch (err) {
      toast.error('Failed to mark notification as read.');
    }
  };

  const handleMarkAllRead = async () => {
    setActionLoading(true);
    try {
      await notificationService.markAllAsRead();
      toast.success('All notifications marked as read.');
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, status: 'read', read_at: new Date().toISOString() }))
      );
      if (onUnreadCountChange) {
        onUnreadCountChange(0);
      }
    } catch (err) {
      toast.error('Failed to mark all as read.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e?.stopPropagation();
    try {
      await notificationService.deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      toast.success('Notification dismissed.');
      if (onUnreadCountChange) {
        const count = await notificationService.getUnreadCount();
        onUnreadCountChange(count);
      }
    } catch (err) {
      toast.error('Failed to delete notification.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm transition-opacity">
      <div
        className="relative flex h-full w-full max-w-md flex-col border-l border-line bg-surface shadow-2xl transition-transform dark:border-dark-line dark:bg-dark-surface"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-line px-5 py-4 dark:border-dark-line">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <Bell className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-heading text-body font-bold text-ink dark:text-dark-text">
                Notifications & Notices
              </h3>
              <p className="text-[11px] text-muted dark:text-dark-muted">
                Official institutional bulletins & mentor alerts
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={loadNotifications}
              disabled={loading}
              className="rounded-input p-1.5 text-muted hover:bg-page hover:text-ink dark:hover:bg-dark-page dark:hover:text-dark-text"
              title="Refresh notifications"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="rounded-input p-1.5 text-muted hover:bg-page hover:text-ink dark:hover:bg-dark-page dark:hover:text-dark-text"
              title="Close drawer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Filter and Mass Actions Bar */}
        <div className="flex items-center justify-between border-b border-line/60 bg-page/50 px-5 py-2.5 dark:border-dark-line/60 dark:bg-dark-page/50">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setUnreadOnly(false)}
              className={`rounded-pill px-2.5 py-1 text-xs font-semibold transition-colors ${
                !unreadOnly
                  ? 'bg-accent text-white shadow-xs'
                  : 'text-muted hover:text-ink dark:text-dark-muted'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setUnreadOnly(true)}
              className={`rounded-pill px-2.5 py-1 text-xs font-semibold transition-colors ${
                unreadOnly
                  ? 'bg-accent text-white shadow-xs'
                  : 'text-muted hover:text-ink dark:text-dark-muted'
              }`}
            >
              Unread Only
            </button>
          </div>

          <button
            onClick={handleMarkAllRead}
            disabled={actionLoading || notifications.length === 0}
            className="flex items-center gap-1 text-[11px] font-semibold text-accent hover:underline disabled:opacity-40"
          >
            <CheckCheck className="h-3.5 w-3.5" />
            <span>Mark all read</span>
          </button>
        </div>

        {/* Notifications Scroll List */}
        <div className="flex-1 overflow-y-auto divide-y divide-line dark:divide-dark-line">
          {loading ? (
            <div className="flex min-h-[250px] flex-col items-center justify-center gap-2 text-muted">
              <RefreshCw className="h-6 w-6 animate-spin text-accent" />
              <p className="text-caption">Fetching messages...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex min-h-[250px] flex-col items-center justify-center gap-3 p-8 text-center text-muted">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-page text-muted dark:bg-dark-page">
                <Bell className="h-6 w-6" />
              </div>
              <div>
                <p className="font-heading text-body font-bold text-ink dark:text-dark-text">
                  No notifications
                </p>
                <p className="text-caption text-muted dark:text-dark-muted">
                  {unreadOnly ? 'You have caught up with all unread notices.' : 'Your notification inbox is clean.'}
                </p>
              </div>
            </div>
          ) : (
            notifications.map((n) => {
              const isUnread = n.status !== 'read';
              return (
                <div
                  key={n.id}
                  onClick={() => isUnread && handleMarkAsRead(n.id)}
                  className={`group relative p-4 transition-colors cursor-pointer hover:bg-page/70 dark:hover:bg-dark-page/70 ${
                    isUnread ? 'bg-accent/5 dark:bg-accent/10' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {isUnread && (
                        <span className="h-2 w-2 rounded-full bg-accent shrink-0" title="Unread" />
                      )}
                      <h4 className="font-heading text-caption font-bold text-ink dark:text-dark-text line-clamp-1">
                        {n.title}
                      </h4>
                    </div>

                    <span className="text-[10px] text-muted whitespace-nowrap">
                      {n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>

                  {/* Context Subtext (Student or Sender) */}
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-muted dark:text-dark-muted">
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {n.sender_name || 'Administration'}
                    </span>
                    {n.student_name && (
                      <>
                        <span>&bull;</span>
                        <span className="flex items-center gap-1 font-medium text-accent">
                          <GraduationCap className="h-3 w-3" />
                          {n.student_name}
                        </span>
                      </>
                    )}
                  </div>

                  {/* Message Content */}
                  <p className="mt-2 text-caption text-ink/80 dark:text-dark-text/80 leading-relaxed whitespace-pre-wrap">
                    {n.message}
                  </p>

                  {/* Actions on Hover */}
                  <div className="mt-3 flex items-center justify-end gap-2 border-t border-line/40 pt-2 dark:border-dark-line/40 opacity-80 group-hover:opacity-100 transition-opacity">
                    {isUnread && (
                      <button
                        onClick={(e) => handleMarkAsRead(n.id, e)}
                        className="flex items-center gap-1 text-[11px] font-medium text-accent hover:underline"
                        title="Mark as read"
                      >
                        <CheckCheck className="h-3 w-3" /> Mark read
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDelete(n.id, e)}
                      className="flex items-center gap-1 text-[11px] font-medium text-muted hover:text-risk-high transition-colors"
                      title="Dismiss notification"
                    >
                      <Trash2 className="h-3 w-3" /> Dismiss
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
