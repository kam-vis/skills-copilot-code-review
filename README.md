# Mergington High School Activities

This project is a FastAPI-based school activities app with role-based teacher login, announcements, and extracurricular signups.

## Features

- Browse extracurricular activities and filter by day, category, and time
- Register and unregister students when signed in
- View a dynamic school announcement banner driven from the database
- Manage announcements from a modal dialog available only to signed-in users
- Seed example data during database initialization

## Local run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start MongoDB locally on port 27017.

3. Run the app:
   ```bash
   uvicorn src.app:app --reload
   ```

4. Open the app in a browser at http://localhost:8000

## API overview

- GET /activities — list activities with optional filters for day, start_time, and end_time
- POST /activities/{activity_name}/signup — register a student, requiring a signed-in teacher
- POST /activities/{activity_name}/unregister — remove a student, requiring a signed-in teacher
- POST /auth/login — log in with a teacher username/password
- GET /auth/check-session — validate a current teacher session
- GET /announcements — list all announcements, including metadata and dates
- GET /announcements/active — list active announcements only
- POST /announcements — create a new announcement (teacher-only management action)
- PUT /announcements/{announcement_id} — update an announcement (teacher-only management action)
- DELETE /announcements/{announcement_id} — delete an announcement (teacher-only management action)

## Announcement data model

Announcements are stored in MongoDB with:

- message: the announcement text
- start_date: optional, format YYYY-MM-DD
- expires_at: required, format YYYY-MM-DD

The database initialization includes example announcement content to demonstrate the behavior. 
