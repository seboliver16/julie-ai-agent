"""
Monitoring Module

This module handles logging and retrieving Julie's actions for real-time monitoring.
"""

import json
import time
import datetime
import sqlite3
import os
from utils import db

# Database file
DB_FILE = os.getenv('DB_FILE', 'julie.db')

def log_action(action_type, details=None):
    """
    Log an action performed by Julie.
    
    Args:
        action_type (str): Type of action (e.g., 'search_initiated', 'search_completed')
        details (dict, optional): Additional details about the action
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create actions table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Convert details to JSON string
    details_json = json.dumps(details) if details else None
    
    # Insert action
    cursor.execute('''
    INSERT INTO actions (action_type, details)
    VALUES (?, ?)
    ''', (action_type, details_json))
    
    conn.commit()
    conn.close()

def get_recent_actions(limit=20):
    """
    Get recent actions for monitoring.
    
    Args:
        limit (int, optional): Maximum number of actions to return
        
    Returns:
        list: List of action dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM actions
    ORDER BY timestamp DESC
    LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    
    actions = []
    for row in rows:
        action = dict(row)
        
        # Parse details JSON
        if action['details']:
            try:
                action['details'] = json.loads(action['details'])
            except:
                action['details'] = {}
        else:
            action['details'] = {}
            
        actions.append(action)
    
    conn.close()
    
    return actions

def get_actions_since(since_id=0):
    """
    Get actions since a specific ID.
    
    Args:
        since_id (int): Get actions with ID greater than this
        
    Returns:
        list: List of action dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM actions
    WHERE id > ?
    ORDER BY timestamp DESC
    LIMIT 50
    ''', (since_id,))
    
    actions = []
    for row in cursor.fetchall():
        action = dict(row)
        # Parse JSON details
        if action['details']:
            action['details'] = json.loads(action['details'])
        actions.append(action)
    
    conn.close()
    return actions

def get_active_searches_count():
    """
    Get the count of active searches.
    
    Returns:
        int: Number of active searches
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
    SELECT COUNT(*) FROM actions
    WHERE action_type = 'search_initiated'
    AND date(timestamp) = ?
    ''', (today,))
    
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return count

def get_experts_found_today():
    """
    Get the count of experts found today.
    
    Returns:
        int: Number of experts found today
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
    SELECT SUM(json_extract(details, '$.experts_found')) as count
    FROM actions
    WHERE action_type = 'search_completed'
    AND date(timestamp) = ?
    ''', (today,))
    result = cursor.fetchone()
    experts_found = result['count'] if result['count'] is not None else 0
    
    conn.close()
    
    return experts_found

def get_scheduled_calls_count():
    """
    Get the count of scheduled calls.
    
    Returns:
        int: Number of scheduled calls
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT COUNT(*) FROM actions
    WHERE action_type = 'scheduling_completed'
    ''')
    
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return count

def get_monitor_data():
    """
    Get data for the monitor page.
    
    Returns:
        dict: Dictionary with monitoring data
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Count active searches (searches initiated today)
    cursor.execute('''
    SELECT COUNT(*) as count FROM actions
    WHERE action_type = 'search_initiated'
    AND date(timestamp) = ?
    ''', (today,))
    active_searches = cursor.fetchone()['count']
    
    # Count experts found today
    cursor.execute('''
    SELECT SUM(json_extract(details, '$.experts_found')) as count
    FROM actions
    WHERE action_type = 'search_completed'
    AND date(timestamp) = ?
    ''', (today,))
    result = cursor.fetchone()
    experts_found = result['count'] if result['count'] is not None else 0
    
    # Count scheduled calls
    cursor.execute('''
    SELECT COUNT(*) as count FROM actions
    WHERE action_type = 'scheduling_completed'
    ''')
    scheduled_calls = cursor.fetchone()['count']
    
    # Get recent actions
    cursor.execute('''
    SELECT * FROM actions
    ORDER BY timestamp DESC
    LIMIT 20
    ''')
    
    actions = []
    for row in cursor.fetchall():
        action = dict(row)
        # Parse JSON details
        if action['details']:
            action['details'] = json.loads(action['details'])
        actions.append(action)
    
    conn.close()
    
    return {
        'active_searches': active_searches,
        'experts_found': experts_found,
        'scheduled_calls': scheduled_calls,
        'actions': actions
    }
