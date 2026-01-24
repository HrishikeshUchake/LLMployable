"""
LaTeX Resume Compiler

Generates LaTeX code from resume data and compiles it to PDF
"""

import os
import subprocess
from typing import Dict
from datetime import datetime


class LaTeXCompiler:
    def __init__(self):
        """Initialize LaTeX compiler"""
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def compile(self, resume_content: Dict) -> str:
        """
        Generate LaTeX code and compile to PDF

        Args:
            resume_content: Dictionary containing resume data

        Returns:
            Path to generated PDF file
        """
        # Generate LaTeX code
        latex_code = self._generate_latex(resume_content)

        # Write to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tex_file = os.path.join(self.temp_dir, f"resume_{timestamp}.tex")
        pdf_file = os.path.join(self.temp_dir, f"resume_{timestamp}.pdf")

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # Compile LaTeX to PDF
        try:
            # Run pdflatex
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    self.temp_dir,
                    tex_file,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"LaTeX compilation warning/error:\n{result.stdout}\n{result.stderr}")

            if os.path.exists(pdf_file):
                return pdf_file
            else:
                raise Exception(f"PDF file was not generated. Return code: {result.returncode}")

        except FileNotFoundError:
            # pdflatex not installed, create a simple text file as fallback
            print("Warning: pdflatex not found, creating text version")
            txt_file = pdf_file.replace(".pdf", ".txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(self._generate_text_resume(resume_content))
            # Return with .txt extension to be clear about format
            return txt_file
        except Exception as e:
            print(f"Error compiling LaTeX: {e}")
            raise

    def _generate_latex(self, content: Dict) -> str:
        """Generate LaTeX code for resume using the professional template style"""

        # Sanitize all text inputs to prevent LaTeX injection
        def sanitize_latex(text: str) -> str:
            """Escape special LaTeX characters"""
            if not text:
                return ""
            # Escape special LaTeX characters
            replacements = {
                "\\": r"\textbackslash{}",
                "&": r"\&",
                "%": r"\%",
                "$": r"\$",
                "#": r"\#",
                "_": r"\_",
                "{": r"\{",
                "}": r"\}",
                "~": r"\textasciitilde{}",
                "^": r"\textasciicircum{}",
            }
            for char, replacement in replacements.items():
                text = text.replace(char, replacement)
            return text

        name = sanitize_latex(content.get("name", "Your Name"))
        email = sanitize_latex(content.get("email", ""))
        location = sanitize_latex(content.get("location", ""))
        github = sanitize_latex(content.get("github_url", "github.com"))
        summary = sanitize_latex(content.get("summary", ""))
        skills = content.get("skills", [])
        experience = content.get("experience", [])
        projects = content.get("projects", [])
        education = content.get("education", [])
        certifications = content.get("certifications", [])
        languages = content.get("languages", [])

        # Format header contact line
        contact_items = []
        if location:
            contact_items.append(location)
        if email:
            contact_items.append(f"\\href{{mailto:{content.get('email', '')}}}{{\\underline{{{email}}}}}")
        if github:
            github_display = github.replace("https://", "").replace("http://", "")
            contact_items.append(f"\\href{{https://{github}}}{{\\underline{{{github_display}}}}}")
        
        contact_line = " $|$ ".join(contact_items)

        # Build Experience items
        exp_latex = ""
        for exp in experience[:5]:
            role = sanitize_latex(exp.get("role", ""))
            company = sanitize_latex(exp.get("company", ""))
            date = sanitize_latex(exp.get("date", ""))
            # Handle list of bullets if description is a list, otherwise split by period or newline
            desc = exp.get("description", "")
            bullets = []
            if isinstance(desc, list):
                bullets = desc
            else:
                # Split by newline or large gaps
                bullets = [b.strip() for b in desc.split("\n") if b.strip()]
                if not bullets:
                    # Fallback to splitting by period if it looks like sentences
                    bullets = [b.strip() for b in desc.split(". ") if b.strip()]

            exp_latex += f"    \\resumeSubheading\n      {{{company}}}{{{date}}}\n      {{{role}}}{{}}\n      \\resumeItemListStart\n"
            for bullet in bullets[:4]:
                exp_latex += f"        \\resumeItem{{{sanitize_latex(bullet)}}}\n"
            exp_latex += "      \\resumeItemListEnd\n\n"

        # Build Education items
        edu_latex = ""
        for edu in education:
            school = sanitize_latex(edu.get("school", ""))
            degree = sanitize_latex(edu.get("degree", ""))
            date = sanitize_latex(edu.get("date", ""))
            details = sanitize_latex(edu.get("details", ""))
            edu_latex += f"    \\resumeSubheading\n      {{{school}}}{{{date}}}\n      {{{degree}}}{{}}\n"
            if details:
                edu_latex += f"      \\resumeItemListStart\n        \\resumeItem{{{details}}}\n      \\resumeItemListEnd\n"
            edu_latex += "\n"

        # Build Projects items
        proj_latex = ""
        for proj in projects[:4]:
            p_name = sanitize_latex(proj.get("name", "Project"))
            p_desc = sanitize_latex(proj.get("description", ""))
            p_tech = ", ".join([sanitize_latex(t) for t in proj.get("technologies", [])])
            proj_title = f"\\textbf{{{p_name}}}"
            if p_tech:
                proj_title += f" $|$ \\emph{{{p_tech}}}"
            
            proj_latex += f"    \\resumeProjectHeading\n      {{{proj_title}}}{{}}\n      \\resumeItemListStart\n"
            # Split description into bullets if needed
            bullets = [b.strip() for b in p_desc.split("\n") if b.strip()]
            for bullet in bullets[:2]:
                proj_latex += f"        \\resumeItem{{{sanitize_latex(bullet)}}}\n"
            proj_latex += "      \\resumeItemListEnd\n\n"

        # Build Skills
        skills_str = ", ".join([sanitize_latex(s) for s in skills[:20]])

        # Build Certifications
        cert_items = []
        for cert in certifications[:5]:
            cert_items.append(f"\\resumeProjectHeading\n      {{\\textbf{{{sanitize_latex(cert)}}}}}{{}}")
        cert_latex = "\n".join(cert_items)

        # Build Languages
        lang_str = ", ".join([sanitize_latex(l) for l in languages])

        # Full Template - "Zero-Dependency" Professional Style
        latex_template = f"""\\documentclass[letterpaper,11pt]{{article}}

\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\usepackage{{geometry}}
\\geometry{{left=0.5in, top=0.5in, right=0.5in, bottom=0.5in}}

% Font option: Use standard Palatino if available, or just stick to default
\\usepackage[T1]{{fontenc}}

\\pagestyle{{fancy}}
\\fancyhf{{}} 
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}

\\urlstyle{{same}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting - Manual implementation without titlesec
\\newcommand{{\\cvsection}}[1]{{
  \\vspace{{10pt}}
  {{\\large \\scshape #1}} \\\\ \\hrule \\vspace{{5pt}}
}}

% Custom commands implementation using standard LaTeX
\\newcommand{{\\resumeItem}}[1]{{
  \\item \\small{{#1 \\vspace{{-2pt}}}}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\item
  \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{#1}} & #2 \\\\
    \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
  \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
  \\item
  \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\small#1 & #2 \\\\
  \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}\\small}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{{document}}

%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}
    \\small {contact_line}
\\end{{center}}

%----------SUMMARY----------
\\cvsection{{Summary}}
\\small{{{summary}}}

%-----------EXPERIENCE-----------
\\cvsection{{Experience}}
\\begin{{itemize}}
{exp_latex}
\\end{{itemize}}

%-----------PROJECTS-----------
\\cvsection{{Notable Projects}}
\\begin{{itemize}}
{proj_latex}
\\end{{itemize}}

%-----------EDUCATION-----------
\\cvsection{{Education}}
\\begin{{itemize}}
{edu_latex}
\\end{{itemize}}

%-----------SKILLS-----------
\\cvsection{{Technical Skills}}
\\begin{{itemize}}
\\item\\small{{\\textbf{{Skills:}} {skills_str}}}
\\end{{itemize}}

%-----------CERTIFICATIONS-----------
\\cvsection{{Certifications}}
\\begin{{itemize}}
{cert_latex}
\\end{{itemize}}

%-----------LANGUAGES-----------
\\cvsection{{Languages}}
\\begin{{itemize}}
\\item\\small{{{lang_str}}}
\\end{{itemize}}

\\end{{document}}
"""
        return latex_template

    def _generate_text_resume(self, content: Dict) -> str:
        """Generate plain text resume as fallback"""
        name = content.get("name", "Your Name")
        email = content.get("email", "")
        location = content.get("location", "")
        github = content.get("github_url", "")
        summary = content.get("summary", "")
        summary = content.get("summary", "")
        skills = content.get("skills", [])
        experience = content.get("experience", [])
        projects = content.get("projects", [])
        education = content.get("education", [])
        certifications = content.get("certifications", [])
        languages = content.get("languages", [])

        text = f"""
{'='*60}
{name.center(60)}
{'='*60}

Contact Information:
  Email: {email}
  Location: {location}
  GitHub: {github}

Professional Summary:
  {summary}

Technical Skills:
  {', '.join(skills[:15])}

Professional Experience:
"""
        for exp in experience[:5]:
            text += f"  {exp.get('role', '')} @ {exp.get('company', '')} | {exp.get('date', '')}\n"
            text += f"    {exp.get('description', '')}\n\n"

        text += "\nNotable Projects:\n"
        for proj in projects[:5]:
            text += f"  {proj.get('name', 'Project')}\n"
            text += f"    {proj.get('description', '')}\n"
            text += f"    Technologies: {', '.join(proj.get('technologies', [])[:5])}\n\n"

        text += "\nEducation:\n"
        for edu in education:
            text += f"  {edu.get('degree', '')}, {edu.get('school', '')} | {edu.get('date', '')}\n"
            text += f"    {edu.get('details', '')}\n\n"

        if certifications:
            text += f"\nCertifications: {', '.join(certifications)}\n"
        
        if languages:
            text += f"Languages: {', '.join(languages)}\n"

        return text
