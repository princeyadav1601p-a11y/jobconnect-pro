# JobConnect Pro — Final Year Online Job Application Project

A realistic recruitment portal inspired by common job-platform workflows, with original branding/UI.

## Features
- Job seeker, recruiter and admin roles
- Registration/login with hashed passwords
- Professional profiles, skills, education, experience and resume upload
- Search/filter by role, company, skill, location, job type and work mode
- Multiple realistic fictional jobs with salary, vacancies and requirements
- Save jobs, apply once, track application status
- Recruiter dashboard, job posting, applicant review and status updates
- Admin dashboard with platform statistics/users/jobs
- SQLite relational database created and seeded automatically
- Responsive modern UI

## VS Code execution
1. Extract ZIP and open the `JobConnect_Pro` folder in VS Code.
2. Terminal > New Terminal.
3. Run: `python -m pip install -r requirements.txt`
4. Run: `python app.py`
5. Open `http://127.0.0.1:5000`

Windows users can also double-click `run_windows.bat`.

## Demo accounts (password for all: demo123)
- Job seeker: aarav@demo.test
- Recruiter: recruiter@jobconnect.test
- Admin: admin@jobconnect.test

The database `jobconnect.db` is generated automatically on first run. Delete it and restart to reset demo data.

## Suggested viva modules
Authentication, role-based access, job management, job search, application tracking, candidate management, profile/resume management, admin reporting, SQLite database.
