# AI Resume Optimization Platform

## FastAPI + MongoDB + Gemini + LaTeX PDF Generation

---

# 1. Overview

A platform that allows users to:

1. Upload LaTeX resume templates.
2. Add unlimited Job Descriptions for multiple roles.
3. Optimize resumes using Gemini.
4. Generate ATS-optimized LaTeX resumes.
5. Compile LaTeX into PDF.
6. Download generated resumes.
7. Track processing status.

Supported Roles:

* Business Analyst
* Business Intelligence Analyst
* Project Manager
* Product Owner

The platform should support any future role without code changes.

---

# 2. Architecture

```text
Frontend (React.js)

        ↓

FastAPI Backend

        ↓

MongoDB

        ↓

Gemini Service

        ↓

Resume Optimization Queue

        ↓

LaTeX Compiler Service

        ↓

PDF Storage
```

---

# 3. Technology Stack

## Frontend

* React.js
* TypeScript
* TailwindCSS
* Shadcn UI
* React Query
* Zustand

## Backend

* FastAPI
* Pydantic
* Motor (Async MongoDB Driver)
* Uvicorn

## Database

* MongoDB

## AI

* Gemini 2.5 Pro

## PDF Generation

* TeX Live
* pdflatex

## Storage

Local Storage

```text
/storage
    /templates
    /generated
```

Future:

* MinIO
* AWS S3

---

# 4. Project Structure

```text
backend/

├── app/
│
├── api/
│   ├── auth.py
│   ├── projects.py
│   ├── templates.py
│   ├── jds.py
│   ├── optimize.py
│   ├── generated.py
│
├── services/
│   ├── gemini_service.py
│   ├── latex_service.py
│   ├── optimization_service.py
│
├── models/
│   ├── project.py
│   ├── template.py
│   ├── jd.py
│   ├── optimization.py
│
├── db/
│   ├── mongodb.py
│
├── storage/
│
├── main.py
│
└── requirements.txt
```

---

# 5. MongoDB Collections

## projects

```json
{
  "_id": "ObjectId",
  "name": "Athira Resume Project",
  "created_at": "datetime"
}
```

---

## resume_templates

```json
{
  "_id": "ObjectId",
  "project_id": "ObjectId",

  "role": "business_analyst",

  "filename": "Business_Analyst.tex",

  "latex_content": "...",

  "created_at": "datetime"
}
```

---

## job_descriptions

```json
{
  "_id": "ObjectId",

  "project_id": "ObjectId",

  "role": "business_analyst",

  "title": "Business Analyst JD 1",

  "content": "...",

  "created_at": "datetime"
}
```

---

## optimization_jobs

```json
{
  "_id": "ObjectId",

  "project_id": "ObjectId",

  "status": "processing",

  "created_at": "datetime"
}
```

---

## generated_resumes

```json
{
  "_id": "ObjectId",

  "job_id": "ObjectId",

  "role": "business_analyst",

  "jd_id": "ObjectId",

  "ats_before": 72,

  "ats_after": 91,

  "optimized_latex": "...",

  "pdf_path": "/generated/123.pdf",

  "created_at": "datetime"
}
```

---

# 6. Frontend Pages

## Dashboard

```text
Projects

Resume Templates

Job Descriptions

Generated Resumes
```

---

## Create Project

```text
Project Name

[ Create ]
```

---

## Resume Templates

```text
Business Analyst

[ Upload .tex ]

--------------------------------

Business Intelligence

[ Upload .tex ]

--------------------------------

Project Manager

[ Upload .tex ]

--------------------------------

Product Owner

[ Upload .tex ]
```

---

## JD Builder

Dynamic Fields

```text
Business Analyst

[ JD ]

+ Add JD

[ JD ]

+ Add JD

--------------------------------

Project Manager

[ JD ]

+ Add JD
```

Unlimited JDs.

---

## Generated Resumes

```text
Role

JD

ATS Score

PDF

Download
```

---

# 7. Backend APIs

## Create Project

POST

```text
/api/projects
```

Request

```json
{
  "name": "Athira Resume Project"
}
```

---

## Upload Template

POST

```text
/api/templates/upload
```

multipart/form-data

```text
role
file
```

Store:

```text
storage/templates/
```

---

## Add JD

POST

```text
/api/jds
```

```json
{
  "project_id": "...",
  "role": "business_analyst",
  "content": "..."
}
```

---

## Bulk Add JDs

POST

```text
/api/jds/bulk
```

```json
{
  "project_id": "...",
  "role": "business_analyst",
  "items": [
    "...",
    "...",
    "..."
  ]
}
```

---

## Start Optimization

POST

```text
/api/optimize
```

```json
{
  "project_id": "..."
}
```

---

## Get Results

GET

```text
/api/generated
```

---

## Download PDF

GET

```text
/api/generated/{id}/download
```

---

# 8. Optimization Workflow

When user clicks:

```text
Generate Resumes
```

Backend:

### Step 1

Load templates

```text
Business Analyst.tex
Business Intelligence.tex
Project Manager.tex
Product Owner.tex
```

---

### Step 2

Load JDs

```text
BA:
JD1
JD2
JD3

BI:
JD1
JD2

PM:
JD1

PO:
JD1
JD2
```

---

### Step 3

Group by role

```python
{
  "business_analyst":[...],
  "business_intelligence":[...],
  "project_manager":[...],
  "product_owner":[...]
}
```

---

### Step 4

Gemini Request

One Gemini call per role.

Example:

```text
Business Analyst Template

+

JD1

JD2

JD3
```

Gemini returns:

```json
{
  "results":[
    {
      "jd_index":1,
      "optimized_latex":"..."
    },
    {
      "jd_index":2,
      "optimized_latex":"..."
    }
  ]
}
```

---

# 9. Gemini Prompt Strategy

Input:

```text
Resume Template

Multiple JDs
```

Output:

```json
{
  "results":[
    {
      "jd_id":"...",
      "optimized_latex":"..."
    }
  ]
}
```

Strict JSON mode.

---

# 10. PDF Generation

For every optimized resume:

Create temp file

```text
resume.tex
```

Run

```bash
pdflatex -interaction=nonstopmode resume.tex
```

Output

```text
resume.pdf
```

Move to

```text
storage/generated/
```

Save path in MongoDB.

---

# 11. Background Processing

Recommended:

```text
FastAPI
+
Celery
+
Redis
```

Queues:

```text
optimization_queue

pdf_queue
```

Flow:

```text
API Request

↓

Optimization Queue

↓

Gemini

↓

PDF Queue

↓

pdflatex

↓

MongoDB Update
```

---

# 12. Future Features

## ATS Scoring

Dedicated ATS engine.

---

## Cover Letter Generation

Generate role-specific cover letters.

---

## Interview Questions

Generate:

* Technical Questions
* Behavioral Questions
* Model Answers

---

## LinkedIn Optimization

Generate LinkedIn profile.

---

## Resume Versioning

Track revisions.

---

## Multi-Model Support

* Gemini
* OpenAI
* Claude
* DeepSeek
* OpenRouter

---

# MVP Deliverables

Phase 1

✅ Project Management

✅ Template Upload

✅ Dynamic JD Builder

✅ Gemini Optimization

✅ PDF Generation

✅ Download PDFs

✅ MongoDB Storage

✅ FastAPI APIs

✅ Next.js Frontend

Expected Processing:

```text
4 Templates

+

50 JDs

↓

50 Optimized PDFs
```

Generated automatically in one execution.
