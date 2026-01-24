"""
Resume Generator using Google Gemini

Uses Google Gemini AI to analyze profile data and job requirements,
then generates tailored resume content.
"""

import google.generativeai as genai
import os
import json
from typing import Dict, List


class ResumeGenerator:
    def __init__(self):
        """Initialize resume generator with Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Using gemini-1.5-pro for better performance
            # Falls back to gemini-pro if not available
            try:
                self.model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception:
                self.model = genai.GenerativeModel("gemini-pro")

    def generate(self, profile_data: Dict, job_requirements: Dict) -> Dict:
        """
        Generate tailored resume content based on profile data and job requirements

        Args:
            profile_data: Dictionary containing GitHub/LinkedIn profile data
            job_requirements: Dictionary containing analyzed job requirements

        Returns:
            Dictionary containing structured resume content
        """
        if not self.model:
            # Fallback without AI
            return self._generate_basic_resume(profile_data, job_requirements)

        try:
            # Prepare prompt for Gemini
            prompt = self._create_prompt(profile_data, job_requirements)

            # Generate content using Gemini
            response = self.model.generate_content(prompt)

            # Parse the response
            resume_content = self._parse_gemini_response(response.text, profile_data)

            return resume_content

        except Exception as e:
            print(f"Error generating resume with Gemini: {e}")
            return self._generate_basic_resume(profile_data, job_requirements)

    def _create_prompt(self, profile_data: Dict, job_requirements: Dict) -> str:
        """Create prompt for Gemini API"""
        github_data = profile_data.get("github", {})
        linkedin_data = profile_data.get("linkedin", {})

        prompt = f"""You are an expert resume writer. Create a tailored resume based on the following information:

JOB REQUIREMENTS:
{job_requirements.get('original_description', 'N/A')}

CANDIDATE PROFILE:
Name: {github_data.get('name', 'N/A')}
Bio: {github_data.get('bio', 'N/A')}
Location: {github_data.get('location', 'N/A')}
Email: {github_data.get('email', 'N/A')}
Company: {github_data.get('company', 'N/A')}

TECHNICAL SKILLS:
Languages: {', '.join([lang for lang, _ in github_data.get('languages', [])])}

TOP PROJECTS:
{self._format_projects(github_data.get('top_projects', []))}

REQUIRED SKILLS FROM JOB:
{json.dumps(job_requirements.get('skills', {}), indent=2)}

TASK:
Generate a tailored resume that:
1. Highlights relevant skills that match the job requirements
2. Emphasizes relevant projects from the GitHub profile
3. Uses strong action words and quantifiable achievements
4. Focuses on experiences most relevant to the job description

Return the response in the following JSON format:
{{
    "summary": "Professional summary (2-3 sentences)",
    "skills": ["skill1", "skill2", "skill3"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Tailored description emphasizing relevance to job",
            "technologies": ["tech1", "tech2"]
        }}
    ]
}}

Only return valid JSON, no additional text."""

        return prompt

    def _format_projects(self, projects: List[Dict]) -> str:
        """Format projects for prompt"""
        if not projects:
            return "No projects available"

        formatted = []
        for proj in projects[:5]:
            formatted.append(
                f"- {proj['name']}: {proj['description']} ({proj['language']}, {proj['stars']} stars)"
            )

        return "\n".join(formatted)

    def _parse_gemini_response(self, response_text: str, profile_data: Dict) -> Dict:
        """Parse Gemini's response into structured resume data"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed = json.loads(json_text)

                # Add profile information
                github_data = profile_data.get("github", {})
                parsed["name"] = github_data.get("name", "Your Name")
                parsed["email"] = github_data.get("email", "")
                parsed["location"] = github_data.get("location", "")
                parsed["github_url"] = (
                    f"github.com/{github_data.get('username', '')}"
                    if github_data.get("username")
                    else ""
                )
                parsed["linkedin_url"] = profile_data.get("linkedin", {}).get("url", "")

                return parsed
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")

        # Fallback
        return self._generate_basic_resume(profile_data, {})

    def _generate_basic_resume(
        self, profile_data: Dict, job_requirements: Dict
    ) -> Dict:
        """Generate basic resume without AI (fallback)"""
        github_data = profile_data.get("github", {})
        linkedin_data = profile_data.get("linkedin", {})

        # Extract skills from GitHub
        languages = [lang for lang, _ in github_data.get("languages", [])]

        # Match skills with job requirements
        job_skills = job_requirements.get("skills", {})
        matched_skills = []
        for category, skills in job_skills.items():
            matched_skills.extend(skills)

        # Combine with user's languages
        all_skills = list(set(languages + matched_skills))

        # Format projects
        projects = []
        for proj in github_data.get("top_projects", [])[:5]:
            projects.append(
                {
                    "name": proj["name"],
                    "description": proj["description"],
                    "technologies": [proj["language"]] + proj.get("topics", []),
                }
            )

        return {
            "name": github_data.get("name", "Your Name"),
            "email": github_data.get("email", ""),
            "location": github_data.get("location", ""),
            "github_url": (
                f"github.com/{github_data.get('username', '')}"
                if github_data.get("username")
                else ""
            ),
            "linkedin_url": linkedin_data.get("url", ""),
            "summary": github_data.get("bio", "Experienced software developer"),
            "skills": all_skills[:15],
            "projects": projects,
        }
