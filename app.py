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
from scrapers.github_scraper import GitHubScraper
from scrapers.linkedin_scraper import LinkedInScraper
from analyzer.job_analyzer import JobAnalyzer
from generator.resume_generator import ResumeGenerator
from generator.latex_compiler import LaTeXCompiler

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
github_scraper = GitHubScraper()
linkedin_scraper = LinkedInScraper()
job_analyzer = JobAnalyzer()
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
                            linkedin_url: linkedin,
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
def generate_resume():
    """
    Main endpoint to generate a tailored resume

    Expected payload:
    - JSON: {"github_username": "...", "linkedin_url": "...", "job_description": "..."}
    - OR Multipart: form fields github_username, linkedin_url, job_description AND optional file linkedin_data
    """
    try:
        linkedin_file = None
        if request.content_type and "multipart/form-data" in request.content_type:
            github_username = request.form.get("github_username", "").strip()
            linkedin_url = request.form.get("linkedin_url", "").strip()
            job_description = request.form.get("job_description", "").strip()
            linkedin_file = request.files.get("linkedin_data")
        else:
            data = request.json
            github_username = data.get("github_username", "").strip()
            linkedin_url = data.get("linkedin_url", "").strip()
            job_description = data.get("job_description", "").strip()

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        if not github_username and not linkedin_url and not linkedin_file:
            return (
                jsonify(
                    {"error": "At least one profile or data export is required"}
                ),
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
        elif linkedin_url:
            linkedin_data = linkedin_scraper.scrape_profile(linkedin_url)
            profile_data["linkedin"] = linkedin_data

        # Step 2: Analyze job description
        job_requirements = job_analyzer.analyze(job_description)

        # Step 3: Generate tailored resume content
        resume_content = resume_generator.generate(profile_data, job_requirements)

        # Step 4: Compile to PDF
        pdf_path = latex_compiler.compile(resume_content)

        # Validate that the PDF path is within the temp directory (security check)
        abs_temp_dir = os.path.abspath("temp")
        abs_pdf_path = os.path.abspath(pdf_path)
        if not abs_pdf_path.startswith(abs_temp_dir):
            return jsonify({"error": "Invalid file path"}), 500

        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="tailored_resume.pdf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
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
    port = int(os.getenv("FLASK_PORT", "5000"))

    # Run the application
    app.run(debug=debug_mode, host=host, port=port)
