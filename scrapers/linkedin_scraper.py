"""
LinkedIn Profile Scraper

Note: LinkedIn actively blocks scraping. This is a simplified implementation
that would work with LinkedIn's API or with user-provided data.

In a production environment, you would:
1. Use LinkedIn's official API with proper OAuth
2. Ask users to export their LinkedIn data
3. Use a third-party service with proper authorization
"""

from typing import Dict, List, Optional
import re
import zipfile
import csv
import io


class LinkedInScraper:
    def __init__(self):
        """Initialize LinkedIn scraper"""
        pass

    def parse_export(self, zip_file_path: str) -> Dict:
        """
        Parse LinkedIn data export ZIP file

        Args:
            zip_file_path: Path to the LinkedIn data export ZIP file

        Returns:
            Dictionary containing profile data
        """
        profile_data = {
            "name": "",
            "headline": "",
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
            "source": "manual_export",
            "full_data": {},  # Store all other CSV data here
        }

        try:
            with zipfile.ZipFile(zip_file_path, "r") as z:
                for file_info in z.infolist():
                    if not file_info.filename.endswith(".csv"):
                        continue

                    filename = file_info.filename

                    # Skip connections as requested
                    if "Connections.csv" in filename:
                        continue

                    with z.open(filename) as f:
                        try:
                            # Use utf-8-sig to handle potential BOM in LinkedIn exports
                            content = io.TextIOWrapper(f, encoding="utf-8-sig")
                            reader = csv.DictReader(content)
                            rows = list(reader)

                            # Standard assignments for known files
                            if "Profile.csv" in filename and rows:
                                row = rows[0]
                                profile_data[
                                    "name"
                                ] = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                                profile_data["headline"] = row.get("Headline", "")
                                profile_data["summary"] = row.get("Summary", "")

                            elif "Positions.csv" in filename:
                                for row in rows:
                                    profile_data["experience"].append(
                                        {
                                            "title": row.get("Title", ""),
                                            "company": row.get("Company Name", ""),
                                            "location": row.get("Location", ""),
                                            "start_date": row.get("Started On", ""),
                                            "end_date": row.get("Finished On", ""),
                                            "description": row.get("Description", ""),
                                        }
                                    )

                            elif "Education.csv" in filename:
                                for row in rows:
                                    profile_data["education"].append(
                                        {
                                            "school": row.get("School Name", ""),
                                            "degree": row.get("Degree Name", ""),
                                            "notes": row.get("Notes", ""),
                                            "field_of_study": row.get(
                                                "Notes", ""
                                            ),  # Fallback
                                            "start_date": row.get("Started On", ""),
                                            "end_date": row.get("Finished On", ""),
                                        }
                                    )

                            elif "Skills.csv" in filename:
                                for row in rows:
                                    skill_name = row.get("Name", "")
                                    if skill_name:
                                        profile_data["skills"].append(skill_name)

                            elif "Projects.csv" in filename:
                                if "projects" not in profile_data:
                                    profile_data["projects"] = []
                                for row in rows:
                                    profile_data["projects"].append(
                                        {
                                            "title": row.get("Title", ""),
                                            "description": row.get("Description", ""),
                                            "url": row.get("URL", ""),
                                            "start_date": row.get("Started On", ""),
                                            "end_date": row.get("Finished On", ""),
                                        }
                                    )

                            elif "Certifications.csv" in filename:
                                if "certifications" not in profile_data:
                                    profile_data["certifications"] = []
                                for row in rows:
                                    profile_data["certifications"].append(
                                        {
                                            "name": row.get("Name", ""),
                                            "authority": row.get("Authority", ""),
                                            "license_number": row.get(
                                                "License Number", ""
                                            ),
                                            "url": row.get("Url", ""),
                                            "start_date": row.get("Started On", ""),
                                            "end_date": row.get("Finished On", ""),
                                        }
                                    )

                            elif "Languages.csv" in filename:
                                if "languages" not in profile_data:
                                    profile_data["languages"] = []
                                for row in rows:
                                    lang = row.get("Name", "")
                                    prof = row.get("Proficiency", "")
                                    if lang:
                                        profile_data["languages"].append(
                                            f"{lang} ({prof})" if prof else lang
                                        )

                            elif "Honors.csv" in filename:
                                if "awards" not in profile_data:
                                    profile_data["awards"] = []
                                for row in rows:
                                    profile_data["awards"].append(
                                        {
                                            "title": row.get("Title", ""),
                                            "issuer": row.get("Issuer", ""),
                                            "date": row.get("Issued On", ""),
                                            "description": row.get("Description", ""),
                                        }
                                    )

                            # Store everything else in full_data
                            key = filename.replace(".csv", "").replace(" ", "_").lower()
                            profile_data["full_data"][key] = rows

                        except Exception as parse_error:
                            print(f"Error parsing {filename}: {parse_error}")

            return profile_data
        except Exception as e:
            print(f"Error parsing LinkedIn export: {e}")
            return profile_data
        except Exception as e:
            print(f"Error parsing LinkedIn export: {e}")
            return profile_data

    def scrape_profile(self, linkedin_url: str) -> Dict:
        """
        Extract LinkedIn profile data

        In this implementation, we return a placeholder structure.
        In production, this would:
        - Use LinkedIn's API with OAuth
        - Or parse user-uploaded LinkedIn data export

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Dictionary containing profile data
        """
        # Extract username from URL
        username = self._extract_username(linkedin_url)

        # Log warning about placeholder usage
        print(
            "Warning: LinkedIn scraper is using placeholder data. "
            "LinkedIn scraping requires API access or manual data export. "
            "For best results, set up LinkedIn API access or ask users to provide their data."
        )

        # Return placeholder data
        # In production, this would fetch real data from LinkedIn API
        return {
            "url": linkedin_url,
            "username": username,
            "name": "",
            "headline": "",
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
            "note": "LinkedIn scraping requires API access or manual data export",
        }

    def _extract_username(self, url: str) -> str:
        """Extract username from LinkedIn URL"""
        match = re.search(r"linkedin\.com/in/([^/]+)", url)
        if match:
            return match.group(1)
        return url
