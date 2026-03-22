# AGENTS.md - Instructions for AI Assistants

This file contains guidelines for AI agents working with the SAM.gov Search Flask Application.

---

## Project Overview

A Flask web application for searching federal contract opportunities using the SAM.gov API. Users can authenticate, search for opportunities, manage search history, and export results.

**Tech Stack:** Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF, WTForms, pandas, requests

---

## Important Conventions

### Code Language
- All code, comments, and documentation MUST be in English
- User interaction can be in Spanish or English as preferred by the user

### API Key Management
- Users store their own SAM.gov API keys in the database
- API keys are stored in the `UserAPIKey` model with a user-defined nickname
- Each user can have multiple API keys; only one is "active" at a time
- The active API key is retrieved via `current_user.get_active_api_key()`
- Fallback order: User's active API key → User's legacy `sam_api_key` → Global `app.config.get('SAM_API_KEY')`

### Database Models
- `User`: Authentication and basic profile
- `UserAPIKey`: User's SAM.gov API keys with nickname and active status
- `SearchHistory`: Stores search parameters and results count

### Forms
- `LoginForm`: Email/password authentication
- `SearchForm`: Search parameters for SAM.gov API
- `AddAPIKeyForm`: Nickname + API key for adding new keys
- `SettingsForm`: Legacy single API key management (retained for backward compatibility)

### Routes Pattern
- Use `@login_required` decorator for protected routes
- Use `current_user` to access authenticated user
- Flash messages: `'success'`, `'danger'`, `'info'`, `'warning'` categories

---

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask app with all routes |
| `utils/models.py` | SQLAlchemy models including UserAPIKey |
| `utils/forms.py` | WTForms definitions |
| `utils/api_client.py` | SAM.gov API client with test_connection and search_opportunities |
| `templates/settings.html` | API key management UI |

---

## Common Tasks

### Adding a New Route
1. Add route in `app.py` inside `create_app()` function
2. Use `@app.route()` decorator
3. Add `@login_required` if protected
4. Follow existing pattern for flash messages and redirects

### Adding a New Model
1. Add class to `utils/models.py`
2. Model must inherit from `db.Model`
3. Use `db.Column()` for columns
4. Add relationship to User model if needed

### Adding a New Form
1. Add class to `utils/forms.py`
2. Inherit from `FlaskForm`
3. Add validators as needed

### Modifying API Key Logic
- API key retrieval: `utils/models.py` → `User.get_active_api_key()`
- API key validation: `utils/api_client.py` → `SAMGovAPIClient.test_connection()`
- Settings route: `app.py` → `settings()` function

---

## Testing Commands

After making changes, verify:
```bash
# Check syntax
python3 -m py_compile app.py
python3 -m py_compile utils/models.py
python3 -m py_compile utils/forms.py

# If running locally
python app.py
```

---

## Docker Deployment

The application runs in Docker on a remote server (192.168.68.81:8503).

To deploy changes:
1. Commit and push to repository
2. SSH to server: `ssh root@192.168.68.81`
3. Pull latest code
4. Rebuild container: `docker build -t samgov-app .`
5. Restart container: `docker stop samgov-app && docker rm samgov-app && docker run -d --name samgov-app -p 8503:5000 samgov-app`

**Note:** Database is persisted in the container. If model changes require new tables, you may need to run `init_db.py` which will recreate all tables (losing data).

---

## Important Notes

1. **Backward Compatibility**: Keep `User.sam_api_key` field for legacy support
2. **API Key Security**: Never log or expose API keys in error messages
3. **CSRF Protection**: All forms use Flask-WTF CSRF tokens
4. **Session Storage**: Large search results stored in session; be mindful of size limits

---

## Specification Documents

Project specifications are stored in `docs/superpowers/specs/`:
- `2026-03-21-samgov-dashboard-design.md` - Original dashboard design spec
- `2026-03-22-multi-api-key-support.md` - Multi-API key management spec

When implementing features, refer to these specs for design decisions.