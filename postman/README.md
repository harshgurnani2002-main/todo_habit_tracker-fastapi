# Postman Collections for Todo Habit Tracker

This directory contains Postman collections for testing all APIs in the Todo Habit Tracker application.

## Collections Included

1. **Auth_API.postman_collection.json** - Authentication APIs
2. **Todo_API.postman_collection.json** - Todo management APIs with filter examples
3. **Habit_API.postman_collection.json** - Habit tracking APIs with filter examples
4. **Pomodoro_API.postman_collection.json** - Pomodoro session APIs with filter examples
5. **Dashboard_API.postman_collection.json** - Dashboard analytics APIs with filter examples
6. **Admin_API.postman_collection.json** - Admin management APIs with filter examples
7. **Todo_Habit_Tracker_Environment.postman_environment.json** - Environment variables for the collections

## How to Use

1. **Import Collections**:
   - Open Postman
   - Click "Import" button
   - Select all JSON files in this directory
   - Click "Import"

2. **Set Up Environment**:
   - Click the "Environment" dropdown (top right)
   - Select "Todo Habit Tracker Environment"
   - Modify the `base_url` if your server runs on a different host/port
   - After logging in, update the `access_token` variable with your JWT token

3. **Using the Collections**:
   - Start with the Auth collection to register and login
   - Copy the access token from the login response
   - Set the `access_token` variable in the environment
   - Test other APIs using the token for authorization

## API Overview

### Authentication
- User registration and login
- Google OAuth integration
- OTP-based authentication
- 2FA setup and verification
- Password reset functionality

### Todos
- Create, read, update, delete todos
- Filter by completion status, priority, category
- Search in title/description
- Date range filtering
- Sorting options

### Habits
- Create, read, update, delete habits
- Track habit entries
- View analytics and streaks
- Filter by frequency, activity status
- Date range filtering and sorting

### Pomodoro
- Create and manage pomodoro sessions
- View productivity analytics
- Filter by activity status
- Date range filtering and sorting

### Dashboard
- View productivity statistics
- Filter by date ranges, categories, priorities

### Admin
- View system-wide analytics
- Manage users, todos, and habits
- Filter and search across all entities

## Filter Examples

All collections include examples of:
- Basic filtering (e.g., by status, category, priority)
- Text search in relevant fields
- Date range filtering
- Sorting by different fields
- Combining multiple filters

These examples help demonstrate the full capabilities of each API endpoint.