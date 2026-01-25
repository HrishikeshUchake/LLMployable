"""
Mployable - Resume Builder Application

This application scrapes LinkedIn and GitHub profiles, analyzes job descriptions,
and generates tailored resumes as PDFs using LaTeX.
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import os.path
import uuid
from dotenv import load_dotenv

# Import our modules
from database import init_db
from database.repositories import UserRepository, ResumeRepository, JobApplicationRepository
from scrapers.github_scraper import GitHubScraper
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.job_analyzer import JobAnalyzer
from analyzer.interview_generator import InterviewGenerator
from generator.resume_generator import ResumeGenerator
from generator.latex_compiler import LaTeXCompiler
from config.logging_config import setup_logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Setup logging
logger = setup_logging(__name__)

# Initialize database
init_db()

# Initialize components
github_scraper = GitHubScraper()
linkedin_scraper = LinkedInScraper()
job_analyzer = JobAnalyzer()
interview_generator = InterviewGenerator()
resume_generator = ResumeGenerator()
latex_compiler = LaTeXCompiler()

# Simple HTML interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mployable - AI Resume Builder</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
        }
        button:hover {
            opacity: 0.9;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .status.info {
            background: #e3f2fd;
            color: #1565c0;
            display: block;
        }
        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
            display: block;
        }
        .status.error {
            background: #ffebee;
            color: #c62828;
            display: block;
        }
        .example {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Mployable</h1>
        <p class="subtitle">AI-Powered Resume Builder for Hackathons & Job Applications</p>
        
        <form id="resumeForm">
            <div class="form-group">
                <label for="github">GitHub Username:</label>
                <input type="text" id="github" name="github" placeholder="octocat">
                <div class="example">Example: torvalds, gvanrossum</div>
            </div>
            
            <div class="form-group">
                <label for="linkedinFile">Upload LinkedIn Data (ZIP):</label>
                <input type="file" id="linkedinFile" name="linkedinFile" accept=".zip">
                <div class="example">Settings > Data Privacy > Get a copy of your data > Download ZIP</div>
            </div>

            <div class="form-group">
                <label for="jobDescription">Job Description:</label>
                <textarea id="jobDescription" name="jobDescription" placeholder="Paste the job description here..."></textarea>
                <div class="example">Paste the full job description including requirements and responsibilities</div>
            </div>

            <button type="submit" id="submitBtn">Generate Tailored Resume</button>
        </form>

        <div id="status" class="status"></div>
    </div>

    <script>
        document.getElementById('resumeForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitBtn');
            const status = document.getElementById('status');

            const github = document.getElementById('github').value;
            const linkedinFile = document.getElementById('linkedinFile').files[0];
            const jobDescription = document.getElementById('jobDescription').value;

            if (!github && !linkedinFile) {
                status.className = 'status error';
                status.textContent = 'Please provide at least one profile (GitHub username or LinkedIn Data Export)';
                return;
            }

            if (!jobDescription) {
                status.className = 'status error';
                status.textContent = 'Please provide a job description';
                return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = 'Generating Resume...';
            status.className = 'status info';
            status.textContent = '⏳ Scraping profiles and analyzing job description...';

            try {
                let response;
                if (linkedinFile) {
                    const formData = new FormData();
                    formData.append('github_username', github);
                    formData.append('job_description', jobDescription);
                    formData.append('linkedin_data', linkedinFile);

                    response = await fetch('/api/generate-resume', {
                        method: 'POST',
                        body: formData
                    });
                } else {
                    response = await fetch('/api/generate-resume', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            github_username: github,
                            job_description: jobDescription
                        })
                    });
                }

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to generate resume');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'tailored_resume.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                status.className = 'status success';
                status.textContent = '✅ Resume generated successfully! Check your downloads.';
            } catch (error) {
                status.className = 'status error';
                status.textContent = '❌ Error: ' + error.message;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Generate Tailored Resume';
            }
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve the main HTML interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/generate-resume", methods=["POST"])
@app.route("/api/v1/generate-resume", methods=["POST"])
def generate_resume():
    """
    Main endpoint to generate a tailored resume

    Expected payload:
    - JSON: {"github_username": "...", "job_description": "..."}
    - OR Multipart: form fields github_username, job_description AND optional file linkedin_data
    """
    try:
        linkedin_file = None
        user_id = None
        if request.content_type and "multipart/form-data" in request.content_type:
            github_username = request.form.get("github_username", "").strip()
            job_description = request.form.get("job_description", "").strip()
            linkedin_file = request.files.get("linkedin_data")
            user_id = request.form.get("user_id")
        else:
            data = request.json
            github_username = data.get("github_username", "").strip()
            job_description = data.get("job_description", "").strip()
            user_id = data.get("user_id")

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        if not github_username and not linkedin_file:
            return (
                jsonify({"error": "At least one profile or data export is required"}),
                400,
            )

        # Step 1: Scrape profiles
        profile_data = {}

        if github_username:
            github_data = github_scraper.scrape_profile(github_username)
            profile_data["github"] = github_data

        # LinkedIn Data Handling (File Export or URL)
        if linkedin_file and linkedin_file.filename:
            # Save file temporarily
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            temp_filename = f"{uuid.uuid4()}_{linkedin_file.filename}"
            file_path = os.path.join(upload_dir, temp_filename)
            linkedin_file.save(file_path)

            linkedin_data = linkedin_scraper.parse_export(file_path)
            profile_data["linkedin"] = linkedin_data

            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)

        # Step 2: Analyze job description
        job_requirements = job_analyzer.analyze(job_description)

        # Step 3: Refine GitHub projects based on job requirements
        if "github" in profile_data and "repositories" in profile_data["github"]:
            job_skills = job_requirements.get("skills", {})
            relevant_projects = github_scraper.select_relevant_projects(
                profile_data["github"]["repositories"], job_skills
            )
            profile_data["github"]["top_projects"] = relevant_projects

        # Step 4: Generate tailored resume content
        resume_content = resume_generator.generate(profile_data, job_requirements, user_id=user_id)

        # Step 5: Compile to PDF
        pdf_path = latex_compiler.compile(resume_content)

        # Step 6: Move PDF to permanent storage and save to database if user is logged in
        if user_id:
            try:
                # Move PDF to a more permanent 'uploads/resumes' folder
                resumes_dir = os.path.join("uploads", "resumes")
                os.makedirs(resumes_dir, exist_ok=True)
                
                permanent_pdf_name = f"resume_{user_id}_{uuid.uuid4().hex[:8]}.pdf"
                permanent_pdf_path = os.path.join(resumes_dir, permanent_pdf_name)
                
                import shutil
                shutil.copy2(pdf_path, permanent_pdf_path)

                # Create Resume record
                resume_doc = ResumeRepository.create_resume(
                    user_id=user_id,
                    github_username=github_username,
                    job_title=resume_content.get("basics", {}).get("label", "Software Engineer"),
                    job_description=job_description,
                    tailored_content=resume_content,
                    pdf_path=permanent_pdf_path
                )

                # Create Job Application record
                company = resume_content.get("basics", {}).get("company", "Target Company")
                job_url = request.form.get("job_url") if (request.content_type and "multipart/form-data" in request.content_type) else (data.get("job_url") if data else None)
                
                JobApplicationRepository.create_application(
                    user_id=user_id,
                    job_title=resume_content.get("basics", {}).get("label", "Software Engineer"),
                    company=company,
                    resume_id=str(resume_doc.id),
                    job_url=job_url,
                    job_description=job_description
                )
                logger.info(f"Stored resume and application for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to store resume/application: {e}")

        # Validate that the PDF path is within the temp directory (security check)
        abs_temp_dir = os.path.abspath("temp")
        abs_pdf_path = os.path.abspath(pdf_path)
        if not abs_pdf_path.startswith(abs_temp_dir):
            return jsonify({"error": "Invalid file path"}), 500

        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=False,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/interview-prep", methods=["POST"])
@app.route("/api/v1/interview-prep", methods=["POST"])
def interview_prep():
    """
    Endpoint to generate interview preparation tips and questions
    """
    try:
        data = request.get_json(silent=True) or {}
        job_description = data.get("job_description", "").strip()

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        # Analyze job description
        job_requirements = job_analyzer.analyze(job_description)

        # Generate interview prep
        prep_data = interview_generator.generate(job_requirements)

        return jsonify(prep_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Authentication & User Endpoints ---

@app.route("/api/auth/register", methods=["POST"])
@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        if not email or not username or not password:
            return jsonify({"error": "Email, username, and password are required"}), 400

        if UserRepository.get_user_by_email(email):
            return jsonify({"error": "Email already registered"}), 400

        if UserRepository.get_user_by_username(username):
            return jsonify({"error": "Username already taken"}), 400

        user = UserRepository.create_user(email, username, password, first_name, last_name)
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """Authenticate user"""
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = UserRepository.authenticate(username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/resumes/<user_id>", methods=["GET"])
@app.route("/api/v1/user/resumes/<user_id>", methods=["GET"])
def get_user_resumes(user_id):
    """Get all resumes for a user"""
    try:
        resumes = ResumeRepository.get_user_resumes(user_id)
        return jsonify([{
            "id": str(r.id),
            "job_title": r.job_title,
            "github_username": r.github_username,
            "created_at": r.created_at.isoformat(),
            "is_archived": r.is_archived
        } for r in resumes])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/user/resumes/download/<resume_id>", methods=["GET"])
def download_resume(resume_id):
    """Download a previously generated resume PDF"""
    try:
        resume = ResumeRepository.get_resume(resume_id)
        if not resume or not resume.pdf_path:
            return jsonify({"error": "Resume not found"}), 404

        if not os.path.exists(resume.pdf_path):
            return jsonify({"error": "PDF file not found on server"}), 404

        return send_file(
            resume.pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"resume_{resume.job_title.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/user/resumes/preview/<resume_id>", methods=["GET"])
def preview_resume(resume_id):
    """Preview a previously generated resume PDF inline"""
    try:
        resume = ResumeRepository.get_resume(resume_id)
        if not resume or not resume.pdf_path:
            return jsonify({"error": "Resume not found"}), 404

        if not os.path.exists(resume.pdf_path):
            return jsonify({"error": "PDF file not found on server"}), 404

        return send_file(
            resume.pdf_path,
            mimetype="application/pdf",
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/applications/<user_id>", methods=["GET"])
@app.route("/api/v1/user/applications/<user_id>", methods=["GET"])
def get_user_applications(user_id):
    """Get all job applications for a user"""
    try:
        applications = JobApplicationRepository.get_user_applications(user_id)
        return jsonify([{
            "id": str(a.id),
            "job_title": a.job_title,
            "company": a.company,
            "status": a.status,
            "applied_date": a.applied_date.isoformat()
        } for a in applications])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
@app.route("/api/v1/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("temp", exist_ok=True)

    # Get configuration from environment
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    # Default to localhost for security, can be overridden with FLASK_HOST=0.0.0.0
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", os.getenv("PORT", "5001")))

    # Run the application
    app.run(debug=debug_mode, host=host, port=port)
