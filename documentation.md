# Todo Habit Tracker API Documentation

## Overview

The Todo Habit Tracker API is a comprehensive productivity application that allows users to manage todos, track habits, and utilize Pomodoro technique for time management. This documentation provides detailed information about all available API endpoints, request/response formats, and filtering options.

## Table of Contents

1. [Authentication](#authentication)
2. [Todos API](#todos-api)
3. [Habits API](#habits-api)
4. [Pomodoro API](#pomodoro-api)
5. [Dashboard API](#dashboard-api)
6. [Admin API](#admin-api)
7. [Data Models](#data-models)

## Authentication

### Register User

**POST** `/auth/register`

Register a new user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "is_active": true,
  "is_verified": false,
  "is_admin": false,
  "profile_picture": null,
  "last_otp_verified": null,
  "created_at": "2023-01-01T00:00:00"
}
```

### Login User

**POST** `/auth/login`

Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "otp_code": "123456"  // Required if 2FA is enabled
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Google Login

**GET** `/auth/google/login`

Get Google OAuth2 login URL.

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### Google Callback

**GET** `/auth/google/callback?code=AUTH_CODE`

Handle Google OAuth2 callback.

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Send OTP

**POST** `/auth/send-otp`

Send OTP code to email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully"
}
```

### Verify OTP

**POST** `/auth/verify-otp`

Verify OTP code and login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Enable 2FA

**POST** `/auth/enable-2fa`

Enable two-factor authentication.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "message": "Scan the QR code with your authenticator app and verify with an OTP"
}
```

### Verify 2FA Setup

**POST** `/auth/verify-2fa?otp_code=123456`

Verify 2FA setup with OTP code.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "2FA enabled successfully"
}
```

### Forgot Password

**POST** `/auth/forgot-password`

Request password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

### Reset Password

**POST** `/auth/reset-password`

Reset password with token.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully"
}
```

### Get Current User

**GET** `/auth/me`

Get current user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "profile_picture": null,
  "last_otp_verified": "2023-01-01T00:00:00",
  "created_at": "2023-01-01T00:00:00"
}
```

## Todos API

### Create Todo

**POST** `/todos/`

Create a new todo item.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "medium",  // low, medium, high
  "category": "personal",
  "due_date": "2023-12-31T23:59:59"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "priority": "medium",
  "category": "personal",
  "due_date": "2023-12-31T23:59:59",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "completed_at": null,
  "owner_id": 1
}
```

### Get Todos

**GET** `/todos/`

Get a list of todos with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 50) - Number of items to return
- `completed` (bool, optional) - Filter by completion status
- `priority` (string, optional) - Filter by priority (low, medium, high)
- `category` (string, optional) - Filter by category
- `search` (string, optional) - Search in title or description
- `due_date_from` (date, optional) - Filter by due date (from)
- `due_date_to` (date, optional) - Filter by due date (to)
- `created_from` (date, optional) - Filter by creation date (from)
- `created_to` (date, optional) - Filter by creation date (to)
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": false,
    "priority": "medium",
    "category": "personal",
    "due_date": "2023-12-31T23:59:59",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": null,
    "completed_at": null,
    "owner_id": 1
  }
]
```

### Get Todo by ID

**GET** `/todos/{todo_id}`

Get a specific todo by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "priority": "medium",
  "category": "personal",
  "due_date": "2023-12-31T23:59:59",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "completed_at": null,
  "owner_id": 1
}
```

### Update Todo

**PUT** `/todos/{todo_id}`

Update a specific todo by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Buy groceries and vegetables",
  "description": "Milk, eggs, bread, carrots",
  "is_completed": true,
  "priority": "high",
  "category": "shopping",
  "due_date": "2023-12-31T23:59:59"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries and vegetables",
  "description": "Milk, eggs, bread, carrots",
  "is_completed": true,
  "priority": "high",
  "category": "shopping",
  "due_date": "2023-12-31T23:59:59",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T01:00:00",
  "completed_at": "2023-01-01T01:00:00",
  "owner_id": 1
}
```

### Delete Todo

**DELETE** `/todos/{todo_id}`

Delete a specific todo by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```
Status: 204 No Content
```

## Habits API

### Create Habit

**POST** `/habits/`

Create a new habit.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Drink water",
  "description": "Drink 8 glasses of water daily",
  "frequency": "daily",  // daily, weekly, monthly
  "target_count": 8
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Drink water",
  "description": "Drink 8 glasses of water daily",
  "frequency": "daily",
  "target_count": 8,
  "is_active": true,
  "streak_count": 0,
  "best_streak": 0,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "owner_id": 1,
  "entries": []
}
```

### Get Habits

**GET** `/habits/`

Get a list of habits with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `active_only` (bool, default: true) - Filter by active status
- `frequency` (string, optional) - Filter by frequency (daily, weekly, monthly)
- `search` (string, optional) - Search in name or description
- `created_from` (date, optional) - Filter by creation date (from)
- `created_to` (date, optional) - Filter by creation date (to)
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Drink water",
    "description": "Drink 8 glasses of water daily",
    "frequency": "daily",
    "target_count": 8,
    "is_active": true,
    "streak_count": 5,
    "best_streak": 10,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": null,
    "owner_id": 1,
    "entries": []
  }
]
```

### Get Habit by ID

**GET** `/habits/{habit_id}`

Get a specific habit by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Drink water",
  "description": "Drink 8 glasses of water daily",
  "frequency": "daily",
  "target_count": 8,
  "is_active": true,
  "streak_count": 5,
  "best_streak": 10,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "owner_id": 1,
  "entries": []
}
```

### Update Habit

**PUT** `/habits/{habit_id}`

Update a specific habit by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Drink water and exercise",
  "description": "Drink 8 glasses of water and do 30 minutes exercise daily",
  "frequency": "daily",
  "target_count": 2,
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Drink water and exercise",
  "description": "Drink 8 glasses of water and do 30 minutes exercise daily",
  "frequency": "daily",
  "target_count": 2,
  "is_active": true,
  "streak_count": 5,
  "best_streak": 10,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T01:00:00",
  "owner_id": 1,
  "entries": []
}
```

