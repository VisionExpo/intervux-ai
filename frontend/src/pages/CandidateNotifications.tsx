import { useEffect, useState } from "react";
import { authFetch } from "../hooks/useAuth";

interface Notification {
  id: number;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export default function CandidateNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const data = await authFetch<Notification[]>("/api/candidate/notifications");
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notifications");
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await authFetch(`/api/candidate/notifications/${notificationId}/read`, {
        method: "POST"
      });
      
      // Update local state
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true } : n
      ));
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "interview_invite":
        return "📅";
      case "resume_analyzed":
        return "📄";
      case "report_ready":
        return "📊";
      default:
        return "🔔";
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading notifications...</div>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="page-container">
      <div className="notifications-header">
        <h1>Notifications</h1>
        <div className="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/mock-interview">Mock Interview</a>
          <a href="/interview-history">History</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="notifications-content">
        <div className="notifications-summary">
          <span className="notification-count">
            {unreadCount > 0 ? `${unreadCount} unread` : "All caught up!"}
          </span>
        </div>

        {notifications.length === 0 ? (
          <div className="no-notifications">
            <p>No notifications yet.</p>
            <p className="hint">You'll receive notifications about interview invites, resume analysis, and more.</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map((notification) => (
              <div 
                key={notification.id} 
                className={`notification-card ${notification.is_read ? "read" : "unread"}`}
                onClick={() => !notification.is_read && markAsRead(notification.id)}
              >
                <div className="notification-icon">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="notification-body">
                  <p className="notification-message">{notification.message}</p>
                  <span className="notification-time">
                    {new Date(notification.created_at).toLocaleString()}
                  </span>
                </div>
                {!notification.is_read && (
                  <div className="unread-indicator">
                    <span className="unread-dot"></span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

