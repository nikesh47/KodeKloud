# Task Management Web Application

A simple and secure task management web application built with Flask and SQLite3. This application provides user authentication, task CRUD operations, and filtering capabilities.

## Features

- **Secure User Authentication**: User registration and login with Werkzeug password hashing
- **Task Management**: Create, read, update, and delete tasks
- **Task Properties**: Each task has a title, description, assigned user, and status
- **Status Management**: Five predefined statuses (Not started, In progress, Complete, Blocked, Closed)
- **Filtering**: Filter tasks by status and assignee
- **Responsive Design**: Modern, mobile-friendly interface built with CSS
- **Database**: SQLite3 database with proper relationships

## Prerequisites

- Python 3.13 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files** to your local machine

2. **Create a virtual environment**:
   ```bash
   python -m venv task_manager_env
   ```

3. **Activate the virtual environment**:
   
   **On Windows:**
   ```bash
   task_manager_env\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   source task_manager_env/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Make sure your virtual environment is activated**

2. **Run the Flask application**:
   ```bash
   python app.py
   ```

3. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Default Login Credentials

For testing purposes, a default admin user is created automatically:

- **Username**: `admin`
- **Password**: `admin123`

## Usage

### Getting Started

1. **Login** with the default credentials or register a new account
2. **Create tasks** using the "Create New Task" button
3. **View tasks** on the dashboard with status summaries
4. **Filter tasks** by status and assignee using the filter controls
5. **Edit or delete tasks** using the action buttons

### Task Management

- **Create**: Add new tasks with title, description, status, and assignee
- **Read**: View all tasks on the dashboard or individual task details
- **Update**: Edit existing tasks by clicking the "Edit" button
- **Delete**: Remove tasks with confirmation dialog

### Filtering

- **Status Filter**: Filter tasks by their current status
- **Assignee Filter**: Filter tasks by assigned user
- **Clear Filters**: Reset all filters to show all tasks

## Project Structure

```
task_manager/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── task_manager.db       # SQLite database (created automatically)
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Main dashboard with task list
│   ├── task_form.html    # Task creation/editing form
│   └── task_detail.html  # Individual task view
└── static/               # Static files
    └── style.css         # CSS styling
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password using Werkzeug
- `created_at`: Timestamp of account creation

### Tasks Table
- `id`: Primary key
- `title`: Task title
- `description`: Task description (optional)
- `status`: Task status (Not started, In progress, Complete, Blocked, Closed)
- `assigned_user_id`: Foreign key to users table
- `created_by_id`: Foreign key to users table (creator)
- `created_at`: Timestamp of task creation
- `updated_at`: Timestamp of last update

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's secure hashing
- **Session Management**: Secure session handling for user authentication
- **Input Validation**: Form validation and SQL injection protection
- **Authentication Required**: Protected routes require user login

## Browser Compatibility

This application is tested and compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 5000 is occupied, the application will show an error. Stop other applications using port 5000 or modify the port in `app.py`.

2. **Database issues**: If you encounter database errors, delete the `task_manager.db` file and restart the application to recreate the database.

3. **Virtual environment issues**: Make sure you've activated your virtual environment before running the application.

### Getting Help

If you encounter any issues:
1. Check that Python 3.13+ is installed
2. Verify all dependencies are installed correctly
3. Ensure the virtual environment is activated
4. Check the console output for error messages

## Development

To modify or extend this application:

1. **Database Changes**: Modify the `init_db()` function in `app.py`
2. **New Routes**: Add new route functions following the existing patterns
3. **Frontend**: Modify templates in the `templates/` directory and styles in `static/style.css`
4. **Dependencies**: Update `requirements.txt` if you add new packages

## License

This project is open source and available under the MIT License.
