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
                print(
                    f"LaTeX compilation warning/error:\n{result.stdout}\n{result.stderr}"
                )

            if os.path.exists(pdf_file):
                return pdf_file
            else:
                raise Exception(
                    f"PDF file was not generated. Return code: {result.returncode}"
                )

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
            contact_items.append(
                f"\\href{{mailto:{content.get('email', '')}}}{{\\underline{{{email}}}}}"
            )
        if github:
            github_display = github.replace("https://", "").replace("http://", "")
            contact_items.append(
                f"\\href{{https://{github}}}{{\\underline{{{github_display}}}}}"
            )

        contact_line = " $|$ ".join(contact_items)

        # Decide how many experiences and projects to show to fit on one page
        # Prioritize experience, then projects.
        max_total_items = 6
        num_exp = len(experience)
        num_proj = len(projects)

        # We want to show as many experiences as possible, up to a limit of 3
        display_exp_count = min(num_exp, 3)
        # The rest goes to projects, also capped at 3
        display_proj_count = min(num_proj, 3)
        
        # Adjust bullets based on number of items
        total_displayed = display_exp_count + display_proj_count
        if total_displayed <= 4:
            max_bullets_exp = 4
            max_bullets_proj = 3
        elif total_displayed <= 5:
            max_bullets_exp = 3
            max_bullets_proj = 2
        else:
            max_bullets_exp = 2
            max_bullets_proj = 2

        # Build Experience items
        exp_latex = ""
        for exp in experience[:display_exp_count]:
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
            for bullet in bullets[:max_bullets_exp]:
                exp_latex += f"        \\resumeItem{{{sanitize_latex(bullet)}}}\n"
            exp_latex += "      \\resumeItemListEnd\n\n"

        # Build Education items
        edu_latex = ""
        for edu in education[:2]:
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
        for proj in projects[:display_proj_count]:
            p_name = sanitize_latex(proj.get("name", "Project"))
            p_desc = sanitize_latex(proj.get("description", ""))
            p_tech = ", ".join(
                [sanitize_latex(t) for t in proj.get("technologies", [])]
            )
            proj_title = f"\\textbf{{{p_name}}}"
            if p_tech:
                proj_title += f" $|$ \\emph{{{p_tech}}}"

            proj_latex += f"    \\resumeProjectHeading\n      {{{proj_title}}}{{}}\n      \\resumeItemListStart\n"
            # Split description into bullets if needed
            bullets = [b.strip() for b in p_desc.split("\n") if b.strip()]
            for bullet in bullets[:max_bullets_proj]:
                proj_latex += f"        \\resumeItem{{{sanitize_latex(bullet)}}}\n"
            proj_latex += "      \\resumeItemListEnd\n\n"

        # Build Skills
        skills_str = ", ".join([sanitize_latex(s) for s in skills[:30]])

        # Build Certifications - more compact if many
        cert_latex = ""
        if certifications:
            if len(certifications) > 3:
                # Comma separated for space efficiency
                certs_str = ", ".join([sanitize_latex(c) for c in certifications[:8]])
                cert_latex = f"    \\item[] \\small{{ {certs_str} }}"
            else:
                cert_items = []
                for cert in certifications[:3]:
                    cert_items.append(
                        f"    \\resumeProjectHeading\n      {{\\textbf{{{sanitize_latex(cert)}}}}}{{}}"
                    )
                cert_latex = "\n".join(cert_items)

        # Build Languages
        lang_str = ", ".join([sanitize_latex(l) for l in languages[:5]])

        # Build sections conditionally
        exp_section = ""
        if exp_latex.strip():
            exp_section = f"\\cvsection{{Experience}}\n\\begin{{itemize}}\n{exp_latex}\\end{{itemize}}"

        proj_section = ""
        if proj_latex.strip():
            proj_section = f"\\cvsection{{Notable Projects}}\n\\begin{{itemize}}\n{proj_latex}\\end{{itemize}}"

        edu_section = ""
        if edu_latex.strip():
            edu_section = f"\\cvsection{{Education}}\n\\begin{{itemize}}\n{edu_latex}\\end{{itemize}}"

        skills_section = ""
        if skills_str.strip():
            skills_section = f"""\\cvsection{{Technical Skills}}
\\begin{{itemize}}
    \\item[] \\small{{
     \\textbf{{Skills:}} {{{skills_str}}} \\vspace{{-7pt}}
    }}
\\end{{itemize}}"""

        cert_section = ""
        if cert_latex.strip():
            cert_section = f"\\cvsection{{Certifications}}\n\\begin{{itemize}}\n{cert_latex}\\end{{itemize}}"

        lang_section = ""
        if lang_str.strip():
            lang_section = f"""\\cvsection{{Languages}}
\\begin{{itemize}}
    \\item[] \\small{{
     {lang_str} \\vspace{{-7pt}}
    }}
\\end{{itemize}}"""

        # Full Template - "Zero-Dependency" Professional Style
        latex_template = f"""\\documentclass[letterpaper,11pt]{{article}}

\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\usepackage{{geometry}}
\\geometry{{left=0.5in, top=0.4in, right=0.5in, bottom=0.4in}}

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
  \\vspace{{5pt}}
  {{\\large \\scshape #1}} \\\\ \\hrule \\vspace{{3pt}}
}}

% Custom commands implementation using standard LaTeX
\\newcommand{{\\resumeItem}}[1]{{
  \\item \\small{{#1 \\vspace{{-2pt}}}}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\item[]
  \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{#1}} & #2 \\\\
    \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
  \\end{{tabular*}}\\vspace{{-5pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
  \\item[]
  \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\small#1 & #2 \\\\
  \\end{{tabular*}}\\vspace{{-5pt}}
}}

\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}\\small\\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parsep}}{{0pt}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-2pt}}}}

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

{edu_section}

{exp_section}

{proj_section}

{cert_section}

{skills_section}

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

Education:
"""
        for edu in education:
            text += f"  {edu.get('degree', '')}, {edu.get('school', '')} | {edu.get('date', '')}\n"
            text += f"    {edu.get('details', '')}\n\n"

        text += "Professional Experience:\n"
        for exp in experience[:3]:
            text += f"  {exp.get('role', '')} @ {exp.get('company', '')} | {exp.get('date', '')}\n"
            text += f"    {exp.get('description', '')}\n\n"

        text += "\nNotable Projects:\n"
        for proj in projects[:3]:
            text += f"  {proj.get('name', 'Project')}\n"
            text += f"    {proj.get('description', '')}\n"
            text += (
                f"    Technologies: {', '.join(proj.get('technologies', [])[:5])}\n\n"
            )

        if certifications:
            text += f"\nCertifications: {', '.join(certifications)}\n"

        text += f"\nTechnical Skills:\n  {', '.join(skills[:15])}\n"

        return text
