"""
LLMployable - Production-Ready Resume Builder Application

This application scrapes LinkedIn and GitHub profiles, analyzes job descriptions,
and generates tailored resumes as PDFs using LaTeX.

Production features:
- Comprehensive logging
- Error handling with proper HTTP status codes
- Input validation
- Rate limiting (if Redis configured)
- CORS security
- Health checks
- API documentation
"""

from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory
from flask_cors import CORS
import os
import os.path
from functools import wraps
from datetime import datetime
import uuid

# Import production configurations and utilities
from config import (
    get_config,
    get_logger,
    api_logger,
    error_logger,
    LLMployableException,
    ValidationError,
    InvalidGitHubUsername,
    InvalidJobDescription,
    GitHubAPIError,
    GitHubUserNotFound,
    ResumeGenerationError,
    LaTeXCompilationError,
)
from utils.validators import InputValidator

# Import database
from database import init_db

# Import our modules
from scrapers.github_scraper import GitHubScraper
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.job_analyzer import JobAnalyzer
from analyzer.interview_generator import InterviewGenerator
from generator.resume_generator import ResumeGenerator
from generator.latex_compiler import LaTeXCompiler

# Get configuration
config = get_config()
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__, 
            static_folder=os.environ.get('STATIC_FOLDER', 'static'),
            static_url_path='')

# Initialize database
init_db()

# Configure CORS with security
cors_config = {
    "origins": config.CORS_ORIGINS,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    "supports_credentials": True,
    "max_age": 3600,
}
CORS(app, resources={"/api/*": cors_config})

# Configure Flask
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB max request size

logger.info(f"LLMployable starting in {config.ENVIRONMENT} mode")

# Initialize components
try:
    github_scraper = GitHubScraper()
    linkedin_scraper = LinkedInScraper()
    job_analyzer = JobAnalyzer()
    interview_generator = InterviewGenerator()
    resume_generator = ResumeGenerator()
    latex_compiler = LaTeXCompiler()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}", exc_info=True)
    raise


