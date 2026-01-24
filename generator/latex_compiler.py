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
        self.temp_dir = 'temp'
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
        tex_file = os.path.join(self.temp_dir, f'resume_{timestamp}.tex')
        pdf_file = os.path.join(self.temp_dir, f'resume_{timestamp}.pdf')
        
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        # Compile LaTeX to PDF
        try:
            # Run pdflatex
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', self.temp_dir, tex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"LaTeX compilation warning/error: {result.stderr}")
            
            if os.path.exists(pdf_file):
                return pdf_file
            else:
                raise Exception("PDF file was not generated")
                
        except FileNotFoundError:
            # pdflatex not installed, create a simple text file as fallback
            print("Warning: pdflatex not found, creating text version")
            txt_file = pdf_file.replace('.pdf', '.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_text_resume(resume_content))
            # Return with .txt extension to be clear about format
            return txt_file
        except Exception as e:
            print(f"Error compiling LaTeX: {e}")
            raise
    
    def _generate_latex(self, content: Dict) -> str:
        """Generate LaTeX code for resume"""
        
        # Sanitize all text inputs to prevent LaTeX injection
        def sanitize_latex(text: str) -> str:
            """Escape special LaTeX characters"""
            if not text:
                return ''
            # Escape special LaTeX characters
            replacements = {
                '\\': r'\textbackslash{}',
                '&': r'\&',
                '%': r'\%',
                '$': r'\$',
                '#': r'\#',
                '_': r'\_',
                '{': r'\{',
                '}': r'\}',
                '~': r'\textasciitilde{}',
                '^': r'\textasciicircum{}',
            }
            for char, replacement in replacements.items():
                text = text.replace(char, replacement)
            return text
        
        name = sanitize_latex(content.get('name', 'Your Name'))
        email = sanitize_latex(content.get('email', ''))
        location = sanitize_latex(content.get('location', ''))
        github = sanitize_latex(content.get('github_url', ''))
        linkedin = sanitize_latex(content.get('linkedin_url', ''))
        summary = sanitize_latex(content.get('summary', ''))
        skills = content.get('skills', [])
        projects = content.get('projects', [])
        
        # Build contact info
        contact_parts = []
        if email:
            # Email needs to be sanitized but the actual email in mailto should not be double-escaped
            contact_parts.append(f"\\href{{mailto:{content.get('email', '')}}}{{{email}}}")
        if location:
            contact_parts.append(location)
        if github:
            contact_parts.append(f"\\href{{https://{github}}}{{{github}}}")
        if linkedin:
            contact_parts.append(f"\\href{{{linkedin}}}{{LinkedIn}}")
        
        contact_line = " $|$ ".join(contact_parts)
        
        # Build skills section
        skills_text = ", ".join([sanitize_latex(s) for s in skills[:15]]) if skills else "Python, JavaScript, Git"
        
        # Build projects section
        projects_section = ""
        for proj in projects[:5]:
            proj_name = sanitize_latex(proj.get('name', 'Project'))
            proj_desc = sanitize_latex(proj.get('description', 'Project description'))
            proj_tech = proj.get('technologies', [])
            tech_str = ", ".join([sanitize_latex(t) for t in proj_tech[:5]]) if proj_tech else ""
            
            projects_section += f"""
\\textbf{{{proj_name}}} \\\\
{proj_desc} \\\\
\\textit{{Technologies: {tech_str}}} \\\\[0.5em]
"""
        
        latex_template = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[margin=0.7in]{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}

% Format section titles
\\titleformat{{\\section}}{{\\Large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing{{\\section}}{{0pt}}{{10pt}}{{5pt}}

% Remove page numbers
\\pagestyle{{empty}}

\\begin{{document}}

% Header
\\begin{{center}}
    {{\\Huge \\textbf{{{name}}}}} \\\\[0.3em]
    {contact_line}
\\end{{center}}

\\vspace{{0.5em}}

% Summary
\\section*{{Professional Summary}}
{summary}

% Skills
\\section*{{Technical Skills}}
{skills_text}

% Projects
\\section*{{Notable Projects}}
{projects_section}

\\end{{document}}
"""
        
        return latex_template
    
    def _generate_text_resume(self, content: Dict) -> str:
        """Generate plain text resume as fallback"""
        name = content.get('name', 'Your Name')
        email = content.get('email', '')
        location = content.get('location', '')
        github = content.get('github_url', '')
        summary = content.get('summary', '')
        skills = content.get('skills', [])
        projects = content.get('projects', [])
        
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

Notable Projects:
"""
        
        for proj in projects[:5]:
            text += f"""
  {proj.get('name', 'Project')}
    {proj.get('description', '')}
    Technologies: {', '.join(proj.get('technologies', [])[:5])}
"""
        
        return text
