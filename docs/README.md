# 🚀 Mployable - AI-Powered Resume Builder

**Mployable** is a sophisticated full-stack platform designed to automate the creation of hyper-tailored resumes. By leveraging LLM-based analysis and semantic matching, Mployable bridges the gap between your technical profile (GitHub/LinkedIn) and specific job requirements.

## ✨ Features

- **Modern Full-Stack Architecture**: React 19.2 frontend with Framer Motion animations and a robust Flask backend.
- **Semantic Tech-Stack Matching**: Intelligent selection of GitHub repositories that best align with job descriptions using skill scoring.
- **Hybrid Profile Sourcing**: 
  - **GitHub**: Automatic repository scraping and language analysis.
  - **LinkedIn**: Structured data import via LinkedIn Data Export ZIP.
- **MongoDB Persistence**: Full database integration for user profiles, resume versioning, job application tracking, and intelligence caching.
- **Gemini AI Integration**: Advanced job description analysis to identify required skills and experience levels.
- **Professional LaTeX Generation**: Dynamic compilation of resume content into high-quality, ATS-friendly PDFs.

## 🛠️ Technology Stack

- **Frontend**: React 19.2, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: Python, Flask (running on port 5001)
- **Database**: MongoDB
- **AI**: Google Gemini API
- **PDF Generation**: LaTeX (pdflatex)
- **Deployment**: Docker, Docker Compose, Nginx

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB instance (local or Atlas)
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Google Gemini API key
- (Optional) GitHub Personal Access Token for higher API rate limits

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/HrishikeshUchake/Mployable.git
cd Mployable
```

### 2. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend && npm install && cd ..
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=your_mongodb_uri_here
GITHUB_TOKEN=your_github_token_here  # Optional
```

### 4. Run the Application

**Manual Start:**
```bash
# Terminal 1
python app.py

# Terminal 2
cd frontend && npm run dev
```

**Using Docker:**
```bash
docker-compose up --build
```

**Get a Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy and paste it into your `.env` file

### 5. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## 📖 Usage

1. **Open your browser** and navigate to `http://localhost:5000`

2. **Enter your profile information:**
   - GitHub username (e.g., `torvalds`)
   - LinkedIn Data Export ZIP (optional)

3. **Paste the job description** for the position you're applying to

4. **Click "Generate Tailored Resume"**

5. **Download your PDF** - The system will automatically download your customized resume!

## 🏗️ Project Structure

```
Mployable/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore rules
├── scrapers/                  # Profile scraping modules
│   ├── github_scraper.py     # GitHub profile scraper
│   └── linkedin_scraper.py   # LinkedIn profile scraper
├── analyzer/                  # Job analysis module
│   └── job_analyzer.py       # Job description analyzer
├── generator/                 # Resume generation modules
│   ├── resume_generator.py   # AI-powered resume generator (Gemini)
│   └── latex_compiler.py     # LaTeX to PDF compiler
└── temp/                      # Temporary files (auto-created)
```

## 🔧 API Endpoints

### `GET /`
Returns the web interface

### `POST /api/generate-resume`
Generates a tailored resume

**Request Body:**
```json
{
  "github_username": "username",
  "job_description": "Full job description text..."
}
```

**OR (with LinkedIn export)**
Multipart form with `github_username`, `job_description`, and `linkedin_data` (file)

**Response:**
Returns PDF file as attachment

### `GET /health`
Health check endpoint

## 🤖 How It Works

1. **Profile Scraping**: 
   - Extracts repositories, languages, and projects from GitHub
   - Parses LinkedIn data export ZIP if provided

2. **Job Analysis**:
   - Parses job description to extract required skills
   - Identifies technical keywords and requirements
   - Determines experience and education requirements

3. **AI Matching** (Google Gemini):
   - Analyzes your profile against job requirements
   - Identifies most relevant projects and skills
   - Generates tailored resume content

4. **PDF Generation**:
   - Creates professional LaTeX-formatted resume
   - Compiles to PDF using pdflatex
   - Returns downloadable PDF file

## 🔒 Privacy & Security

- All processing happens locally on your server
- No profile data is stored permanently
- Temporary files are created only during PDF generation
- API keys are stored in `.env` and not committed to git

## ⚠️ Limitations

- **LinkedIn Scraping**: LinkedIn actively blocks scraping. In production, you should:
  - Use LinkedIn's official API with OAuth
  - Ask users to export their data manually
  - Use a third-party service with proper authorization

- **Rate Limits**: 
  - GitHub API has rate limits (60 requests/hour without token, 5000 with token)
  - Gemini API has usage quotas based on your plan

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is open source and available for hackathon and educational purposes.

## 🎯 Perfect For

- **Hackathons**: Quickly generate resumes for sponsor booths
- **Job Applications**: Tailor your resume for each position
- **Career Fairs**: Create targeted resumes on the fly
- **Students**: Highlight relevant projects for different roles

## 🆘 Troubleshooting

**LaTeX not found:**
- Ensure LaTeX is installed and `pdflatex` is in your PATH
- The app will fall back to text format if LaTeX is unavailable

**API Rate Limits:**
- Add a GitHub Personal Access Token to your `.env` file
- This increases rate limits from 60 to 5000 requests/hour

**Gemini API Errors:**
- Verify your API key is correct
- Check your Gemini API quota
- The app will fall back to basic resume generation without AI

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Built with ❤️ for hackathons and job seekers everywhere!