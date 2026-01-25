"""
Interview Preparation Generator using Google Gemini

Uses Google Gemini AI to analyze job requirements and generate 
tailored interview preparation tips and sample questions.
"""

from google import genai
import os
import json
from typing import Dict, List
from config.config import get_config


class InterviewGenerator:
    def __init__(self):
        """Initialize interview generator with Gemini API"""
        self.config = get_config()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=api_key)
                self.model_name = self.config.GEMINI_MODEL
            except Exception:
                self.client = genai.Client(api_key=api_key)
                self.model_name = "gemini-2.0-flash"

    def generate(self, job_requirements: Dict) -> Dict:
        """
        Generate interview tips and sample questions based on job requirements

        Args:
            job_requirements: Dictionary containing analyzed job requirements

        Returns:
            Dictionary containing structured interview prep content
        """
        if not self.client:
            print("InterviewGenerator: No client initialized, using basic prep")
            return self._generate_basic_prep(job_requirements)

        try:
            # Prepare prompt for Gemini
            prompt = self._create_prompt(job_requirements)
            print(f"InterviewGenerator: Generating content with Gemini...")

            # Generate content using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if not response or not response.text:
                print("InterviewGenerator: Empty response from Gemini")
                return self._generate_basic_prep(job_requirements)

            # Parse the response
            prep_content = self._parse_gemini_response(response.text)
            print("InterviewGenerator: Successfully generated interview prep")

            return prep_content

        except Exception as e:
            print(f"Error generating interview prep with Gemini: {e}")
            return self._generate_basic_prep(job_requirements)

    def _create_prompt(self, job_requirements: Dict) -> str:
        """Create prompt for Gemini API"""
        skills = job_requirements.get("skills", {})
        experience = job_requirements.get("experience", "Not specified")
        education = job_requirements.get("education", "Not specified")
        sections = job_requirements.get("sections", {})
        
        # Flatten skills for prompt
        all_skills = []
        for category, skill_list in skills.items():
            all_skills.extend(skill_list)
        
        skills_text = ", ".join(all_skills) if all_skills else "General technical skills"
        
        prompt = f"""
        Act as an expert technical recruiter and interview coach. 
        Based on the following job requirements, generate a comprehensive interview preparation guide.

        JOB REQUIREMENTS:
        - Required Skills: {skills_text}
        - Experience Level: {experience}
        - Education: {education}
        
        ADDITIONAL JOB DETAILS:
        {json.dumps(sections, indent=2)}

        TASKS:
        1. Provide 5-7 customized Interview Preparation Tips specific to this role and these technologies.
        2. Generate 5 Technical Questions based on the required skills.
        3. Generate 3 Behavioral Questions tailored to the responsibilities of this role.
        4. Generate 2 "Situational" or "Scenario-based" Questions.
        5. Provide a brief "Winning Strategy" for this specific role.

        FORMAT:
        Return ONLY a JSON object with this exact structure:
        {{
            "tips": ["tip 1", "tip 2", ...],
            "technical_questions": [
                {{"question": "...", "context": "Focus on..."}}
            ],
            "behavioral_questions": [
                {{"question": "...", "context": "Focus on..."}}
            ],
            "situational_questions": [
                {{"question": "...", "context": "Focus on..."}}
            ],
            "winning_strategy": "..."
        }}
        """
        return prompt

    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini JSON response"""
        try:
            # Find the JSON part in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._generate_basic_prep({})

    def _generate_basic_prep(self, job_requirements: Dict) -> Dict:
        """Basic fallback interview prep without AI"""
        return {
            "tips": [
                "Research the company's recent projects and values.",
                "Review the core technologies mentioned in the job description.",
                "Prepare examples using the STAR method (Situation, Task, Action, Result).",
                "Practice explaining your technical decisions and trade-offs.",
                "Have 2-3 thoughtful questions ready for the interviewer."
            ],
            "technical_questions": [
                {"question": "Can you walk us through a challenging technical problem you solved recently?", "context": "Focus on your problem-solving process and final outcome."},
                {"question": "What is your experience with the core tech stack mentioned in this role?", "context": "Be specific about libraries and frameworks you've used."}
            ],
            "behavioral_questions": [
                {"question": "Tell me about a time you had a conflict with a teammate. How did you handle it?", "context": "Focus on collaboration and professionalism."},
                {"question": "Where do you see your technical skills evolving in the next 2 years?", "context": "Show growth mindset and alignment with company goals."}
            ],
            "situational_questions": [
                {"question": "If you are given a task with a tight deadline and unclear requirements, what would you do?", "context": "Focus on communication and prioritization."}
            ],
            "winning_strategy": "Be authentic, demonstrate how your unique skills solve the company's specific problems, and show enthusiasm for the role."
        }
