export interface Project {
  id: string
  name: string
  created_at: string
}

export interface ResumeTemplate {
  id: string
  project_id: string
  role: string
  filename: string
  latex_content: string
  created_at: string
}

export interface JobDescription {
  id: string
  project_id: string
  role: string
  company_name: string
  title: string
  content: string
  created_at: string
}

export interface OptimizationJob {
  id: string
  project_id: string
  status: string
  created_at: string
}

export interface GeneratedResume {
  id: string
  job_id: string
  role: string
  jd_id: string
  jd_title: string
  company_name: string
  ats_before: number | null
  ats_after: number | null
  optimized_latex: string | null
  pdf_path: string | null
  created_at: string
}
