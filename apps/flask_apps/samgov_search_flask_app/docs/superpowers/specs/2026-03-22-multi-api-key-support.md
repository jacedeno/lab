# SAM.gov Search App - Multi-API Key Management Spec

**Date:** 2026-03-22
**Project:** SAM.gov Federal Contract Opportunity Search - Multi-API Key Support
**Status:** Implemented

---

## 1. Overview

This specification covers the implementation of multi-API key management, allowing each user to store and manage multiple SAM.gov API keys with nicknames. This enables users to:
- Maintain several API keys for different purposes (work, personal, different organizations)
- Easily switch between active API keys
- Organize and identify keys with custom nicknames

---

## 2. Database Schema

### UserAPIKey Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Auto-increment ID |
| user_id | Integer | Foreign Key (user.id), Not Null | Owner of the API key |
| api_key | String(100) | Not Null | The actual SAM.gov API key |
| nickname | String(50) | Not Null | User-defined identifier |
| is_active | Boolean | Default: True | Whether this key is currently selected |
| created_at | DateTime | Default: utcnow | When the key was added |

### Relationships
- User has one-to-many relationship with UserAPIKey
- Cascade delete: when user is deleted, all their API keys are deleted

---

## 3. API Key Management Features

### 3.1 Add API Key

**Form Fields:**
- `nickname` (required): String, 3-50 characters, unique per user
- `api_key` (required): String, 10-100 characters

**Behavior:**
1. User enters nickname and API key
2. Click "Test Connection" validates the key against SAM.gov API
3. If validation fails, show error message
4. If nickname already exists for user, show error
5. On success, save the new key and set it as active
6. Automatically deactivate all other keys for this user
7. Redirect to settings page with success message

### 3.2 List API Keys

**Display:**
- Table showing all user's API keys
- Columns: Nickname, Status (Active/Inactive badge), Created Date, Actions
- Sorted by creation date (newest first)

### 3.3 Set Active API Key

**Behavior:**
- Click checkmark button on inactive key
- Deactivate all other keys for user
- Activate selected key
- Show success flash message

### 3.4 Delete API Key

**Behavior:**
- Click trash button with confirmation dialog
- Permanently remove the API key from database
- Show info flash message

---

## 4. Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/settings` | GET/POST | Display and manage API keys |
| `/settings/set_active_api/<id>` | POST | Set an API key as active |
| `/settings/delete_api/<id>` | POST | Delete an API key |

---

## 5. User Flow

### First-Time User
1. User logs in
2. Goes to Settings
3. Adds first API key with nickname (e.g., "Work Account")
4. Key is validated and saved
5. User can now perform searches

### Returning User
1. User logs in
2. Goes to Settings
3. Sees list of their API keys with active one highlighted
4. Can add new keys, switch active key, or delete old keys

### Search Behavior
- When user performs a search, the system uses `current_user.get_active_api_key()`
- Falls back to global `app.config.get('SAM_API_KEY')` if user has no active key
- Falls back to global `.env` SAM_API_KEY if neither exists

---

## 6. Forms

### AddAPIKeyForm

```python
class AddAPIKeyForm(FlaskForm):
    nickname = StringField('API Nickname', validators=[
        DataRequired(message='Nickname is required'),
        Length(min=3, max=50, message='Nickname must be between 3 and 50 characters')
    ])
    api_key = PasswordField('SAM.gov API Key', validators=[
        DataRequired(message='API key is required'),
        Length(min=10, max=100, message='API key must be between 10 and 100 characters')
    ])
    submit = SubmitField('Add API Key')
```

---

## 7. Security Considerations

1. **API Key Validation**: All keys are validated against SAM.gov API before saving
2. **Unique Nicknames**: Nicknames must be unique per user, not globally
3. **CSRF Protection**: All forms protected with CSRF tokens
4. **Secure Storage**: API keys stored as plain strings (no encryption, following original design)
5. **User Isolation**: Users can only manage their own API keys

---

## 8. Backward Compatibility

- The old `User.sam_api_key` field is retained for fallback purposes
- Existing users with API keys stored in `sam_api_key` will continue to work
- New multi-key system supplements, not replaces, the old single-key system
- Search routes check `get_active_api_key()` first, then fall back to `sam_api_key`

---

## 9. Future Enhancements

Potential improvements for API key management:
- API key expiration tracking
- Usage statistics per API key
- Key rotation suggestions
- Bulk import/export of keys
- API key permissions/scope validation