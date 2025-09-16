"""
Field Issue Logger - Flask Web Application
A web app for logging and tracking field issues with SQLite database backend.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database configuration
DATABASE = 'issues.db'

def get_db_connection():
    """Create and return a database connection with row factory for easy access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def init_db():
    """Initialize the database and create the issues table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT NOT NULL,
            urgency TEXT NOT NULL,
            resolved INTEGER DEFAULT 0
        )
    ''')
    
    # Add resolved column to existing tables (migration for existing databases)
    try:
        conn.execute('ALTER TABLE issues ADD COLUMN resolved INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists, which is fine
        pass
    
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    """Homepage dashboard showing summary statistics and all issues."""
    conn = get_db_connection()
    
    # Get search parameters from URL
    search_location = request.args.get('search_location', '')
    search_type = request.args.get('search_type', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'DESC')
    
    # Build the query with search filters
    query = "SELECT * FROM issues WHERE 1=1"
    params = []
    
    if search_location:
        query += " AND location LIKE ?"
        params.append(f"%{search_location}%")
    
    if search_type:
        query += " AND issue_type = ?"
        params.append(search_type)
    
    # Add sorting
    valid_sort_columns = ['date', 'urgency', 'issue_type', 'location']
    if sort_by in valid_sort_columns:
        if sort_by == 'urgency':
            # Custom ordering for urgency: High > Medium > Low
            query += f" ORDER BY CASE urgency WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END {sort_order}"
        else:
            query += f" ORDER BY {sort_by} {sort_order}"
    
    issues = conn.execute(query, params).fetchall()
    
    # Get summary statistics
    total_issues = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
    resolved_issues = conn.execute("SELECT COUNT(*) FROM issues WHERE resolved = 1").fetchone()[0]
    open_issues = total_issues - resolved_issues
    
    # Count issues by urgency (only open issues)
    urgency_counts = {}
    for urgency in ['Low', 'Medium', 'High']:
        count = conn.execute("SELECT COUNT(*) FROM issues WHERE urgency = ? AND resolved = 0", (urgency,)).fetchone()[0]
        urgency_counts[urgency] = count
    
    # Get all high urgency issues that are still open for quick reference
    high_urgency_issues = conn.execute(
        "SELECT * FROM issues WHERE urgency = 'High' AND resolved = 0 ORDER BY date DESC"
    ).fetchall()
    
    # Get unique issue types for filter dropdown
    issue_types = conn.execute("SELECT DISTINCT issue_type FROM issues ORDER BY issue_type").fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         issues=issues,
                         total_issues=total_issues,
                         resolved_issues=resolved_issues,
                         open_issues=open_issues,
                         urgency_counts=urgency_counts,
                         high_urgency_issues=high_urgency_issues,
                         issue_types=issue_types,
                         search_location=search_location,
                         search_type=search_type,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/new', methods=['GET', 'POST'])
def new_issue():
    """Page for creating a new issue."""
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        location = request.form.get('location')
        issue_type = request.form.get('issue_type')
        description = request.form.get('description')
        urgency = request.form.get('urgency')
        
        # Validate required fields
        if not all([date, location, issue_type, description, urgency]):
            flash('All fields are required!', 'error')
            return render_template('new_issue.html')
        
        # Insert new issue into database
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO issues (date, location, issue_type, description, urgency)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, location, issue_type, description, urgency))
            conn.commit()
            conn.close()
            
            flash('Issue logged successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            flash(f'Error saving issue: {str(e)}', 'error')
            return render_template('new_issue.html')
    
    # GET request - show the form with today's date as default
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('new_issue.html', today=today)

@app.route('/delete/<int:issue_id>', methods=['POST'])
def delete_issue(issue_id):
    """Delete an issue by ID."""
    try:
        conn = get_db_connection()
        
        # First check if the issue exists
        issue = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if not issue:
            flash('Issue not found!', 'error')
            conn.close()
            return redirect(url_for('dashboard'))
        
        # Delete the issue
        conn.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
        conn.commit()
        conn.close()
        
        flash(f'Issue #{issue_id} deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting issue: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/view/<int:issue_id>')
def view_issue(issue_id):
    """View detailed information about a specific issue."""
    try:
        conn = get_db_connection()
        
        # Get the specific issue
        issue = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        
        if not issue:
            flash('Issue not found!', 'error')
            conn.close()
            return redirect(url_for('dashboard'))
        
        conn.close()
        return render_template('view_issue.html', issue=issue)
        
    except Exception as e:
        flash(f'Error loading issue: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/toggle-resolved/<int:issue_id>', methods=['POST'])
def toggle_resolved(issue_id):
    """Toggle the resolved status of an issue."""
    try:
        conn = get_db_connection()
        
        # First check if the issue exists and get current status
        issue = conn.execute("SELECT resolved FROM issues WHERE id = ?", (issue_id,)).fetchone()
        if not issue:
            flash('Issue not found!', 'error')
            conn.close()
            return redirect(url_for('dashboard'))
        
        # Toggle the resolved status (0 -> 1, 1 -> 0)
        new_status = 1 if issue['resolved'] == 0 else 0
        
        # Update the database
        conn.execute("UPDATE issues SET resolved = ? WHERE id = ?", (new_status, issue_id))
        conn.commit()
        conn.close()
        
        # Provide user feedback
        status_text = "resolved" if new_status == 1 else "reopened"
        flash(f'Issue #{issue_id} marked as {status_text}!', 'success')
        
    except Exception as e:
        flash(f'Error updating issue: {str(e)}', 'error')
    
    # Check if we came from the view page
    referrer = request.headers.get('Referer', '')
    if f'/view/{issue_id}' in referrer:
        return redirect(url_for('view_issue', issue_id=issue_id))
    else:
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Initialize database when app starts
    init_db()
    
    # Run the app
    # host='0.0.0.0' allows access from other computers on the network
    # port=5000 is the default Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)