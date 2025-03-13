"""
LinkedIn Module

This module handles expert search via LinkedIn API or mock data for development.
"""

import os
import json
import random
import time
from datetime import datetime

# Check if we should use mock data
USE_MOCK = os.getenv('USE_MOCK_LINKEDIN', 'True').lower() in ('true', '1', 't')

def search_experts(query):
    """
    Search for experts on LinkedIn based on query.
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of expert dictionaries
    """
    if USE_MOCK:
        return _mock_search_experts(query)
    else:
        return _api_search_experts(query)

def _mock_search_experts(query):
    """
    Generate mock expert data for development.
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of mock expert dictionaries
    """
    # Simulate search delay
    time.sleep(1.5)
    
    # Parse query to determine expert type
    query_lower = query.lower()
    
    # Default expert type
    expert_type = "technology"
    
    # Determine expert type from query
    if any(term in query_lower for term in ["ai", "machine learning", "data science", "artificial intelligence"]):
        expert_type = "ai"
    elif any(term in query_lower for term in ["finance", "investment", "banking", "hedge fund"]):
        expert_type = "finance"
    elif any(term in query_lower for term in ["healthcare", "medical", "doctor", "pharma"]):
        expert_type = "healthcare"
    elif any(term in query_lower for term in ["legal", "law", "attorney", "compliance"]):
        expert_type = "legal"
    
    # Load mock data based on expert type
    mock_experts = _get_mock_experts(expert_type)
    
    # Add unique IDs and timestamps
    for i, expert in enumerate(mock_experts):
        expert['id'] = f"mock-{expert_type}-{i}"
        expert['timestamp'] = datetime.now().isoformat()
    
    return mock_experts

def _get_mock_experts(expert_type):
    """
    Get mock experts based on type.
    
    Args:
        expert_type (str): Type of expert
        
    Returns:
        list: List of mock expert dictionaries
    """
    experts = []
    
    if expert_type == "ai":
        experts = [
            {
                "name": "Sarah Johnson",
                "title": "AI Research Scientist",
                "company": "DeepMind",
                "location": "London, UK",
                "profile_url": "https://linkedin.com/in/mock-sarah-johnson",
                "skills": ["Machine Learning", "Deep Learning", "Neural Networks", "Python", "TensorFlow"]
            },
            {
                "name": "Michael Chen",
                "title": "Director of AI Ethics",
                "company": "Stanford University",
                "location": "Palo Alto, CA",
                "profile_url": "https://linkedin.com/in/mock-michael-chen",
                "skills": ["AI Ethics", "Machine Learning", "Policy", "Research", "Public Speaking"]
            },
            # Add more AI experts
        ]
    elif expert_type == "finance":
        experts = [
            {
                "name": "David Williams",
                "title": "Investment Banking Director",
                "company": "Goldman Sachs",
                "location": "New York, NY",
                "profile_url": "https://linkedin.com/in/mock-david-williams",
                "skills": ["Investment Banking", "M&A", "Financial Analysis", "Valuation", "Deal Structuring"]
            },
            {
                "name": "Jennifer Lee",
                "title": "Hedge Fund Manager",
                "company": "Citadel",
                "location": "Chicago, IL",
                "profile_url": "https://linkedin.com/in/mock-jennifer-lee",
                "skills": ["Portfolio Management", "Risk Analysis", "Derivatives", "Quantitative Finance"]
            },
            # Add more finance experts
        ]
    # Add more expert types as needed
    
    # If no specific experts found, return generic technology experts
    if not experts:
        experts = [
            {
                "name": "Alex Rodriguez",
                "title": "Senior Software Engineer",
                "company": "Google",
                "location": "Mountain View, CA",
                "profile_url": "https://linkedin.com/in/mock-alex-rodriguez",
                "skills": ["Python", "Java", "Cloud Computing", "Distributed Systems"]
            },
            {
                "name": "Emma Wilson",
                "title": "Product Manager",
                "company": "Microsoft",
                "location": "Seattle, WA",
                "profile_url": "https://linkedin.com/in/mock-emma-wilson",
                "skills": ["Product Strategy", "User Experience", "Agile", "Market Research"]
            },
            # Add more generic experts
        ]
    
    # Add 5-10 more random experts to the list
    return experts[:random.randint(5, 10)]

def _api_search_experts(query):
    """
    Search for experts using LinkedIn API.
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of expert dictionaries
    """
    # This would be implemented with actual LinkedIn API
    # For now, return empty list if not in mock mode
    return []
