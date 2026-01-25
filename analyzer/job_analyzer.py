"""
Job Description Analyzer

Analyzes job descriptions to extract:
- Required skills
- Preferred qualifications
- Key responsibilities
- Technologies mentioned
"""

import re
from typing import Dict, List, Set

from database.repositories import CacheRepository


class JobAnalyzer:
    def __init__(self):
        """Initialize job analyzer"""
        # Common technical skills to look for
        self.tech_keywords = {
            "languages": [
                "python",
                "java",
                "javascript",
                "typescript",
                "c++",
                "c#",
                "go",
                "rust",
                "ruby",
                "php",
                "swift",
                "kotlin",
                "scala",
                "r",
            ],
            "frameworks": [
                "react",
                "angular",
                "vue",
                "django",
                "flask",
                "spring",
                "express",
                "fastapi",
                "rails",
                "laravel",
                ".net",
                "node.js",
                "nodejs",
            ],
            "databases": [
                "sql",
                "mysql",
                "postgresql",
                "mongodb",
                "redis",
                "elasticsearch",
                "dynamodb",
                "cassandra",
                "oracle",
            ],
            "cloud": [
                "aws",
                "azure",
                "gcp",
                "google cloud",
                "docker",
                "kubernetes",
                "k8s",
                "terraform",
                "ansible",
            ],
            "tools": ["git", "jenkins", "ci/cd", "jira", "agile", "scrum", "linux"],
        }

    def analyze(self, job_description: str) -> Dict:
        """
        Analyze a job description and extract key requirements

        Args:
            job_description: The job description text

        Returns:
            Dictionary containing analyzed requirements
        """
        # Check cache first
        try:
            cached_result = CacheRepository.get_cached_job_analysis(job_description)
            if cached_result:
                return cached_result
        except Exception:
            pass  # Fallback to re-analyzing if cache fails

        job_desc_lower = job_description.lower()

        # Extract skills
        skills = self._extract_skills(job_desc_lower)

        # Extract experience requirements
        experience = self._extract_experience(job_desc_lower)

        # Extract education requirements
        education = self._extract_education(job_desc_lower)

        # Identify key sections
        sections = self._identify_sections(job_description)

        result = {
            "original_description": job_description,
            "skills": skills,
            "experience_required": experience,
            "education_required": education,
            "sections": sections,
            "keywords": self._extract_keywords(job_desc_lower),
        }

        # Cache the result (using default 48 hours TTL)
        try:
            CacheRepository.cache_job_analysis(job_description, result)
        except Exception:
            pass

        return result

    def _extract_skills(self, job_desc_lower: str) -> Dict[str, List[str]]:
        """Extract technical skills from job description"""
        found_skills = {}

        for category, keywords in self.tech_keywords.items():
            found = []
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, job_desc_lower):
                    found.append(keyword)
            if found:
                found_skills[category] = found

        return found_skills

    def _extract_experience(self, job_desc_lower: str) -> str:
        """Extract experience requirements"""
        # Look for patterns like "3+ years", "5-7 years", etc.
        patterns = [
            r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
            r"(\d+)-(\d+)\s*years?\s+(?:of\s+)?experience",
            r"minimum\s+(?:of\s+)?(\d+)\s*years?",
        ]

        for pattern in patterns:
            match = re.search(pattern, job_desc_lower)
            if match:
                return match.group(0)

        return "Not specified"

    def _extract_education(self, job_desc_lower: str) -> str:
        """Extract education requirements"""
        education_keywords = ["bachelor", "master", "phd", "degree", "bs", "ms", "mba"]

        for keyword in education_keywords:
            if keyword in job_desc_lower:
                # Extract sentence containing the keyword
                sentences = job_desc_lower.split(".")
                for sentence in sentences:
                    if keyword in sentence:
                        return sentence.strip()

        return "Not specified"

    def _identify_sections(self, job_description: str) -> Dict[str, str]:
        """Identify different sections in the job description"""
        sections = {}

        # Common section headers
        section_patterns = {
            "responsibilities": r"(?:responsibilities|duties|role)[:\s]*([^\n]+(?:\n(?!\n)[^\n]+)*)",
            "requirements": r"(?:requirements|qualifications)[:\s]*([^\n]+(?:\n(?!\n)[^\n]+)*)",
            "nice_to_have": r"(?:nice to have|preferred|bonus)[:\s]*([^\n]+(?:\n(?!\n)[^\n]+)*)",
        }

        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, job_description, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[section_name] = match.group(1).strip()

        return sections

    def _extract_keywords(self, job_desc_lower: str) -> List[str]:
        """Extract important keywords from job description"""
        # Remove common words
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "can",
        }

        # Extract words
        words = re.findall(r"\b[a-z]{3,}\b", job_desc_lower)

        # Filter and count
        word_freq = {}
        for word in words:
            if word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:20]]
