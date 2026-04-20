import { useEffect, useState, useRef } from "react";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Button } from "../components/ui/Button/Button";
import { Input } from "../components/ui/Input/Input";
import { Sparkles, UserRound, FileText, CheckCircle2 } from "lucide-react";
import styles from "./CandidateProfile.module.css";
import { API } from "../config/api";
import { CandidateProfileResponse, ResumeUploadResponse } from "../types/api";

export default function CandidateProfile() {
  const [profile, setProfile] = useState<CandidateProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    name: "",
    skills: "",
    experience_years: "",
    education: "",
    github_url: "",
    linkedin_url: "",
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await authFetch<CandidateProfileResponse>(API.profile.candidate);
        setProfile(data);
        setFormData({
          name: data.name || "",
          skills: data.skills?.join(", ") || "",
          experience_years: data.experience_years?.toString() || "",
          education: data.education || "",
          github_url: data.github_url || "",
          linkedin_url: data.linkedin_url || "",
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const updateData = {
        name: formData.name,
        skills: formData.skills.split(",").map((s) => s.trim()).filter(Boolean),
        experience_years: formData.experience_years ? parseInt(formData.experience_years) : null,
        education: formData.education || null,
        github_url: formData.github_url || null,
        linkedin_url: formData.linkedin_url || null,
      };

      const updatedProfile = await authFetch<CandidateProfileResponse>(API.profile.candidate, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateData),
      });

      setProfile(updatedProfile);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadMessage(null);

    try {
      const uploadFormData = new FormData();
      uploadFormData.append("file", file);

      const API_BASE = import.meta.env.VITE_API_URL;
      const response = await fetch(`${API_BASE}/api/candidate/resume`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: uploadFormData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(error.detail || "Failed to upload resume");
      }

      const result: ResumeUploadResponse = await response.json();
      
      setUploadMessage({
        type: "success",
        text: `Resume uploaded! Score: ${result.resume_score.toFixed(0)}% - Skills detected: ${result.skills.join(", ")}`,
      });

      // Refresh profile to get updated data
      const updatedProfile = await authFetch<CandidateProfileResponse>(API.profile.candidate);
      setProfile(updatedProfile);
      setFormData((prev) => ({
        ...prev,
        skills: updatedProfile.skills?.join(", ") || "",
      }));
    } catch (err) {
      setUploadMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to upload resume",
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingState}>
        <GlassCard padding="lg">
          <div className={styles.loadingRow}>
            <Sparkles className={styles.loadingIcon} />
            <p className={styles.loadingText}>Loading profile...</p>
          </div>
        </GlassCard>
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className={styles.loadingState}>
        <GlassCard padding="lg">
          <div className={styles.errorState}>{error}</div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>My Profile</h1>
        <p className={styles.subtitle}>Manage your skills, experience, and resume.</p>
      </div>

      {error && (
        <GlassCard className={styles.errorCard}>
          <p className={styles.errorText}>{error}</p>
        </GlassCard>
      )}

      {/* Score Cards */}
      <div className={styles.scoreGrid}>
        <GlassCard className={styles.scoreCard}>
          <div className={`${styles.scoreOverlay} ${styles.scoreOverlayIndigo}`} />
          <h3 className={styles.scoreLabel}>Profile Score</h3>
          <p className={styles.scoreValue}>{profile?.profile_score?.toFixed(0) || 0}</p>
        </GlassCard>
        
        <GlassCard className={styles.scoreCard}>
          <div className={`${styles.scoreOverlay} ${styles.scoreOverlayBlue}`} />
          <h3 className={styles.scoreLabel}>Resume Score</h3>
          <p className={styles.scoreValue}>{profile?.resume_score?.toFixed(0) || "N/A"}</p>
        </GlassCard>
        
        <GlassCard className={styles.scoreCard}>
          <div className={`${styles.scoreOverlay} ${styles.scoreOverlayGreen}`} />
          <h3 className={styles.scoreLabel}>Interview Score</h3>
          <p className={styles.scoreValue}>{profile?.interview_score?.toFixed(0) || "N/A"}</p>
        </GlassCard>
        
        <GlassCard className={styles.scoreCard}>
          <div className={`${styles.scoreOverlay} ${styles.scoreOverlayPurple}`} />
          <h3 className={styles.scoreLabel}>Interviews Left</h3>
          <p className={styles.scoreValue}>{profile?.mock_interviews_remaining || 0}</p>
        </GlassCard>
      </div>

      <GlassCard padding="lg">
        {!isEditing ? (
          <div className={styles.viewLayout}>
            <div className={styles.viewGrid}>
              {/* Basic Info */}
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>
                  <UserRound size={20} /> Basic Information
                </h3>
                <div className={styles.fieldList}>
                  <p><strong className={styles.fieldLabel}>Name:</strong> {profile?.name}</p>
                  <p><strong className={styles.fieldLabel}>Email:</strong> {profile?.user_id}</p>
                  <p><strong className={styles.fieldLabel}>Experience:</strong> {profile?.experience_years || 0} years</p>
                  <p><strong className={styles.fieldLabel}>Education:</strong> {profile?.education || "Not specified"}</p>
                </div>
              </div>

              {/* Links & Resume */}
              <div className={styles.section}>
                <h3 className={`${styles.sectionTitle} ${styles.sectionTitleGreen}`}>
                  <FileText size={20} /> Documents & Links
                </h3>
                <div className={styles.fieldList}>
                  <p><strong className={styles.fieldLabel}>GitHub:</strong> {profile?.github_url ? <a href={profile.github_url} className={styles.link} target="_blank" rel="noreferrer">View Profile</a> : "Not provided"}</p>
                  <p><strong className={styles.fieldLabel}>LinkedIn:</strong> {profile?.linkedin_url ? <a href={profile.linkedin_url} className={styles.link} target="_blank" rel="noreferrer">View Profile</a> : "Not provided"}</p>
                  <div className={styles.uploadArea}>
                    <input
                      ref={fileInputRef}
                      type="file"
                      id="resume-upload"
                      accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                      onChange={handleResumeUpload}
                      style={{ display: "none" }}
                    />
                    <div className={styles.uploadActions}>
                      {profile?.resume_url && (
                        <Button variant="secondary" onClick={() => window.open(profile.resume_url!, '_blank')}>
                          View Current Resume
                        </Button>
                      )}
                      <Button 
                        variant="secondary" 
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                      >
                        {isUploading ? "Uploading..." : "Upload New Resume"}
                      </Button>
                    </div>
                  </div>
                  {uploadMessage && (
                    <div className={`${styles.uploadMessage} ${uploadMessage.type === 'success' ? styles.uploadSuccess : styles.uploadError}`}>
                      {uploadMessage.type === 'success' && <CheckCircle2 style={{ display: 'inline', marginRight: '0.5rem' }} size={16} />}
                      {uploadMessage.text}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className={styles.skillsSection}>
              <h3 className={styles.skillsSectionTitle}>Skills Set</h3>
              <div className={styles.skillsList}>
                {profile?.skills && profile.skills.length > 0 ? (
                  profile.skills.map((skill, index) => (
                    <span key={index} className={styles.skillTag}>
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className={styles.noSkills}>No skills added yet.</p>
                )}
              </div>
            </div>

            <div className={styles.editActions}>
              <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className={styles.editGrid}>
              <Input
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <Input
                label="Skills (comma-separated)"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="Python, JavaScript, Machine Learning"
              />
              <Input
                label="Experience (years)"
                type="number"
                value={formData.experience_years}
                onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
              />
              <Input
                label="Education"
                value={formData.education}
                onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                placeholder="B.S. Computer Science"
              />
              <Input
                label="GitHub URL"
                type="url"
                value={formData.github_url}
                onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                placeholder="https://github.com/username"
              />
              <Input
                label="LinkedIn URL"
                type="url"
                value={formData.linkedin_url}
                onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            <div className={styles.editActions}>
              <Button type="submit">Save Changes</Button>
              <Button variant="secondary" type="button" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          </form>
        )}
      </GlassCard>
    </div>
  );
}
