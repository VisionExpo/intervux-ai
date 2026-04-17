import { useEffect, useState } from "react";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Calendar, FileText, BarChart3, Bell, Check, BellRing } from "lucide-react";
import styles from "./CandidateNotifications.module.css";

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
        return <Calendar className={styles.iconBlue} size={20} />;
      case "resume_analyzed":
        return <FileText className={styles.iconGreen} size={20} />;
      case "report_ready":
        return <BarChart3 className={styles.iconPurple} size={20} />;
      default:
        return <Bell className={styles.iconIndigo} size={20} />;
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingState}>
        <GlassCard padding="lg">
          <div className={styles.loadingRow}>
            <div className={styles.spinner} />
            <p className={styles.loadingText}>Loading notifications...</p>
          </div>
        </GlassCard>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>
            <BellRing /> Notifications
          </h1>
          <p className={styles.subtitle}>Stay updated on your interview progress and profile analysis.</p>
        </div>
        <div className={styles.badge}>
          {unreadCount > 0 ? `${unreadCount} unread` : "All caught up!"}
        </div>
      </div>

      {error && (
        <GlassCard className={styles.errorCard}>
          <p className={styles.errorText}>{error}</p>
        </GlassCard>
      )}

      <GlassCard padding="none" style={{ overflow: "hidden" }}>
        {notifications.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIconWrap}>
              <Bell size={28} />
            </div>
            <p className={styles.emptyTitle}>No notifications yet</p>
            <p className={styles.emptyDescription}>
              You'll receive notifications about interview invites, resume structure feedback, and AI reports here.
            </p>
          </div>
        ) : (
          <div className={styles.notificationList}>
            {notifications.map((notification) => (
              <div 
                key={notification.id} 
                className={`${styles.notificationItem} ${
                  notification.is_read ? styles.notificationRead : styles.notificationUnread
                }`}
                onClick={() => !notification.is_read && markAsRead(notification.id)}
              >
                <div className={`${styles.iconCircle} ${
                  notification.is_read ? styles.iconCircleRead : styles.iconCircleUnread
                }`}>
                  {getNotificationIcon(notification.type)}
                </div>
                
                <div className={styles.notifContent}>
                  <div className={styles.notifTop}>
                    <p className={notification.is_read ? styles.notifMessageRead : styles.notifMessageUnread}>
                      {notification.message}
                    </p>
                    <div className={styles.notifMeta}>
                      <span className={styles.notifDate}>
                        {new Date(notification.created_at).toLocaleDateString(undefined, { 
                          month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                        })}
                      </span>
                      {!notification.is_read && (
                        <div className={styles.unreadDot} />
                      )}
                    </div>
                  </div>
                  {notification.is_read && (
                    <div className={styles.readIndicator}>
                      <Check size={12} /> Read
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
