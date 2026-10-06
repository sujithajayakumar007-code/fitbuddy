# FitBuddy

FitBuddy is an AI-powered fitness plan generator.

It uses:

- FastAPI
- Jinja2
- SQLite
- SQLAlchemy
- Google Gemini
- HTML/CSS
- REST APIs

The application can generate:

- Personalized 7-day workout plans
- Nutrition and recovery tips
- Updated plans based on user feedback
- Admin/coach user views

---

# 1. Requirements

Install:

- Python 3.11 or newer (64-bit; Python 3.12 is recommended on Windows)
- VS Code
- Internet connection for installing Python packages
- Gemini API key if you want real AI generation

---

# 2. Open the project

Open the FitBuddy folder in VS Code.

The project should contain:

FitBuddy/
    app/
    templates/
        static/
            tests/
    requirements.txt

---

# 3. Create virtual environment

Install 64-bit Python 3.12 from python.org. In the installer, enable
"Add python.exe to PATH". Open a new PowerShell terminal, then verify:

    python --version

It must report Python 3.12.x. Do not reuse the existing `.venv` if it was
created with the Microsoft Store Python 3.13; create a separate environment:

    Set-Location "C:\path\to\fitbuddy"
    python -m venv .venv312

If `python --version` still selects the wrong Python, use the Python 3.12
installation path directly (the default per-user path is shown below):

    & "$env:LocalAppData\Programs\Python\Python312\python.exe" -m venv .venv312

If your Python 3.12 installation is in a different location, substitute its
`python.exe` path. You do not need to activate the virtual environment.

---

# 4. Install dependencies

Run:

    .\.venv312\Scripts\python.exe -m pip install --upgrade pip

Then:

    .\.venv312\Scripts\python.exe -m pip install -r requirements.txt

---

# 5. Configure environment

No configuration is required for local testing; demo mode is enabled by
default and does not require a Gemini API key.

To use Gemini, create a `.env` file in the project root:

    DEMO_MODE=false
    GEMINI_API_KEY=your-api-key

For sample plans, keep `DEMO_MODE=true` and leave `GEMINI_API_KEY` empty.

---

# 6. Start the application

Run:

    .\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload

If Windows again reports that it blocked `_pydantic_core`, do not try to
bypass the device policy. Ask your administrator to approve the Python
installation or the package DLL, or run the project on a device where it is
permitted.

You should see something similar to:

    Uvicorn running on http://127.0.0.1:8000

---

# 7. Open FitBuddy

Open:

    http://127.0.0.1:8000

---

# 8. Create a test plan

Use:

User ID:

    user001

Name:

    Sujitha

Age:

    25

Weight:

    65

Goal:

    General Wellness

Intensity:

    Medium

Click:

    Generate My Plan

---

# 9. Test feedback

On the result page enter:

    Add more cardio and make Day 4 a rest day.

Click:

    Regenerate Plan

FitBuddy will generate an updated plan.

---

# 10. Admin page

Open:

    http://127.0.0.1:8000/view-all-users

The admin page template is `templates/all_user.html`.

This displays saved users and plans.

If ADMIN_KEY is configured in .env, use:

    http://127.0.0.1:8000/view-all-users?admin_key=YOUR_KEY

---

# 11. API documentation

FastAPI automatically provides Swagger documentation.

Open:

    http://127.0.0.1:8000/docs

Alternative:

    http://127.0.0.1:8000/redoc

---

# 12. API endpoints

Create plan:

POST /api/plans

Feedback:

POST /api/plans/feedback

Get user:

GET /api/users/{user_id}

Health:

GET /health

---

# 13. Example API request

POST /api/plans

JSON:

{
    "user_id": "user001",
    "name": "Sujitha",
    "age": 25,
    "weight": 65,
    "goal": "general wellness",
    "intensity": "medium"
}

---

# 14. Enable Gemini

Create a Gemini API key.

Then edit:

    .env

Set:

    DEMO_MODE=false

and:

    GEMINI_API_KEY=YOUR_REAL_API_KEY

The application will then use Gemini instead of the built-in demo responses.

---

# 15. Database

FitBuddy automatically creates:

    fitbuddy.db

The database contains:

    users

and:

    plans

You do not need to manually create the database.

---

# 16. Run tests

Run from the project root:

    .\.venv312\Scripts\python.exe -m pytest templates\static\tests\test_app.py -q

Expected tests include:

- Home page
- Admin page
- Health endpoint
- Plan generation
- Feedback-based plan update

---

# 17. Stop the server

Press:

    CTRL + C

---

# 18. Safety

FitBuddy provides general fitness and wellness information.

It should not be treated as:

- Medical diagnosis
- Medical treatment
- Emergency advice
- Prescription nutrition advice
- A substitute for a qualified healthcare professional

Users with injuries, pregnancy, chronic disease, severe pain,
or other medical concerns should seek appropriate professional
guidance.