### Delete Habit

**DELETE** `/habits/{habit_id}`

Delete a specific habit by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Habit deleted successfully"
}
```

### Get Habit Analytics

**GET** `/habits/{habit_id}/analytics`

Get analytics for a specific habit.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days` (int, default: 30) - Number of days to analyze

**Response:**
```json
{
  "total_entries": 25,
  "completed_entries": 20,
  "completion_rate": 80.0,
  "current_streak": 5,
  "best_streak": 10,
  "average_completion": 1.2
}
```

### Create Habit Entry

**POST** `/habits/{habit_id}/entries`

Create a new habit entry.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "completed_count": 2,
  "notes": "Completed morning and evening",
  "date": "2023-01-01T00:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "completed_count": 2,
  "notes": "Completed morning and evening",
  "date": "2023-01-01T00:00:00",
  "habit_id": 1
}
```

### Get Habit Entries

**GET** `/habits/{habit_id}/entries`

Get entries for a specific habit.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `date_from` (date, optional) - Filter by date (from)
- `date_to` (date, optional) - Filter by date (to)
- `sort_by` (string, default: "date") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "completed_count": 2,
    "notes": "Completed morning and evening",
    "date": "2023-01-01T00:00:00",
    "habit_id": 1
  }
]
```

### Get Aggregate Habit Analytics

**GET** `/habits/analytics/aggregate`

Get analytics for all habits combined.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days` (int, default: 30) - Number of days to analyze

**Response:**
```json
{
  "stats": {
    "total_habits": 5,
    "active_habits": 4,
    "completed_today": 3,
    "completion_rate": 75.0,
    "average_streak": 4.2,
    "best_streak": 15
  },
  "frequency_distribution": {
    "daily": 3,
    "weekly": 1,
    "monthly": 1
  },
  "completion_trend": [
    {
      "date": "2023-01-01",
      "completed": 2
    }
  ],
  "category_completion": {
    "daily": 3,
    "weekly": 1,
    "monthly": 1
  }
}
```

## Pomodoro API

### Create Pomodoro Session

**POST** `/pomodoro/`

Create a new Pomodoro session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Work on project",
  "description": "Focus on completing the project tasks",
  "duration": 25,  // in minutes
  "break_duration": 5  // in minutes
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Work on project",
  "description": "Focus on completing the project tasks",
  "duration": 25,
  "break_duration": 5,
  "is_active": true,
  "completed_at": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "owner_id": 1
}
```

