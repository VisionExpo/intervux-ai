import { useEffect, useState } from "react";
import { authFetch } from "../../hooks/useAuth";
import type { JobPost, JobPostCreate } from "../../types";

export default function JobPostManager() {
  const [jobPosts, setJobPosts] = useState<JobPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isCreating, setIsCreating] = useState(false);
  const [newJob, setNewJob] = useState<JobPostCreate>({
    title: "",
    description: "",
    required_skills: [],
    experience_level: "Entry",
    employment_type: "Full-Time",
    interview_focus_areas: [],
    evaluation_weights: { technical: 40, communication: 30, problem_solving: 30 },
  });
  
  // Temporary string input to parse JSON or array formats manually
  const [skillsInput, setSkillsInput] = useState("");
  const [focusAreasInput, setFocusAreasInput] = useState("");

  const fetchJobPosts = async () => {
    setIsLoading(true);
    try {
      const posts = await authFetch<JobPost[]>("/api/job-posts");
      setJobPosts(posts);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load job posts");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchJobPosts();
  }, []);

  const handleCreate = async () => {
    try {
      const jobToCreate = {
        ...newJob,
        required_skills: skillsInput.split(",").map(s => s.trim()).filter(Boolean),
        interview_focus_areas: focusAreasInput.split(",").map(f => f.trim()).filter(Boolean),
      };

      await authFetch<JobPost>("/api/job-posts", {
        method: "POST",
        body: JSON.stringify(jobToCreate),
      });
      setIsCreating(false);
      setSkillsInput("");
      setFocusAreasInput("");
      setNewJob({
        title: "",
        description: "",
        required_skills: [],
        experience_level: "Entry",
        employment_type: "Full-Time",
        interview_focus_areas: [],
        evaluation_weights: { technical: 40, communication: 30, problem_solving: 30 },
      });
      void fetchJobPosts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job post");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this job post?")) return;
    try {
      await authFetch(`/api/job-posts/${id}`, { method: "DELETE" });
      void fetchJobPosts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete job post");
    }
  };

  if (isLoading) {
    return <div className="loading">Loading job posts...</div>;
  }

  return (
    <div className="job-post-manager">
      <div className="manager-header">
        <h2>Job Posts</h2>
        <button className="primary-btn" onClick={() => setIsCreating(!isCreating)}>
          {isCreating ? "Cancel" : "Create New Job"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {isCreating && (
        <div className="new-job-form card">
          <h3>Create New Job Post</h3>
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              placeholder="e.g. Senior Frontend Engineer"
              value={newJob.title}
              onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
            />
          </div>
          
          <div className="form-group">
            <label>Description</label>
            <textarea
              placeholder="Job Description..."
              value={newJob.description}
              onChange={(e) => setNewJob({ ...newJob, description: e.target.value })}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Experience Level</label>
              <select
                title="Experience Level"
                value={newJob.experience_level}
                onChange={(e) => setNewJob({ ...newJob, experience_level: e.target.value })}
              >
                <option value="Entry">Entry</option>
                <option value="Mid">Mid</option>
                <option value="Senior">Senior</option>
                <option value="Expert">Expert</option>
              </select>
            </div>
            <div className="form-group">
              <label>Employment Type</label>
              <select
                title="Employment Type"
                value={newJob.employment_type}
                onChange={(e) => setNewJob({ ...newJob, employment_type: e.target.value })}
              >
                <option value="Full-Time">Full-Time</option>
                <option value="Part-Time">Part-Time</option>
                <option value="Contract">Contract</option>
                <option value="Freelance">Freelance</option>
              </select>
            </div>
            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                placeholder="e.g. Remote, San Francisco"
                value={newJob.location || ""}
                onChange={(e) => setNewJob({ ...newJob, location: e.target.value })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Required Skills (comma separated)</label>
            <input
              type="text"
              placeholder="React, TypeScript, CSS"
              value={skillsInput}
              onChange={(e) => setSkillsInput(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Interview Focus Areas (comma separated)</label>
            <input
              type="text"
              placeholder="Frontend Architecture, UI/UX, Performance"
              value={focusAreasInput}
              onChange={(e) => setFocusAreasInput(e.target.value)}
            />
          </div>

          <button className="primary-btn" onClick={handleCreate}>Save Job Post</button>
        </div>
      )}

      <div className="job-list">
        {jobPosts.length === 0 && !isCreating && (
          <p>No job posts available.</p>
        )}
        {jobPosts.map((post) => (
          <div key={post.id} className="job-card card">
            <div className="job-header">
              <h3>{post.title}</h3>
              <span className={`status-badge ${post.status.toLowerCase()}`}>
                {post.status}
              </span>
            </div>
            <p className="job-meta">
              <span>{post.employment_type}</span> &bull; <span>{post.experience_level}</span> 
              {post.location && <span> &bull; {post.location}</span>}
            </p>
            <p className="job-desc">{post.description}</p>
            
            <div className="job-tags">
              <strong>Skills:</strong>{" "}
              {post.required_skills?.map(skill => <span key={skill} className="tag">{skill}</span>)}
            </div>

            <div className="job-actions">
              <button className="danger-btn text-sm" onClick={() => handleDelete(post.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
