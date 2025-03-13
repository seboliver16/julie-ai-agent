"""
Julie AI Agent - Main Application

This file contains the main Flask application for the Julie AI Agent.
It defines routes for user input, expert search, and scheduling.
"""

import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from utils import linkedin, email, db, nlp, monitor

# Initialize Flask app
app = Flask(__name__)

# Load configuration
if os.path.exists('config.py'):
    app.config.from_pyfile('config.py')
else:
    # Default configuration
    app.config['SECRET_KEY'] = 'development-key'
    app.config['DEBUG'] = True
    os.environ['USE_MOCK_LINKEDIN'] = 'True'
    os.environ['USE_MOCK_EMAIL'] = 'True'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize database
db.init_db()

@app.route('/')
def index():
    """
    Render the home page with the input form.
    Users can enter their query and email here.
    """
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """
    Process the search form:
    1. Get user query and email from form
    2. Search for experts on LinkedIn
    3. Rank experts using NLP
    4. Store results in session
    5. Render search results page
    """
    # Get form data
    query = request.form.get('query')
    user_email = request.form.get('email')
    
    # Store in session for later use
    session['query'] = query
    session['user_email'] = user_email
    
    # Log the search request for monitoring
    monitor.log_action('search_initiated', {'query': query, 'email': user_email})
    
    # Record start time for performance tracking
    start_time = time.time()
    
    # Search for experts
    experts = linkedin.search_experts(query)
    
    # Rank experts
    ranked_experts = nlp.rank_experts(experts, query)
    
    # Store in session
    session['experts'] = ranked_experts
    
    # Calculate search time
    search_time = round(time.time() - start_time, 2)
    
    # Log the search results
    monitor.log_action('search_completed', {
        'experts_found': len(ranked_experts),
        'search_time': search_time
    })
    
    return render_template('search_results.html', experts=ranked_experts)

@app.route('/schedule', methods=['POST'])
def schedule():
    """
    Process the expert selection form:
    1. Get selected expert IDs from form
    2. Retrieve expert details from session
    3. Send email to user with selected experts
    4. Render confirmation page
    """
    # Get selected expert IDs
    expert_ids = request.form.getlist('expert_id')
    
    # Get experts from session
    all_experts = session.get('experts', [])
    
    # Filter selected experts
    selected_experts = [expert for expert in all_experts if expert['id'] in expert_ids]
    
    # Get user email from session
    user_email = session.get('user_email')
    query = session.get('query')
    
    # Log scheduling initiation
    monitor.log_action('scheduling_initiated', {
        'selected_experts': len(selected_experts),
        'user_email': user_email
    })
    
    # Send email with selected experts
    email_status = email.send_expert_selection_email(user_email, selected_experts, query)
    
    # Log scheduling completion
    monitor.log_action('scheduling_completed', {
        'user_email': user_email,
        'email_status': 'sent' if email_status else 'failed'
    })
    
    return render_template('schedule.html', experts=selected_experts)

@app.route('/monitor')
def monitor_view():
    """
    Render the monitoring page where users can see Julie's actions.
    """
    # Get monitor data
    monitor_data = monitor.get_monitor_data()
    return render_template('monitor.html', **monitor_data)

@app.route('/api/monitor/updates')
def monitor_updates():
    """
    API endpoint for getting real-time updates for the monitor page.
    """
    since_id = request.args.get('since', 0, type=int)
    new_actions = monitor.get_actions_since(since_id)
    return jsonify(new_actions)

if __name__ == '__main__':
    app.run(debug=True)