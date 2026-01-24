"""
Resume Generator using Google Gemini

Uses Google Gemini AI to analyze profile data and job requirements,
then generates tailored resume content.
"""

import google.generativeai as genai
import os
import json
from typing import Dict, List
from config.config import get_config


class ResumeGenerator:
    def __init__(self):
        """Initialize resume generator with Gemini API"""
        config = get_config()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Using the model specified in configuration (cheapest: gemini-2.0-flash-lite)
            try:
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
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

        # Merge skills
        github_languages = [lang for lang, _ in github_data.get("languages", [])]
        linkedin_skills = linkedin_data.get("skills", [])
        all_candidate_skills = list(set(github_languages + linkedin_skills))

        # Format LinkedIn Experience
        experience_text = ""
        for exp in linkedin_data.get("experience", []):
            experience_text += f"- {exp.get('title')} at {exp.get('company')} ({exp.get('start_date')} - {exp.get('end_date')}): {exp.get('description')}\n"

        # Format Education
        education_text = ""
        for edu in linkedin_data.get("education", []):
            degree = edu.get("degree") or "Degree"
            field = edu.get("field_of_study") or edu.get("notes")
            school = edu.get("school") or "University"
            dates = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"

            education_text += f"- {degree}"
            if field:
                education_text += f" in {field}"
            education_text += f" from {school} ({dates})\n"

        # Format LinkedIn Projects (if available)
        linkedin_projects = linkedin_data.get("projects", [])
        li_projects_text = ""
        for lp in linkedin_projects:
            li_projects_text += f"- {lp.get('title')}: {lp.get('description')} ({lp.get('start_date')} - {lp.get('end_date')})\n"

        # Format Other LinkedIn Data
        additional_info = ""
        full_data = linkedin_data.get("full_data", {})
        for category, items in full_data.items():
            if category in [
                "profile",
                "positions",
                "education",
                "skills",
                "projects",
                "connections",
            ]:
                continue
            if items:
                additional_info += f"\n{category.upper()}:\n"
                for item in items[
                    :10
                ]:  # Limit to 10 items per category to avoid token bloat
                    # Clean up dictionary to string
                    item_str = ", ".join([f"{k}: {v}" for k, v in item.items() if v])
                    additional_info += f"- {item_str}\n"

        prompt = f"""You are an expert resume writer. Create a tailored resume based on the following information:

JOB DESCRIPTION:
{job_requirements.get('original_description', 'N/A')}

CANDIDATE INFORMATION:
Name: {linkedin_data.get('name') or github_data.get('name', 'N/A')}
Headline: {linkedin_data.get('headline', 'N/A')}
Bio: {github_data.get('bio', 'N/A')}
Summary: {linkedin_data.get('summary', 'N/A')}
Location: {linkedin_data.get('location') or github_data.get('location', 'N/A')}
Email: {github_data.get('email', 'N/A')}

PROFESSIONAL EXPERIENCE:
{experience_text or 'N/A'}

EDUCATION:
{education_text or 'N/A'}

TECHNICAL SKILLS:
{', '.join(all_candidate_skills)}

GITHUB PROJECTS:
{self._format_projects(github_data.get('top_projects', []))}

LINKEDIN PROJECTS:
{li_projects_text or 'N/A'}

ADDITIONAL PROFESSIONAL DETAILS (from LinkedIn Archive):
{additional_info or 'N/A'}

REQUIRED SKILLS FROM JOB:
{json.dumps(job_requirements.get('skills', {}), indent=2)}

TASK:
Generate a tailored resume that:
1. Highlights relevant skills that match the job requirements
2. Incorporates both professional experience from LinkedIn and technical projects from GitHub
3. Uses strong action words and quantifiable achievements
4. Tailors the "Summary" and "Projects" descriptions to emphasize relevance to the specific job description

Return the response in the following JSON format:
{{
    "summary": "Professional summary (2-3 sentences)",
    "skills": ["skill1", "skill2", "skill3"],
    "education": [
        {{
            "degree": "Degree Name",
            "school": "School Name",
            "date": "Graduation Date",
            "details": "Minor or relevant coursework"
        }}
    ],
    "experience": [
        {{
            "role": "Job Title",
            "company": "Company Name",
            "date": "Start - End",
            "description": "Tailored bullet point highlighting relevance"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Tailored description emphasizing project impact",
            "technologies": ["tech1", "tech2"]
        }}
    ],
    "certifications": ["Cert 1", "Cert 2"],
    "languages": ["Lang 1", "Lang 2"]
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
                linkedin_data = profile_data.get("linkedin", {})

                # Prioritize LinkedIn data for formal name and location
                parsed["name"] = linkedin_data.get("name") or github_data.get(
                    "name", "Your Name"
                )
                parsed["email"] = github_data.get("email", "")
                parsed["location"] = linkedin_data.get("location") or github_data.get(
                    "location", ""
                )

                parsed["github_url"] = (
                    f"github.com/{github_data.get('username', '')}"
                    if github_data.get("username")
                    else ""
                )
                parsed["linkedin_url"] = linkedin_data.get("url", "")

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

        # Extract skills (merge GitHub and LinkedIn)
        github_languages = [lang for lang, _ in github_data.get("languages", [])]
        linkedin_skills = linkedin_data.get("skills", [])
        all_candidate_skills = list(set(github_languages + linkedin_skills))

        # Match skills with job requirements
        job_skills = job_requirements.get("skills", {})
        job_skills_list = []
        for category, skills in job_skills.items():
            job_skills_list.extend(skills)

        # Highlight matched skills
        highlighted_skills = [
            s
            for s in all_candidate_skills
            if s.lower() in [js.lower() for js in job_skills_list]
        ]
        # Use a mix of matched skills and candidate's top tools
        final_skills = (
            highlighted_skills
            + [s for s in all_candidate_skills if s not in highlighted_skills]
        )[:15]

        # Format projects (prioritize LinkedIn, then GitHub)
        projects = []

        # Add LinkedIn Experience/Projects as projects in the base resume
        for exp in linkedin_data.get("experience", [])[:3]:
            projects.append(
                {
                    "name": f"{exp.get('title')} at {exp.get('company')}",
                    "description": exp.get("description", ""),
                    "technologies": [],
                }
            )

        # Add GitHub projects
        for proj in github_data.get("top_projects", [])[:3]:
            projects.append(
                {
                    "name": proj["name"],
                    "description": proj["description"],
                    "technologies": [proj["language"]] + proj.get("topics", []),
                }
            )

        return {
            "name": linkedin_data.get("name") or github_data.get("name", "Your Name"),
            "email": github_data.get("email", ""),
            "location": linkedin_data.get("location")
            or github_data.get("location", ""),
            "github_url": (
                f"github.com/{github_data.get('username', '')}"
                if github_data.get("username")
                else ""
            ),
            "linkedin_url": linkedin_data.get("url", ""),
            "summary": linkedin_data.get("summary")
            or github_data.get("bio", "Experienced software developer"),
            "skills": final_skills,
            "projects": projects[:5],
        }