### Get Pomodoro Analytics

**GET** `/pomodoro/analytics`

Get analytics for Pomodoro sessions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days` (int, default: 30) - Number of days to analyze

**Response:**
```json
{
  "total_sessions": 10,
  "completed_sessions": 8,
  "completion_rate": 80.0,
  "average_duration": 25.0,
  "total_time": 200
}
```

### Get Pomodoro Sessions

**GET** `/pomodoro/`

Get a list of Pomodoro sessions with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `active_only` (bool, default: true) - Filter by active status
- `search` (string, optional) - Search in title or description
- `created_from` (date, optional) - Filter by creation date (from)
- `created_to` (date, optional) - Filter by creation date (to)
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Work on project",
    "description": "Focus on completing the project tasks",
    "duration": 25,
    "break_duration": 5,
    "is_active": true,
    "completed_at": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": null,
    "owner_id": 1
  }
]
```

### Get Pomodoro Session by ID

**GET** `/pomodoro/{pomodoro_id}`

Get a specific Pomodoro session by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Work on project",
  "description": "Focus on completing the project tasks",
  "duration": 25,
  "break_duration": 5,
  "is_active": true,
  "completed_at": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null,
  "owner_id": 1
}
```

### Update Pomodoro Session

**PUT** `/pomodoro/{pomodoro_id}`

Update a specific Pomodoro session by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Work on project and documentation",
  "description": "Focus on completing the project tasks and update documentation",
  "duration": 30,
  "break_duration": 5,
  "is_active": true,
  "completed_at": "2023-01-01T00:30:00"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Work on project and documentation",
  "description": "Focus on completing the project tasks and update documentation",
  "duration": 30,
  "break_duration": 5,
  "is_active": true,
  "completed_at": "2023-01-01T00:30:00",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T01:00:00",
  "owner_id": 1
}
```

### Delete Pomodoro Session

**DELETE** `/pomodoro/{pomodoro_id}`

Delete a specific Pomodoro session by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Pomodoro session deleted successfully"
}
```

## Dashboard API

### Get Dashboard Stats

**GET** `/dashboard/stats`

Get dashboard statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date` (date, optional) - Start date for statistics
- `end_date` (date, optional) - End date for statistics
- `category` (string, optional) - Filter by todo category
- `priority` (string, optional) - Filter by todo priority

**Response:**
```json
{
  "todo_stats": {
    "total": 10,
    "completed": 7,
    "pending": 3,
    "completion_rate": 70.0
  },
  "habit_stats": {
    "total": 5,
    "active": 4,
    "completion_rate": 80.0,
    "average_streak": 4.2
  },
  "productivity_trend": [
    {
      "date": "2023-01-01",
      "todos_completed": 2,
      "habits_completed": 3
    }
  ],
  "category_distribution": {
    "work": 5,
    "personal": 3,
    "shopping": 2
  },
  "priority_distribution": {
    "high": 3,
    "medium": 5,
    "low": 2
  }
}
```

## Admin API

### Get Admin Dashboard

**GET** `/admin/dashboard`

Get admin dashboard statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_stats": {
    "total_users": 50,
    "active_users": 45,
    "admin_users": 2
  },
  "todo_stats": {
    "total_todos": 200,
    "completed_todos": 150,
    "pending_todos": 50
  },
  "habit_stats": {
    "total_habits": 100,
    "active_habits": 80
  }
}
```

### Get Users

**GET** `/admin/users`

Get a list of users with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `is_active` (bool, optional) - Filter by active status
- `is_admin` (bool, optional) - Filter by admin status
- `is_verified` (bool, optional) - Filter by verification status
- `search` (string, optional) - Search in email, full_name, or username
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "User Name",
    "is_active": true,
    "is_verified": true,
    "is_admin": false,
    "profile_picture": null,
    "last_otp_verified": "2023-01-01T00:00:00",
    "created_at": "2023-01-01T00:00:00"
  }
]
```

