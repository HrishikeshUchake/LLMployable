# LLMployable - AI-Powered Resume Builder

**LLMployable** is a sophisticated full-stack platform designed to automate the creation of hyper-tailored resumes. By leveraging LLM-based analysis and semantic matching, LLMployable bridges the gap between your technical profile (GitHub/LinkedIn) and specific job requirements.

## Latest Features

- **Modern Full-Stack Architecture**: React 19.2 frontend with Framer Motion animations and a robust Flask backend.
- **AI-Powered Interview Preparation**: Generates tailored interview questions and preparation tips based on specific job descriptions.
- **Interactive Mock Interviews**: Voice-enabled practice sessions integrated with ElevenLabs AI for realistic interview simulation.
- **Semantic Tech-Stack Matching**: Intelligent selection of GitHub repositories that best align with job descriptions using skill scoring.
- **Hybrid Profile Sourcing**: 
  - **GitHub**: Automatic repository scraping and language analysis.
  - **LinkedIn**: Structured data import via LinkedIn Data Export ZIP.
- **MongoDB Persistence**: Full database integration for user profiles, resume versioning, job application tracking, and intelligence caching using MongoDB Atlas.
- **Gemini AI Integration**: Advanced job description analysis to identify required skills and experience levels using Gemini 2.0 Flash models.
- **Professional LaTeX Generation**: Dynamic compilation of resume content into high-quality, ATS-friendly PDFs.

## Technology Stack

### Frontend
- **React 19.2**: Utilizing modern hooks and patterns.
- **Vite**: Ultra-fast build tool and development server.
- **Tailwind CSS**: Utility-first CSS framework for clean, responsive UI.
- **Framer Motion**: Smooth, high-performance web animations.
- **Lucide React**: Clean and consistent iconography.
- **ElevenLabs API**: AI-driven voice synthesis for mock interview simulations.

### Backend
- **Python / Flask**: Scalable RESTful API service.
- **MongoDB**: Document-oriented database for flexible data storage.
- **Google Gemini API**: state-of-the-art LLM for intelligent text analysis.
- **PyGithub & BeautifulSoup**: Specialized scraping tools for profile data.
- **LaTeX (pdflatex)**: Industry-standard typesetting for professional PDFs.

### DevOps
- **Docker & Docker Compose**: Containerized environment for consistent deployment.
- **Nginx**: High-performance web server and reverse proxy.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** & npm
- **MongoDB**: Local instance or MongoDB Atlas URI (dnspython required).
- **LaTeX Distribution**: TeX Live (Linux/macOS) or MiKTeX (Windows).
- **API Keys**: Google Gemini API and optionally ElevenLabs API.

## Getting Started

### 1. Clone & Setup Environments

```bash
git clone https://github.com/HrishikeshUchake/LLMployable.git
cd LLMployable
cp .env.example .env
```

### 2. Backend Installation

```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Frontend Installation

```bash
cd frontend
npm install
cd ..
```

### 4. Running the Application

**Option A: Manual Start**

```bash
# Terminal 1: Backend (Port 5001)
python app.py

# Terminal 2: Frontend (Port 5173)
cd frontend
npm run dev
```

**Option B: Docker (Recommended)**

```bash
docker-compose up --build
```

## How it Works

1. **Profile Connection**: Enter your GitHub username. LLMployable fetches your repos, languages, and contributions.
2. **Contextual Input**: Provide your LinkedIn Data Export for professional experience.
3. **Job Analysis**: Paste a job description. The AI extracts key requirements, tech stack, and experience levels.
4. **Smart Selection**: LLMployable's semantic matcher identifies which of your GitHub projects most closely match the job's tech stack.
5. **PDF Generation**: A customized LaTeX template is filled with the matched data and compiled into a downloadable PDF.
6. **Interview Preparation**: Generate behavioral and technical questions tailored to the job, and practice with voice-enabled AI mock interviews.

---

Built for developers who want to stand out.
