# 🚀 CareerPilot AI - Backend API

CareerPilot AI is an intelligent backend service designed to analyze resumes, compare them against industry role-skill matrices, and provide actionable career guidance. Powered by **FastAPI**, **PostgreSQL (Neon)**, and **OpenRouter AI**, it automates the resume screening process and generates detailed ATS scores, skill gap analyses, and project recommendations.

---

## ✨ Features

* **📄 Resume Parsing:** Upload resumes in PDF or DOCX format and extract structured text.
* **🧠 AI-Powered Skill Extraction:** Intelligent extraction of technical and soft skills from resumes.
* **📊 Role-Based Gap Analysis:** Compares candidate skills against database records to identify missing skills.
* **📈 ATS Scoring Engine:** Calculates a dynamic Match Score and ATS Score based on industry standards.
* **💡 AI Recommendations:** Integrates with OpenRouter AI to generate:
  * ATS Improvement Suggestions
  * Certification Recommendations
  * Resume Improvement Tips
  * Career Guidance
* **📂 Project Suggestions:** Recommends specific projects based on the targeted role's requirement matrix.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL (Hosted on Neon)
* **ORM:** SQLAlchemy
* **AI Engine:** OpenRouter API (LLM Integration)
* **File Handling:** Python-docx, PyPDF2 (or similar)

---

## 🚀 Getting Started (Local Development)

Follow these steps to set up the backend on your local machine.

### 1. Prerequisites
* Python 3.9+
* PostgreSQL database (Neon DB account)
* OpenRouter API Key

### 2. Clone the Repository
```bash
git clone [https://github.com/Amaanbhardwaj/careerpilot-backend.git](https://github.com/Amaanbhardwaj/careerpilot-backend.git)
cd careerpilot-backend