### Get User by ID

**GET** `/admin/users/{user_id}`

Get a specific user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "profile_picture": null,
  "last_otp_verified": "2023-01-01T00:00:00",
  "created_at": "2023-01-01T00:00:00"
}
```

### Update User

**PUT** `/admin/users/{user_id}`

Update a specific user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "is_active": true,
  "is_admin": false,
  "is_verified": true
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "profile_picture": null,
  "last_otp_verified": "2023-01-01T00:00:00",
  "created_at": "2023-01-01T00:00:00"
}
```

### Delete User

**DELETE** `/admin/users/{user_id}`

Delete a specific user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```
Status: 204 No Content
```

### Get All Todos (Admin)

**GET** `/admin/todos`

Get all todos with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `is_completed` (bool, optional) - Filter by completion status
- `priority` (string, optional) - Filter by priority
- `category` (string, optional) - Filter by category
- `user_id` (int, optional) - Filter by user ID
- `search` (string, optional) - Search in title or description
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": false,
    "priority": "medium",
    "category": "personal",
    "due_date": "2023-12-31T23:59:59",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": null,
    "completed_at": null,
    "owner_id": 1
  }
]
```

### Get All Habits (Admin)

**GET** `/admin/habits`

Get all habits with optional filtering and sorting.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 100) - Number of items to return
- `is_active` (bool, optional) - Filter by active status
- `frequency` (string, optional) - Filter by frequency
- `user_id` (int, optional) - Filter by user ID
- `search` (string, optional) - Search in name or description
- `sort_by` (string, default: "created_at") - Sort by field
- `sort_order` (string, default: "desc") - Sort order (asc or desc)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Drink water",
    "description": "Drink 8 glasses of water daily",
    "frequency": "daily",
    "target_count": 8,
    "is_active": true,
    "streak_count": 5,
    "best_streak": 10,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": null,
    "owner_id": 1,
    "entries": []
  }
]
```

## Data Models

### User

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| email | string | User's email address |
| username | string (optional) | User's username |
| full_name | string (optional) | User's full name |
| is_active | boolean | Whether the user account is active |
| is_verified | boolean | Whether the user's email is verified |
| is_admin | boolean | Whether the user has admin privileges |
| profile_picture | string (optional) | URL to user's profile picture |
| is_2fa_enabled | boolean | Whether two-factor authentication is enabled |
| last_otp_verified | datetime (optional) | Timestamp of last OTP verification |
| created_at | datetime | When the user account was created |

### Todo

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| title | string | Todo title |
| description | string | Todo description |
| is_completed | boolean | Whether the todo is completed |
| priority | string | Priority level (low, medium, high) |
| category | string (optional) | Todo category |
| due_date | datetime (optional) | Due date for the todo |
| created_at | datetime | When the todo was created |
| updated_at | datetime (optional) | When the todo was last updated |
| completed_at | datetime (optional) | When the todo was completed |
| owner_id | integer | ID of the user who owns this todo |

### Habit

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| name | string | Habit name |
| description | string (optional) | Habit description |
| frequency | string | How often to perform the habit (daily, weekly, monthly) |
| target_count | integer | Target number of completions per frequency period |
| is_active | boolean | Whether the habit is active |
| streak_count | integer | Current streak count |
| best_streak | integer | Best streak achieved |
| created_at | datetime | When the habit was created |
| updated_at | datetime (optional) | When the habit was last updated |
| owner_id | integer | ID of the user who owns this habit |

### HabitEntry

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| completed_count | integer | Number of times the habit was completed |
| notes | string (optional) | Notes about the habit completion |
| date | datetime | Date of the habit entry |
| habit_id | integer | ID of the habit this entry belongs to |

### PomodoroSession

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| title | string | Session title |
| description | string (optional) | Session description |
| duration | integer | Session duration in minutes |
| break_duration | integer | Break duration in minutes |
| is_active | boolean | Whether the session is active |
| completed_at | datetime (optional) | When the session was completed |
| created_at | datetime | When the session was created |
| updated_at | datetime (optional) | When the session was last updated |
| owner_id | integer | ID of the user who owns this session |