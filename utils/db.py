"""
Database Module

This module handles database operations for storing user queries,
expert information, and scheduling details.
"""

import sqlite3
import json
import os
import datetime

# Database file
DB_FILE = os.getenv('DB_FILE', 'julie.db')

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create queries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create experts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS experts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        title TEXT,
        company TEXT,
        location TEXT,
        profile_url TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create selections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS selections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        expert_id TEXT NOT NULL,
        query_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (expert_id) REFERENCES experts (id),
        FOREIGN KEY (query_id) REFERENCES queries (id)
    )
    ''')
    
    # Create schedules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        expert_id TEXT NOT NULL,
        scheduled_time TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (expert_id) REFERENCES experts (id)
    )
    ''')
    
    # Create actions table for monitoring
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_user(email):
    """
    Get a user by email or create if not exists.
    
    Args:
        email (str): User's email address
        
    Returns:
        int: User ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
    else:
        # Create new user
        cursor.execute('INSERT INTO users (email) VALUES (?)', (email,))
        user_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return user_id

def store_query(user_email, query):
    """
    Store a user query in the database.
    
    Args:
        user_email (str): User's email address
        query (str): Search query
        
    Returns:
        int: Query ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get or create user
    user_id = get_or_create_user(user_email)
    
    # Store query
    cursor.execute('INSERT INTO queries (user_id, query) VALUES (?, ?)', 
                  (user_id, query))
    query_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return query_id

def store_expert(expert):
    """
    Store an expert in the database.
    
    Args:
        expert (dict): Expert information
        
    Returns:
        str: Expert ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convert details to JSON
    details = json.dumps(expert)
    
    # Check if expert exists
    cursor.execute('SELECT id FROM experts WHERE id = ?', (expert['id'],))
    existing = cursor.fetchone()
    
    if existing:
        # Update expert
        cursor.execute('''
        UPDATE experts 
        SET name = ?, title = ?, company = ?, location = ?, profile_url = ?, details = ?
        WHERE id = ?
        ''', (
            expert['name'], 
            expert.get('title', ''), 
            expert.get('company', ''), 
            expert.get('location', ''), 
            expert['profile_url'], 
            details,
            expert['id']
        ))
    else:
        # Insert new expert
        cursor.execute('''
        INSERT INTO experts (id, name, title, company, location, profile_url, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            expert['id'], 
            expert['name'], 
            expert.get('title', ''), 
            expert.get('company', ''), 
            expert.get('location', ''), 
            expert['profile_url'], 
            details
        ))
    
    conn.commit()
    conn.close()
    
    return expert['id']

def store_expert_selection(user_email, expert, query=None):
    """
    Store an expert selection in the database.
    
    Args:
        user_email (str): User's email address
        expert (dict): Expert information
        query (str, optional): Search query
        
    Returns:
        int: Selection ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get or create user
    user_id = get_or_create_user(user_email)
    
    # Store expert
    expert_id = store_expert(expert)
    
    # Get or create query
    if query:
        query_id = store_query(user_email, query)
    else:
        # Get the most recent query for this user
        cursor.execute('''
        SELECT id FROM queries 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        query_id = result[0] if result else 0
    
    # Store selection
    cursor.execute('''
    INSERT INTO selections (user_id, expert_id, query_id)
    VALUES (?, ?, ?)
    ''', (user_id, expert_id, query_id))
    selection_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return selection_id

def store_schedule(user_email, expert_id, scheduled_time):
    """
    Store a scheduled call in the database.
    
    Args:
        user_email (str): User's email address
        expert_id (str): Expert ID
        scheduled_time (str): Scheduled time for the call
        
    Returns:
        int: Schedule ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get or create user
    user_id = get_or_create_user(user_email)
    
    # Store schedule
    cursor.execute('''
    INSERT INTO schedules (user_id, expert_id, scheduled_time)
    VALUES (?, ?, ?)
    ''', (user_id, expert_id, scheduled_time))
    schedule_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return schedule_id

def get_expert(expert_id):
    """
    Get expert information from the database.
    
    Args:
        expert_id (str): Expert ID
        
    Returns:
        dict: Expert information
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM experts WHERE id = ?', (expert_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        expert = dict(row)
        # Parse details JSON
        if 'details' in expert and expert['details']:
            expert.update(json.loads(expert['details']))
        return expert
    
    return None

def get_user_experts(user_email):
    """
    Get all experts selected by a user.
    
    Args:
        user_email (str): User's email address
        
    Returns:
        list: List of expert dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute('SELECT id FROM users WHERE email = ?', (user_email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return []
    
    user_id = user['id']
    
    # Get expert IDs selected by the user
    cursor.execute('''
    SELECT DISTINCT expert_id FROM selections
    WHERE user_id = ?
    ''', (user_id,))
    
    expert_ids = [row['expert_id'] for row in cursor.fetchall()]
    
    # Get expert details
    experts = []
    for expert_id in expert_ids:
        cursor.execute('SELECT * FROM experts WHERE id = ?', (expert_id,))
        row = cursor.fetchone()
        if row:
            expert = dict(row)
            # Parse details JSON
            if 'details' in expert and expert['details']:
                expert.update(json.loads(expert['details']))
            experts.append(expert)
    
    conn.close()
    
    return experts
