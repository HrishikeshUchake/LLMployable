"""
Mployable - Production-Ready Resume Builder Application

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

from flask import Flask, request, jsonify, send_file, render_template_string
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
    MployableException,
    ValidationError,
    InvalidGitHubUsername,
    InvalidJobDescription,
    GitHubAPIError,
    GitHubUserNotFound,
    ResumeGenerationError,
    LaTeXCompilationError,
)
from utils.validators import InputValidator

# Import our modules
from scrapers.github_scraper import GitHubScraper
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.job_analyzer import JobAnalyzer
from generator.resume_generator import ResumeGenerator
from generator.latex_compiler import LaTeXCompiler

# Get configuration
config = get_config()
logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)

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

logger.info(f"Mployable starting in {config.ENVIRONMENT} mode")

# Initialize components
try:
    github_scraper = GitHubScraper()
    linkedin_scraper = LinkedInScraper()
    job_analyzer = JobAnalyzer()
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
                <label for="linkedin">LinkedIn Profile URL (optional):</label>
                <input type="text" id="linkedin" name="linkedin" placeholder="https://www.linkedin.com/in/username/">
                <div class="example">Example: https://www.linkedin.com/in/satyanadella/</div>
            </div>

            <div class="form-group">
                <label for="linkedinFile">OR Upload LinkedIn Data (ZIP):</label>
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
            const linkedin = document.getElementById('linkedin').value;
            const linkedinFile = document.getElementById('linkedinFile').files[0];
            const jobDescription = document.getElementById('jobDescription').value;

            if (!github && !linkedin && !linkedinFile) {
                status.className = 'status error';
                status.textContent = 'Please provide at least one profile (GitHub, LinkedIn URL, or Data Export)';
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
                    formData.append('linkedin_url', linkedin);
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
                            linkedin_url: linkedin,
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
    if hasattr(request, "start_time"):
        duration = (datetime.utcnow() - request.start_time).total_seconds()
        api_logger.info(
            f"[{request.request_id}] {request.method} {request.path} "
            f"{response.status_code} {duration:.3f}s"
        )
    return response


# Error handlers
@app.errorhandler(MployableException)
def handle_mployable_exception(error):
    """Handle application-specific exceptions"""
    error_logger.warning(f"[{request.request_id}] {error.error_code}: {error.message}")
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
    error_logger.error(
        f"[{request.request_id}] Unhandled exception: {error}", exc_info=True
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


# Routes
@app.route("/", methods=["GET"])
def index():
    """Serve the main HTML interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/v1/generate-resume", methods=["POST"])
