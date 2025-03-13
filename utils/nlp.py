"""
Natural Language Processing Module

This module handles expert ranking and filtering based on NLP techniques.
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """
    Preprocess text for NLP analysis.
    
    Args:
        text (str): Text to preprocess
        
    Returns:
        list: List of preprocessed tokens
    """
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens

def calculate_relevance_score(expert, query_tokens):
    """
    Calculate relevance score for an expert based on query tokens.
    
    Args:
        expert (dict): Expert information
        query_tokens (list): Preprocessed query tokens
        
    Returns:
        float: Relevance score (0-1)
    """
    # Combine relevant expert fields
    expert_text = ' '.join(filter(None, [
        expert.get('name', ''),
        expert.get('title', ''),
        expert.get('company', ''),
        expert.get('summary', ''),
        ' '.join(expert.get('skills', [])),
        ' '.join([edu.get('field', '') for edu in expert.get('education', [])])
    ]))
    
    # Preprocess expert text
    expert_tokens = preprocess_text(expert_text)
    
    if not expert_tokens or not query_tokens:
        return 0.0
    
    # Count matching tokens
    matches = sum(1 for token in query_tokens if token in expert_tokens)
    
    # Calculate score
    score = matches / len(query_tokens) if query_tokens else 0.0
    
    # Boost score for exact title matches
    if any(token in expert.get('title', '').lower() for token in query_tokens):
        score *= 1.5
    
    # Cap at 1.0
    return min(score, 1.0)

def rank_experts(experts, query):
    """
    Rank experts based on relevance to the query.
    
    Args:
        experts (list): List of expert dictionaries
        query (str): Search query
        
    Returns:
        list: Ranked list of expert dictionaries
    """
    # Preprocess query
    query_tokens = preprocess_text(query)
    
    # Calculate relevance scores
    for expert in experts:
        expert['relevance_score'] = calculate_relevance_score(expert, query_tokens)
    
    # Sort by relevance score (descending)
    ranked_experts = sorted(experts, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return ranked_experts

def extract_keywords(query, max_keywords=5):
    """
    Extract important keywords from a query.
    
    Args:
        query (str): Search query
        max_keywords (int): Maximum number of keywords to extract
        
    Returns:
        list: List of keywords
    """
    # Preprocess query
    tokens = preprocess_text(query)
    
    # Remove very short tokens
    tokens = [token for token in tokens if len(token) > 2]
    
    # Return top keywords
    return tokens[:max_keywords]

def analyze_expertise_match(expert, query):
    """
    Analyze how well an expert's expertise matches the query.
    
    Args:
        expert (dict): Expert information
        query (str): Search query
        
    Returns:
        dict: Analysis results
    """
    query_tokens = preprocess_text(query)
    
    # Extract skills
    skills = expert.get('skills', [])
    
    # Extract education fields
    education_fields = [edu.get('field', '') for edu in expert.get('education', [])]
    
    # Calculate matches
    skill_matches = [skill for skill in skills if any(token in skill.lower() for token in query_tokens)]
    education_matches = [field for field in education_fields if any(token in field.lower() for token in query_tokens)]
    
    return {
        'skill_matches': skill_matches,
        'education_matches': education_matches,
        'match_score': len(skill_matches) + len(education_matches)
    }