# HTML TEMPLATE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LLMployable - AI Resume Builder</title>
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
        <h1>🚀 LLMployable</h1>
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

                    response = await fetch('/api/v1/generate-resume', {
                        method: 'POST',
                        body: formData
                    });
                } else {
                    response = await fetch('/api/v1/generate-resume', {
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
                    throw new Error(error.message || error.error || 'Failed to generate resume');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'tailored_resume_' + new Date().toISOString().split('T')[0] + '.pdf';
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


# Middleware for request tracking
@app.before_request
def before_request():
    """Track request metadata"""
    request.request_id = str(uuid.uuid4())[:8]
    request.start_time = datetime.utcnow()
    api_logger.debug(f"[{request.request_id}] {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log response details"""
    rid = getattr(request, "request_id", "unknown")
    if hasattr(request, "start_time"):
        duration = (datetime.utcnow() - request.start_time).total_seconds()
        api_logger.info(
            f"[{rid}] {request.method} {request.path} "
            f"{response.status_code} {duration:.3f}s"
        )
    return response


# Error handlers
@app.errorhandler(LLMployableException)
def handle_llmployable_exception(error):
    """Handle application-specific exceptions"""
    rid = getattr(request, "request_id", "unknown")
    error_logger.warning(f"[{rid}] {error.error_code}: {error.message}")
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return (
        jsonify(
            {"error": "BAD_REQUEST", "message": "Invalid request format", "status": 400}
        ),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return (
        jsonify({"error": "NOT_FOUND", "message": "Endpoint not found", "status": 404}),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    rid = getattr(request, "request_id", "unknown")
    error_logger.error(
        f"[{rid}] Unhandled exception: {error}", exc_info=True
    )
    return (
        jsonify(
            {
                "error": "INTERNAL_ERROR",
                "message": "An internal server error occurred",
                "status": 500,
            }
        ),
        500,
    )


# API endpoints
@app.route("/api/v1/generate-resume", methods=["POST"])
def generate_resume():
    """
    Main endpoint to generate a tailored resume

    Expected payload:
    - JSON: {"github_username": "...", "job_description": "..."}
    - OR Multipart: form fields github_username, job_description AND optional file linkedin_data

    Returns:
        PDF file: application/pdf
    """
    rid = getattr(request, "request_id", "unknown")
    try:
        # Parse and validate request
        linkedin_file = None
        user_id = None

        content_type = request.content_type or ""
        if "multipart/form-data" in content_type:
            github_username = request.form.get("github_username", "").strip()
            job_description = request.form.get("job_description", "").strip()
            linkedin_file = request.files.get("linkedin_data")
            user_id = request.form.get("user_id")
        else:
            data = request.get_json(force=True) if not request.json else request.json
            if not data:
                raise InvalidJobDescription("Request body is empty")

            github_username = data.get("github_username", "").strip()
            job_description = data.get("job_description", "").strip()
            user_id = data.get("user_id")

        logger.info(f"[{rid}] Resume generation request")

        # Validate inputs
        (
            github_username,
            job_description,
        ) = InputValidator.validate_request(
            github_username, job_description
        )

        if (
            not github_username
            and not (linkedin_file and linkedin_file.filename)
        ):
            raise ValidationError(
                "Please provide at least one profile source (GitHub Username or LinkedIn Data Export zip file)"
            )

        logger.info(f"[{rid}] Input validation passed")

        # Step 1: Scrape profiles
        profile_data = {}

        if github_username:
            try:
                logger.debug(
                    f"[{rid}] Scraping GitHub profile: {github_username}"
                )
                github_data = github_scraper.scrape_profile(github_username)
                profile_data["github"] = github_data
                logger.debug(
                    f"[{rid}] GitHub profile scraped successfully"
                )
            except GitHubUserNotFound as e:
                raise InvalidGitHubUsername(github_username)
            except GitHubAPIError as e:
                logger.error(f"[{rid}] GitHub API error: {e}")
                raise

        # LinkedIn Data Handling (File Export or URL)
        if linkedin_file and linkedin_file.filename:
            try:
                logger.debug(f"[{rid}] Parsing LinkedIn data export")
                # Save file temporarily
                temp_filename = f"{uuid.uuid4()}_{linkedin_file.filename}"
                file_path = os.path.join(config.UPLOAD_DIR, temp_filename)
                os.makedirs(config.UPLOAD_DIR, exist_ok=True)
                linkedin_file.save(file_path)

                linkedin_data = linkedin_scraper.parse_export(file_path)
                profile_data["linkedin"] = linkedin_data
                logger.debug(
                    f"[{rid}] LinkedIn export parsed successfully"
                )

                # Cleanup
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(
                    f"[{rid}] LinkedIn export parsing failed: {e}"
                )

        # Step 2: Analyze job description
        try:
            logger.debug(f"[{rid}] Analyzing job description")
            job_requirements = job_analyzer.analyze(job_description)
            logger.debug(f"[{rid}] Job analysis completed")
        except Exception as e:
            logger.error(f"[{rid}] Job analysis failed: {e}")
            raise ResumeGenerationError("Failed to analyze job description")

        # Step 3: Refine GitHub projects based on job requirements
        if "github" in profile_data and "repositories" in profile_data["github"]:
            try:
                logger.debug(
                    f"[{rid}] Refining GitHub projects by relevance"
                )
                job_skills = job_requirements.get("skills", {})
                relevant_projects = github_scraper.select_relevant_projects(
                    profile_data["github"]["repositories"], job_skills
                )
                profile_data["github"]["top_projects"] = relevant_projects
                logger.debug(
                    f"[{rid}] Refined to {len(relevant_projects)} relevant projects"
                )
            except Exception as e:
                logger.warning(
                    f"[{rid}] GitHub project refinement failed: {e}"
                )
                # Continue with default projects if refinement fails

        # Step 4: Generate tailored resume content
        try:
            logger.debug(f"[{rid}] Generating resume content")
            resume_content = resume_generator.generate(profile_data, job_requirements, user_id=user_id)
            logger.debug(f"[{rid}] Resume content generated")
        except Exception as e:
            logger.error(
                f"[{rid}] Resume generation failed: {e}", exc_info=True
            )
            raise ResumeGenerationError(f"Failed to generate resume: {str(e)}")

        # Step 4: Compile to PDF
        try:
            logger.debug(f"[{rid}] Compiling LaTeX to PDF")
            pdf_path = latex_compiler.compile(resume_content)
            logger.debug(f"[{rid}] LaTeX compilation completed")
        except LaTeXCompilationError as e:
            logger.error(f"[{rid}] LaTeX compilation failed: {e}")
            raise
        except Exception as e:
            logger.error(
                f"[{rid}] PDF compilation failed: {e}", exc_info=True
            )
            raise LaTeXCompilationError("Failed to compile resume to PDF")

        # Security: Validate that the PDF path is within the temp directory
        abs_temp_dir = os.path.abspath(config.TEMP_DIR)
        abs_pdf_path = os.path.abspath(pdf_path)
        if not abs_pdf_path.startswith(abs_temp_dir):
            logger.error(f"[{rid}] Invalid file path: {abs_pdf_path}")
            raise ValueError("Invalid file path")

        # Verify file exists
        if not os.path.exists(abs_pdf_path):
            logger.error(f"[{rid}] PDF file not found: {abs_pdf_path}")
            raise ValueError("Generated PDF file not found")

        # Step 6: Create resume and job application records if user is logged in
        if user_id:
            try:
                from database.repositories import ResumeRepository, JobApplicationRepository
                
                # Move PDF to a more permanent 'uploads/resumes' folder
                resumes_dir = os.path.join("uploads", "resumes")
                os.makedirs(resumes_dir, exist_ok=True)
                
                permanent_pdf_name = f"resume_{user_id}_{uuid.uuid4().hex[:8]}.pdf"
                permanent_pdf_path = os.path.join(resumes_dir, permanent_pdf_name)
                
                import shutil
                shutil.copy2(abs_pdf_path, permanent_pdf_path)

                # Create Resume record
                resume_doc = ResumeRepository.create_resume(
                    user_id=user_id,
                    github_username=github_username,
                    job_title=resume_content.get("basics", {}).get("label", "Software Engineer"),
                    job_description=job_description,
                    tailored_content=resume_content,
                    pdf_path=permanent_pdf_path
                )

                company = resume_content.get("basics", {}).get("company", "Target Company")
                job_title = resume_content.get("basics", {}).get("label", "Software Engineer")
                
                # Safe access to job_url based on content type
                is_multipart = "multipart/form-data" in content_type
                job_url = request.form.get("job_url") if is_multipart else (locals().get('data', {}).get("job_url"))

                JobApplicationRepository.create_application(
                    user_id=user_id,
                    job_title=job_title,
                    company=company,
                    resume_id=str(resume_doc.id),
                    job_url=job_url,
                    job_description=job_description
                )
                logger.debug(f"[{rid}] Resume and application records created")
            except Exception as e:
                logger.error(f"[{rid}] Failed to create records: {e}", exc_info=True)

        logger.info(f"[{rid}] Resume generated successfully")

        # Return the PDF file
        return send_file(
            abs_pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f'tailored_resume_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        )

    except LLMployableException:
        # Re-raise application exceptions
        raise
    except Exception as e:
        logger.error(f"[{rid}] Unexpected error: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during resume generation",
                    "status": 500,
                }
            ),
            500,
        )


@app.route("/api/config/elevenlabs", methods=["GET"])
@app.route("/api/v1/config/elevenlabs", methods=["GET"])
def get_elevenlabs_config():
    """Return ElevenLabs Agent ID for the mock interview"""
    config = get_config()
    agent_id = getattr(config, "ELEVENLABS_AGENT_ID", None)
    if not agent_id:
        agent_id = os.getenv("ELEVENLABS_AGENT_ID")
        
    if not agent_id:
        return jsonify({"error": "ElevenLabs Agent ID not configured"}), 404
    return jsonify({"agentId": agent_id})


@app.route("/api/v1/interview-prep", methods=["POST"])
def interview_prep():
    """
    Endpoint to generate interview preparation tips and questions
    """
    rid = getattr(request, "request_id", "unknown")
    try:
        logger.info(f"[{rid}] Interview prep request")
        data = request.json
        if not data:
            raise ValidationError("Request body is required")
            
        job_description = data.get("job_description", "").strip()

        if not job_description:
            raise ValidationError("Job description is required")

        # Analyze job description
        job_requirements = job_analyzer.analyze(job_description)

        # Generate interview prep
        prep_data = interview_generator.generate(job_requirements)

        return jsonify(prep_data)

    except ValidationError as e:
        return jsonify({"error": "VALIDATION_ERROR", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"[{rid}] Interview prep generation failed: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during interview prep generation",
                    "status": 500,
                }
            ),
            500,
        )


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        from database.repositories import UserRepository
        data = request.json
        if not data:
            return jsonify({"error": "VALIDATION_ERROR", "message": "Request body is required"}), 400
            
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        if not email or not username or not password:
            return jsonify({"error": "VALIDATION_ERROR", "message": "Email, username, and password are required"}), 400

        if UserRepository.get_user_by_email(email):
            return jsonify({"error": "CONFLICT", "message": "Email already registered"}), 409

        if UserRepository.get_user_by_username(username):
            return jsonify({"error": "CONFLICT", "message": "Username already taken"}), 409

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
        logger.error(f"Registration failed: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """Authenticate user"""
    try:
        from database.repositories import UserRepository
        data = request.json
        if not data:
            return jsonify({"error": "VALIDATION_ERROR", "message": "Request body is required"}), 400
            
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "VALIDATION_ERROR", "message": "Username and password are required"}), 400

        user = UserRepository.authenticate(username, password)
        if not user:
            return jsonify({"error": "UNAUTHORIZED", "message": "Invalid username or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            }
        })
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/api/v1/user/resumes/<user_id>", methods=["GET"])
def get_user_resumes(user_id):
    """Get all resumes for a user"""
    try:
        from database.repositories import ResumeRepository
        resumes = ResumeRepository.get_user_resumes(user_id)
        return jsonify([{
            "id": str(r.id),
            "job_title": r.job_title,
            "job_description": r.job_description or "",
            "github_username": r.github_username,
            "created_at": r.created_at.isoformat(),
            "is_archived": r.is_archived
        } for r in resumes])
    except Exception as e:
        logger.error(f"Failed to fetch user resumes: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/api/v1/user/resumes/download/<resume_id>", methods=["GET"])
def download_resume(resume_id):
    """Download a previously generated resume PDF"""
    try:
        from database.repositories import ResumeRepository
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
        logger.error(f"Failed to download resume: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/api/v1/user/resumes/preview/<resume_id>", methods=["GET"])
def preview_resume(resume_id):
    """Preview a previously generated resume PDF inline"""
    try:
        from database.repositories import ResumeRepository
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
        logger.error(f"Failed to preview resume: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/api/v1/user/applications/<user_id>", methods=["GET"])
def get_user_applications(user_id):
    """Get all job applications for a user"""
    try:
        from database.repositories import JobApplicationRepository
        applications = JobApplicationRepository.get_user_applications(user_id)
        return jsonify([{
            "id": str(a.id),
            "job_title": a.job_title,
            "company": a.company,
            "status": a.status,
            "applied_date": a.applied_date.isoformat(),
            "job_description": a.job_description or ""
        } for a in applications])
    except Exception as e:
        logger.error(f"Failed to fetch user applications: {e}", exc_info=True)
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": config.VERSION,
            }
        ),
        200,
    )


@app.route("/health/detailed", methods=["GET"])
def health_detailed():
    """Detailed health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.VERSION,
        "components": {
            "github_scraper": "available",
            "linkedin_scraper": "available",
            "job_analyzer": "available",
            "resume_generator": "available",
            "latex_compiler": "available",
        },
        "environment": config.ENVIRONMENT,
    }

    return jsonify(health_status), 200


@app.route("/api/v1/health", methods=["GET"])
def api_health():
    """API health endpoint"""
    return health()


# Frontend routes - Catch-all for React Router
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """Serve the React frontend"""
    # Don't intercept API calls
    if path.startswith("api/"):
        return jsonify({"error": "NOT_FOUND", "message": "API endpoint not found"}), 404
        
    # Check if we should serve static files or the template
    static_file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(static_file_path):
        return send_from_directory(app.static_folder, path)
    
    # Check for index.html in static folder
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    
    # Fallback to HTML_TEMPLATE for development/testing if static folder isn't built
    return render_template_string(HTML_TEMPLATE)


def create_app():
    """Application factory"""
    return app


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    logger.info(f"Starting LLMployable v{config.VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug mode: {config.DEBUG}")

    # Run the application
    # In production, use a WSGI server like gunicorn instead:
    # gunicorn -w 4 -b 0.0.0.0:5000 app_production:create_app()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT, threaded=True)