def generate_resume():
    """
    Main endpoint to generate a tailored resume

    Expected payload:
    - JSON: {"github_username": "...", "linkedin_url": "...", "job_description": "..."}
    - OR Multipart: form fields github_username, linkedin_url, job_description AND optional file linkedin_data

    Returns:
        PDF file: application/pdf
    """
    try:
        # Parse and validate request
        linkedin_file = None

        if request.content_type and "multipart/form-data" in request.content_type:
            github_username = request.form.get("github_username", "").strip()
            linkedin_url = request.form.get("linkedin_url", "").strip()
            job_description = request.form.get("job_description", "").strip()
            linkedin_file = request.files.get("linkedin_data")
        else:
            data = request.get_json(force=True) if not request.json else request.json
            if not data:
                raise InvalidJobDescription("Request body is empty")

            github_username = data.get("github_username", "").strip()
            linkedin_url = data.get("linkedin_url", "").strip()
            job_description = data.get("job_description", "").strip()

        logger.info(f"[{request.request_id}] Resume generation request")

        # Validate inputs
        (
            github_username,
            job_description,
            linkedin_url,
        ) = InputValidator.validate_request(
            github_username, job_description, linkedin_url
        )

        if (
            not github_username
            and not linkedin_url
            and not (linkedin_file and linkedin_file.filename)
        ):
            raise ValidationError(
                "Please provide at least one profile source (GitHub Username, LinkedIn URL, or LinkedIn Data Export zip file)"
            )

        logger.info(f"[{request.request_id}] Input validation passed")

        # Step 1: Scrape profiles
        profile_data = {}

        if github_username:
            try:
                logger.debug(
                    f"[{request.request_id}] Scraping GitHub profile: {github_username}"
                )
                github_data = github_scraper.scrape_profile(github_username)
                profile_data["github"] = github_data
                logger.debug(
                    f"[{request.request_id}] GitHub profile scraped successfully"
                )
            except GitHubUserNotFound as e:
                raise InvalidGitHubUsername(github_username)
            except GitHubAPIError as e:
                logger.error(f"[{request.request_id}] GitHub API error: {e}")
                raise

        # LinkedIn Data Handling (File Export or URL)
        if linkedin_file and linkedin_file.filename:
            try:
                logger.debug(f"[{request.request_id}] Parsing LinkedIn data export")
                # Save file temporarily
                temp_filename = f"{uuid.uuid4()}_{linkedin_file.filename}"
                file_path = os.path.join(config.UPLOAD_DIR, temp_filename)
                os.makedirs(config.UPLOAD_DIR, exist_ok=True)
                linkedin_file.save(file_path)

                linkedin_data = linkedin_scraper.parse_export(file_path)
                profile_data["linkedin"] = linkedin_data
                logger.debug(
                    f"[{request.request_id}] LinkedIn export parsed successfully"
                )

                # Cleanup
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(
                    f"[{request.request_id}] LinkedIn export parsing failed: {e}"
                )
        elif linkedin_url:
            try:
                logger.debug(f"[{request.request_id}] Scraping LinkedIn profile")
                linkedin_data = linkedin_scraper.scrape_profile(linkedin_url)
                profile_data["linkedin"] = linkedin_data
                logger.debug(
                    f"[{request.request_id}] LinkedIn profile scraped successfully"
                )
            except Exception as e:
                logger.warning(f"[{request.request_id}] LinkedIn scraping failed: {e}")
                # Don't fail if LinkedIn scraping fails, continue with GitHub data

        # Step 2: Analyze job description
        try:
            logger.debug(f"[{request.request_id}] Analyzing job description")
            job_requirements = job_analyzer.analyze(job_description)
            logger.debug(f"[{request.request_id}] Job analysis completed")
        except Exception as e:
            logger.error(f"[{request.request_id}] Job analysis failed: {e}")
            raise ResumeGenerationError("Failed to analyze job description")

        # Step 3: Refine GitHub projects based on job requirements
        if "github" in profile_data and "repositories" in profile_data["github"]:
            try:
                logger.debug(
                    f"[{request.request_id}] Refining GitHub projects by relevance"
                )
                job_skills = job_requirements.get("skills", {})
                relevant_projects = github_scraper.select_relevant_projects(
                    profile_data["github"]["repositories"], job_skills
                )
                profile_data["github"]["top_projects"] = relevant_projects
                logger.debug(
                    f"[{request.request_id}] Refined to {len(relevant_projects)} relevant projects"
                )
            except Exception as e:
                logger.warning(
                    f"[{request.request_id}] GitHub project refinement failed: {e}"
                )
                # Continue with default projects if refinement fails

        # Step 4: Generate tailored resume content
        try:
            logger.debug(f"[{request.request_id}] Generating resume content")
            resume_content = resume_generator.generate(profile_data, job_requirements)
            logger.debug(f"[{request.request_id}] Resume content generated")
        except Exception as e:
            logger.error(
                f"[{request.request_id}] Resume generation failed: {e}", exc_info=True
            )
            raise ResumeGenerationError(f"Failed to generate resume: {str(e)}")

        # Step 4: Compile to PDF
        try:
            logger.debug(f"[{request.request_id}] Compiling LaTeX to PDF")
            pdf_path = latex_compiler.compile(resume_content)
            logger.debug(f"[{request.request_id}] LaTeX compilation completed")
        except LaTeXCompilationError as e:
            logger.error(f"[{request.request_id}] LaTeX compilation failed: {e}")
            raise
        except Exception as e:
            logger.error(
                f"[{request.request_id}] PDF compilation failed: {e}", exc_info=True
            )
            raise LaTeXCompilationError("Failed to compile resume to PDF")

        # Security: Validate that the PDF path is within the temp directory
        abs_temp_dir = os.path.abspath(config.TEMP_DIR)
        abs_pdf_path = os.path.abspath(pdf_path)
        if not abs_pdf_path.startswith(abs_temp_dir):
            logger.error(f"[{request.request_id}] Invalid file path: {abs_pdf_path}")
            raise ValueError("Invalid file path")

        # Verify file exists
        if not os.path.exists(abs_pdf_path):
            logger.error(f"[{request.request_id}] PDF file not found: {abs_pdf_path}")
            raise ValueError("Generated PDF file not found")

        logger.info(f"[{request.request_id}] Resume generated successfully")

        # Return the PDF file
        return send_file(
            abs_pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f'tailored_resume_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        )

    except MployableException:
        # Re-raise application exceptions
        raise
    except Exception as e:
        logger.error(f"[{request.request_id}] Unexpected error: {e}", exc_info=True)
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


def create_app():
    """Application factory"""
    return app


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    logger.info(f"Starting Mployable v{config.VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug mode: {config.DEBUG}")

    # Run the application
    # In production, use a WSGI server like gunicorn instead:
    # gunicorn -w 4 -b 0.0.0.0:5000 app_production:create_app()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT, threaded=True)
