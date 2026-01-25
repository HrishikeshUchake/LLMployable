# LLMployable AI Coding Instructions

Expert instructions for coding in the LLMployable repository.

## 🏗️ Architecture & Component Flow
LLMployable follows a linear data processing pipeline:
1.  **Scrapers** ([scrapers/](scrapers/)): Fetch raw data from GitHub (API-based) or LinkedIn (placeholder).
2.  **Analyzer** ([analyzer/](analyzer/)): Uses Google Gemini AI to extract structured requirements from job descriptions.
3.  **Generator** ([generator/resume_generator.py](generator/resume_generator.py)): Uses Gemini to map profile data to job requirements, producing a structured JSON resume.
4.  **Compiler** ([generator/latex_compiler.py](generator/latex_compiler.py)): Transforms JSON into LaTeX and compiles to PDF via `pdflatex`.

## 🛠️ Critical Workflows
- **Running locally**: `python app.py` (Flask server).
- **Environment**: Requires `GEMINI_API_KEY` in `.env`. `GITHUB_TOKEN` is optional but recommended.
- **Testing**: Run [test_app.py](test_app.py) to verify component integration and API connectivity.
- **Demo**: Use [demo.py](demo.py) for a CLI-based execution flow.

## 🎨 Coding Conventions
- **AI Integration**: Use `google-generative-ai`. Always provide a non-AI fallback (see `_generate_basic_resume` in [generator/resume_generator.py](generator/resume_generator.py)).
- **LaTeX Safety**: ALWAYS use `sanitize_latex()` when inserting user or AI-generated content into LaTeX templates to prevent compilation errors and injection.
- **Error Handling**: Use `try-except` blocks around external API calls (Gemini, GitHub) with graceful degradation to local/mock data.
- **Type Hinting**: Use Python type hints (`Dict`, `List`, `str`) for all public method signatures.

## 🔗 Integration Patterns
- **JSON Contracts**: Components communicate primarily through dictionaries. When modifying AI prompts, ensure the JSON response schema is strictly enforced in the prompt text.
- **Path Management**: Use `os.path.join` for all file operations. Temporary files go in the `temp/` directory, managed by [generator/latex_compiler.py](generator/latex_compiler.py).

## ⚠️ Security & Performance
- **Input Sanitization**: LaTeX characters like `&`, `%`, `$`, `#`, `_` must be escaped.
- **API Rate Limits**: GitHub scraper should handle authenticated (higher limit) vs unauthenticated sessions.
- **Timeout**: Set 30s timeouts for `subprocess.run` (LaTeX) and AI generation to prevent hanging.
