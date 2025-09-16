# Field Issue Logger

A Flask web application for logging and tracking field issues with SQLite database backend.

## Features

- **Dashboard**: View summary statistics and all issues in a searchable/filterable table
- **Issue Logging**: Easy form to log new issues with validation
- **Search & Filter**: Filter issues by location and type, sort by date, urgency, or type
- **Responsive Design**: Professional Bootstrap-based UI that works on all devices
- **Network Sharing**: Run locally and share with coworkers on the same network

## Requirements

- Python 3.7 or higher
- Flask 2.3.3
- Modern web browser

## Installation and Setup

### 1. Download/Clone the Application
Ensure all files are in a folder called `field_issue_logger`:
```
field_issue_logger/
├── app.py
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── dashboard.html
    └── new_issue.html
```

### 2. Install Python Dependencies
Open Command Prompt or PowerShell in the `field_issue_logger` folder and run:

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Start the Flask development server
python app.py
```

You should see output like:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-ip]:5000
```

### 4. Access the Application

- **Locally**: Open your browser and go to `http://localhost:5000`
- **Network Access**: Other computers on your network can access it at `http://[your-computer-ip]:5000`

### 5. Sharing with Coworkers

To find your computer's IP address:

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network connection.

**Share this URL with coworkers:**
```
http://[your-ip-address]:5000
```

For example: `http://192.168.1.100:5000`

## Usage

### Dashboard (Homepage)
- View summary statistics (total issues, counts by urgency)
- See all high-priority issues at a glance
- Search issues by location
- Filter issues by type
- Sort by date, urgency, or type
- Click "Add New Issue" to log a new issue

### Logging New Issues
1. Click "Add New Issue" from the dashboard
2. Fill out the form:
   - **Date**: Defaults to today, but can be changed
   - **Location**: Specific location where issue was found
   - **Issue Type**: Safety, Quality, Access, Coordination, or Other
   - **Description**: Detailed description of the issue
   - **Urgency**: Low, Medium, or High priority
3. Click "Log Issue" to save

### Database
- Issues are automatically stored in `issues.db` SQLite database
- Database is created automatically when you first run the app
- Data persists between application restarts

## Stopping the Application

Press `Ctrl+C` in the terminal/command prompt where the app is running.

## Troubleshooting

### Port Already in Use
If you see "Address already in use" error, either:
- Stop the existing Flask app running on port 5000
- Change the port in `app.py` (line 123): `app.run(debug=True, host='0.0.0.0', port=5001)`

### Cannot Connect from Other Computers
- Make sure Windows Firewall allows connections on port 5000
- Ensure both computers are on the same network
- Try temporarily disabling firewall to test connectivity

### Database Issues
If you encounter database errors:
- Delete the `issues.db` file (this will remove all data)
- Restart the application to recreate the database

## Security Note

This application is designed for local network use. For production deployment, consider:
- Setting a strong secret key
- Using a production WSGI server (like Gunicorn)
- Implementing proper authentication
- Using HTTPS

## Support

For issues with this application, check the Flask documentation at https://flask.palletsprojects.com/