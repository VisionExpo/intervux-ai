import { useEffect, useState, useRef } from "react";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Button } from "../components/ui/Button/Button";
import { Input } from "../components/ui/Input/Input";
import { 
  Sparkles, 
  UserRound, 
  FileText, 
  CheckCircle2, 
  Mail, 
  Briefcase, 
  GraduationCap,
  ExternalLink,
  ShieldCheck
} from "lucide-react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import styles from "./CandidateProfile.module.css";
import { API } from "../config/api";
import type { CandidateProfileResponse, ResumeUploadResponse } from "../types/api";

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
    email: "", 
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
          email: data.user_id || "", 
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

      const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
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
        text: `Resume analyzed! Score: ${result.resume_score.toFixed(0)}%`,
      });

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
            <p className={styles.loadingText}>Loading identity...</p>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>Candidate Profile</h1>
          <p className={styles.subtitle}>Your career identity, verified by Intervux AI.</p>
        </div>
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)} className={styles.editBtn}>
            Edit Profile
          </Button>
        )}
      </div>

      {error && (
        <GlassCard className={styles.errorCard}>
          <p className={styles.errorText}>{error}</p>
        </GlassCard>
      )}

      <div className={styles.bentoGrid}>
        {!isEditing ? (
          <>
            {/* 1. Profile Header Card */}
            <GlassCard className={`${styles.bentoCard} ${styles.headerCard}`}>
              <div className={styles.avatarContainer}>
                <UserRound size={64} />
              </div>
              <div className={styles.profileInfo}>
                <h2>{profile?.name}</h2>
                <div className={styles.profileEmail}>
                  <Mail size={16} /> {profile?.user_id}
                </div>
                <div className={styles.profileSocials}>
                  {profile?.github_url && <FaGithub size={20} className={styles.socialIcon} />}
                  {profile?.linkedin_url && <FaLinkedin size={20} className={styles.socialIcon} />}
                </div>
              </div>
            </GlassCard>

            {/* 2. Benchmarks Card */}
            <GlassCard className={`${styles.bentoCard} ${styles.scoresCard}`}>
              <h3 className={styles.cardTitle}><Sparkles size={16} /> AI Benchmarks</h3>
              <div className={styles.scoreRow}>
                <span className={styles.scoreName}>Profile Strength</span>
                <span className={styles.scoreVal}>{profile?.profile_score?.toFixed(0) || 0}%</span>
              </div>
              <div className={styles.scoreRow}>
                <span className={styles.scoreName}>Resume Score</span>
                <span className={styles.scoreVal}>{profile?.resume_score?.toFixed(0) || 0}%</span>
              </div>
              <div className={styles.scoreRow}>
                <span className={styles.scoreName}>Interview Performance</span>
                <span className={styles.scoreVal}>{profile?.interview_score?.toFixed(0) || "N/A"}%</span>
              </div>
              <div className={styles.scoreRow}>
                <span className={styles.scoreName}>Credits Left</span>
                <span className={styles.scoreVal}>{profile?.mock_interviews_remaining || 0}</span>
              </div>
            </GlassCard>

            {/* 3. Summary Card */}
            <GlassCard className={`${styles.bentoCard} ${styles.summaryCard}`}>
              <h3 className={styles.cardTitle}><ShieldCheck size={16} /> Professional Summary</h3>
              <p className={styles.summaryText}>
                {profile?.experience_years ? `Experienced professional with ${profile.experience_years} years in the field. ` : "Eager professional starting their career journey. "}
                {profile?.education ? `Graduated from ${profile.education}. ` : ""}
                Currently focused on mastering {profile?.skills?.slice(0, 3).join(", ") || "new technical domains"}.
                Intervux AI has calculated a profile strength of {profile?.profile_score?.toFixed(0)}% based on your recent activity.
              </p>
            </GlassCard>

            {/* 4. Skills Card */}
            <GlassCard className={`${styles.bentoCard} ${styles.skillsCard}`}>
              <h3 className={styles.cardTitle}><Sparkles size={16} /> Skills Cloud</h3>
              <div className={styles.skillsList}>
                {profile?.skills && profile.skills.length > 0 ? (
                  profile.skills.map((skill, index) => (
                    <span key={index} className={styles.skillTag}>
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className={styles.noSkills}>Upload your resume to detect skills automatically.</p>
                )}
              </div>
            </GlassCard>

            {/* 5. Portfolio & Links Card */}
            <GlassCard className={`${styles.bentoCard} ${styles.linksCard}`}>
              <h3 className={styles.cardTitle}><FileText size={16} /> Artifacts & Links</h3>
              <div className={styles.linksList}>
                <div className={styles.linkItem}>
                  <div className={styles.linkInfo}><FaGithub size={18} /> GitHub</div>
                  {profile?.github_url ? (
                    <a href={profile.github_url} target="_blank" rel="noreferrer"><ExternalLink size={16} /></a>
                  ) : <span className={styles.linkPlaceholder}>Not Linked</span>}
                </div>
                <div className={styles.linkItem}>
                  <div className={styles.linkInfo}><FaLinkedin size={18} /> LinkedIn</div>
                  {profile?.linkedin_url ? (
                    <a href={profile.linkedin_url} target="_blank" rel="noreferrer"><ExternalLink size={16} /></a>
                  ) : <span className={styles.linkPlaceholder}>Not Linked</span>}
                </div>
                
                <div className={styles.resumeCardSection}>
                  <div className={styles.uploadArea}>
                    <input
                      ref={fileInputRef}
                      type="file"
                      id="resume-upload"
                      accept=".pdf,.docx"
                      onChange={handleResumeUpload}
                      className={styles.hiddenInput}
                    />
                    <div className={styles.resumeStatus}>
                      <FileText className={styles.resumeIcon} />
                      <p className={styles.resumeStatusText}>
                        {profile?.resume_url ? "Resume Loaded" : "No Resume"}
                      </p>
                    </div>
                    <div className={styles.resumeActions}>
                      {profile?.resume_url && (
                        <Button 
                          variant="secondary" 
                          size="sm"
                          onClick={() => {
                            const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
                            const fullUrl = profile.resume_url!.startsWith('http') 
                              ? profile.resume_url 
                              : `${API_BASE}${profile.resume_url}`;
                            window.open(fullUrl, '_blank');
                          }}
                        >
                          View
                        </Button>
                      )}
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                      >
                        {isUploading ? "..." : "Upload"}
                      </Button>
                    </div>
                  </div>
                  {uploadMessage && (
                    <div className={`${styles.uploadMessage} ${uploadMessage.type === 'success' ? styles.uploadSuccess : styles.uploadError}`}>
                      {uploadMessage.text}
                    </div>
                  )}
                </div>
              </div>
            </GlassCard>

            {/* 6. Experience & Education */}
            <GlassCard className={`${styles.bentoCard} ${styles.experienceCard}`}>
              <h3 className={styles.cardTitle}><Briefcase size={16} /> Experience</h3>
              <div className={styles.eduExpContent}>
                <p className={styles.primaryText}>{profile?.experience_years || 0} Years Experience</p>
                <p className={styles.secondaryText}>Professional trajectory analyzed via AI models.</p>
              </div>
            </GlassCard>

            <GlassCard className={`${styles.bentoCard} ${styles.educationCard}`}>
              <h3 className={styles.cardTitle}><GraduationCap size={16} /> Education</h3>
              <div className={styles.eduExpContent}>
                <p className={styles.primaryText}>{profile?.education || "Degrees Not Specified"}</p>
                <p className={styles.secondaryText}>Academic background verification.</p>
              </div>
            </GlassCard>
          </>
        ) : (
          <GlassCard className={styles.summaryCard}>
            <form onSubmit={handleSubmit} className={styles.formContent}>
              <div className={styles.editGrid}>
                <div className={styles.inputWrap}>
                  <Input
                    label="Full Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div className={styles.inputWrap}>
                  <Input
                    label="Education"
                    value={formData.education}
                    onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                  />
                </div>
                <div className={styles.inputWrap}>
                  <Input
                    label="Experience (Years)"
                    type="number"
                    value={formData.experience_years}
                    onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
                  />
                </div>
                <div className={styles.inputWrap}>
                  <Input
                    label="GitHub URL"
                    value={formData.github_url}
                    onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                  />
                </div>
                <div className={styles.inputWrap}>
                  <Input
                    label="LinkedIn URL"
                    value={formData.linkedin_url}
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                  />
                </div>
                <div className={styles.fullWidth}>
                  <Input
                    label="Skills (Comma Separated)"
                    value={formData.skills}
                    onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                  />
                </div>
              </div>
              <div className={styles.editActions}>
                <Button type="submit">Save Identity</Button>
                <Button variant="secondary" outline onClick={() => setIsEditing(false)}>Cancel</Button>
              </div>
            </form>
          </GlassCard>
        )}
      </div>
    </div>
  );
}
