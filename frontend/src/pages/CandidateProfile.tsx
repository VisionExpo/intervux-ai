import { useEffect, useState, useRef } from "react";
import { authFetch } from "../hooks/useAuth";

interface ProfileData {
  id: number;
  user_id: string;
  name: string;
  skills: string[];
  experience_years: number | null;
  education: string | null;
  resume_url: string | null;
  resume_score: number | null;
  interview_score: number | null;
  profile_score: number | null;
  github_url: string | null;
  linkedin_url: string | null;
  mock_interviews_remaining: number;
  created_at: string;
}

interface ResumeUploadResponse {
  resume_url: string;
  resume_score: number;
  skills: string[];
  strengths: string[];
  weaknesses: string[];
}

export default function CandidateProfile() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
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
        const data = await authFetch<ProfileData>("/api/candidate/profile");
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

      const updatedProfile = await authFetch<ProfileData>("/api/candidate/profile", {
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

      const response = await fetch("http://localhost:8000/api/candidate/resume", {
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
      const updatedProfile = await authFetch<ProfileData>("/api/candidate/profile");
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
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className="page-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="profile-header">
        <h1>My Profile</h1>
        <div className="nav-links">
          <a href="#/dashboard">Dashboard</a>
          <a href="#/mock-interview">Mock Interview</a>
          <a href="#/interview-history">History</a>
          <a href="#/notifications">Notifications</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="profile-content">
        <div className="profile-scores">
          <div className="score-box">
            <span className="score-label">Profile Score</span>
            <span className="score-number">{profile?.profile_score?.toFixed(0) || 0}</span>
          </div>
          <div className="score-box">
            <span className="score-label">Resume Score</span>
            <span className="score-number">{profile?.resume_score?.toFixed(0) || "N/A"}</span>
          </div>
          <div className="score-box">
            <span className="score-label">Interview Score</span>
            <span className="score-number">{profile?.interview_score?.toFixed(0) || "N/A"}</span>
          </div>
          <div className="score-box">
            <span className="score-label">Interviews Left</span>
            <span className="score-number">{profile?.mock_interviews_remaining || 0}</span>
          </div>
        </div>

        {!isEditing ? (
          <div className="profile-view">
            <div className="profile-section">
              <h3>Basic Information</h3>
              <p><strong>Name:</strong> {profile?.name}</p>
              <p><strong>Email:</strong> {profile?.user_id}</p>
              <p><strong>Experience:</strong> {profile?.experience_years || 0} years</p>
              <p><strong>Education:</strong> {profile?.education || "Not specified"}</p>
            </div>

            <div className="profile-section">
              <h3>Skills</h3>
              <div className="skills-list">
                {profile?.skills && profile.skills.length > 0 ? (
                  profile.skills.map((skill, index) => (
                    <span key={index} className="skill-tag">{skill}</span>
                  ))
                ) : (
                  <p>No skills added yet.</p>
                )}
              </div>
            </div>

            <div className="profile-section">
              <h3>Resume</h3>
              {profile?.resume_url ? (
                <p><strong>Resume:</strong> <a href={profile.resume_url} target="_blank" rel="noopener noreferrer">View Resume</a></p>
              ) : (
                <p>No resume uploaded yet.</p>
              )}
              
              <div className="resume-upload-section">
                <input
                  ref={fileInputRef}
                  type="file"
                  id="resume-upload"
                  accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                  onChange={handleResumeUpload}
                  style={{ display: "none" }}
                />
                <label htmlFor="resume-upload" className="upload-button">
                  {isUploading ? "Uploading..." : profile?.resume_url ? "Upload New Resume" : "Upload Resume"}
                </label>
                <p className="upload-hint">Supported: PDF, DOCX, DOC, PNG, JPG (max 10MB)</p>
              </div>

              {uploadMessage && (
                <div className={`upload-message ${uploadMessage.type}`}>
                  {uploadMessage.text}
                </div>
              )}
            </div>

            <div className="profile-section">
              <h3>Links</h3>
              <p><strong>GitHub:</strong> {profile?.github_url || "Not provided"}</p>
              <p><strong>LinkedIn:</strong> {profile?.linkedin_url || "Not provided"}</p>
            </div>

            <button onClick={() => setIsEditing(true)} className="edit-button">
              Edit Profile
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profile-edit">
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="skills">Skills (comma-separated)</label>
              <input
                id="skills"
                type="text"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="Python, JavaScript, Machine Learning"
              />
            </div>

            <div className="form-group">
              <label htmlFor="experience_years">Experience (years)</label>
              <input
                id="experience_years"
                type="number"
                value={formData.experience_years}
                onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="education">Education</label>
              <input
                id="education"
                type="text"
                value={formData.education}
                onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                placeholder="B.S. Computer Science"
              />
            </div>

            <div className="form-group">
              <label htmlFor="github_url">GitHub URL</label>
              <input
                id="github_url"
                type="url"
                value={formData.github_url}
                onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                placeholder="https://github.com/username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="linkedin_url">LinkedIn URL</label>
              <input
                id="linkedin_url"
                type="url"
                value={formData.linkedin_url}
                onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="save-button">Save Changes</button>
              <button type="button" onClick={() => setIsEditing(false)} className="cancel-button">
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

