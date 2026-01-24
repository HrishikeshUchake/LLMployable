"""
Demo script for Mployable
Shows how to use the resume builder programmatically
"""

from scrapers.github_scraper import GitHubScraper
from analyzer.job_analyzer import JobAnalyzer
from generator.resume_generator import ResumeGenerator
from generator.latex_compiler import LaTeXCompiler

print("=" * 60)
print(" Mployable - AI-Powered Resume Builder Demo")
print("=" * 60)

# Sample job description
job_description = """
Senior Full Stack Developer

We're looking for an experienced Full Stack Developer to join our team.

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React and modern web frameworks
- Familiarity with cloud platforms (AWS, Azure, or GCP)
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Design and implement scalable web applications
- Collaborate with cross-functional teams
- Mentor junior developers
- Participate in code reviews

Nice to have:
- Experience with Docker and Kubernetes
- Contributions to open source projects
- Experience with CI/CD pipelines
"""

print("\n1. Analyzing job description...")
analyzer = JobAnalyzer()
job_requirements = analyzer.analyze(job_description)
print(f"   ✓ Found {len(job_requirements['skills'])} skill categories")
print(f"   ✓ Experience required: {job_requirements['experience_required']}")
print(f"   ✓ Skills: {job_requirements['skills']}")

print("\n2. Scraping GitHub profile...")
github_scraper = GitHubScraper()

# You can replace this with any GitHub username
# For demo purposes, using placeholder data (not a real GitHub user)
profile_data = {
    "github": {
        "username": "demo-user",  # Example GitHub username (placeholder)
        "name": "Demo User",
        "bio": "Full-stack developer with a passion for building scalable web applications",
        "location": "San Francisco, CA",
        "email": "demo@example.com",
        "languages": [("Python", 15), ("JavaScript", 12), ("TypeScript", 8), ("Go", 5)],
        "top_projects": [
            {
                "name": "web-app-framework",
                "description": "A modern web application framework built with Python and React",
                "language": "Python",
                "stars": 250,
                "topics": ["web", "react", "python", "framework"],
            },
            {
                "name": "cloud-deploy-tool",
                "description": "Automated deployment tool for AWS and GCP",
                "language": "Python",
                "stars": 180,
                "topics": ["aws", "gcp", "devops", "docker"],
            },
            {
                "name": "react-dashboard",
                "description": "Beautiful dashboard component library for React",
                "language": "TypeScript",
                "stars": 120,
                "topics": ["react", "typescript", "ui", "components"],
            },
        ],
        "public_repos": 42,
    }
}
print("   ✓ Profile data prepared")

print("\n3. Generating tailored resume...")
generator = ResumeGenerator()
resume_content = generator.generate(profile_data, job_requirements)
print("   ✓ Resume content generated")
print(f"   ✓ Name: {resume_content['name']}")
print(f"   ✓ Skills highlighted: {len(resume_content['skills'])}")
print(f"   ✓ Projects included: {len(resume_content['projects'])}")

print("\n4. Compiling to PDF...")
compiler = LaTeXCompiler()
try:
    pdf_path = compiler.compile(resume_content)
    print(f"   ✓ Resume generated: {pdf_path}")

    # Show some content
    print("\n" + "=" * 60)
    print("GENERATED RESUME PREVIEW")
    print("=" * 60)
    print(f"\nName: {resume_content['name']}")
    print(f"Location: {resume_content['location']}")
    print(f"Email: {resume_content['email']}")
    print(f"\nSummary:\n{resume_content['summary']}")
    print(f"\nSkills:\n{', '.join(resume_content['skills'][:10])}")
    print(f"\nTop Projects:")
    for i, proj in enumerate(resume_content["projects"][:3], 1):
        print(f"\n{i}. {proj['name']}")
        print(f"   {proj['description']}")
        print(f"   Technologies: {', '.join(proj['technologies'][:5])}")

    print("\n" + "=" * 60)
    print(f"✅ Resume successfully generated at: {pdf_path}")
    print("=" * 60)

except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Demo complete!")
print("\nTo use the web interface:")
print("1. Set GEMINI_API_KEY in .env file")
print("2. Run: python app.py")
print("3. Open: http://localhost:5000")
print("=" * 60)
