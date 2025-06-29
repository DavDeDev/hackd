"""
Hackd - Main API Server
Flask API that handles user matching, GitHub analysis, and recruiter interactions.
"""

import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import logging
from typing import Dict, List, Optional

# Import our services
import sys
sys.path.append('../github-analyzer')
sys.path.append('../matching')

from github_analyzer import GitHubAnalyzer
from matcher import MatchingEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for both development and production
if os.environ.get('FLASK_ENV') == 'production':
    # Production: Allow specific origins
    CORS(app, origins=['*'])  # In production, specify your frontend domain
else:
    # Development: Allow all origins
    CORS(app)

# Initialize services
github_analyzer = None
matching_engine = None

try:
    github_analyzer = GitHubAnalyzer()
    matching_engine = MatchingEngine()
    logger.info("✓ Services initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize services: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'github_analyzer': github_analyzer is not None,
            'matching_engine': matching_engine is not None
        }
    })

@app.route('/api/analyze-github', methods=['POST'])
def analyze_github_profile():
    """Analyze a GitHub profile and return tech stack + collaboration data"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
            
        if not github_analyzer:
            return jsonify({'error': 'GitHub analyzer not available'}), 503
            
        profile = github_analyzer.analyze_user_profile(username)
        
        if not profile:
            return jsonify({'error': f'Could not analyze profile for {username}'}), 404
            
        return jsonify({
            'username': profile.username,
            'languages': profile.languages,
            'total_lines': profile.total_lines,
            'complexity_score': profile.avg_complexity,
            'collaboration_score': profile.collaboration_score,
            'top_technologies': profile.top_technologies,
            'repository_count': profile.repository_count,
            'experience_level': 'Beginner' if profile.avg_complexity < 4 else 'Intermediate' if profile.avg_complexity < 7 else 'Advanced'
        })
        
    except Exception as e:
        logger.error(f"Error analyzing GitHub profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/match-users', methods=['POST'])
def match_users():
    """Find matching users based on tech stack and collaboration preferences"""
    try:
        data = request.get_json()
        target_username = data.get('username')
        user_pool = data.get('user_pool', [])  # List of usernames to match against
        
        if not target_username:
            return jsonify({'error': 'Target username is required'}), 400
            
        if not github_analyzer or not matching_engine:
            return jsonify({'error': 'Services not available'}), 503
        
        # Analyze all users in the pool
        profiles = []
        for username in [target_username] + user_pool:
            profile = github_analyzer.analyze_user_profile(username)
            if profile:
                profiles.append(profile)
        
        if len(profiles) < 2:
            return jsonify({'error': 'Not enough valid profiles to generate matches'}), 400
        
        # Generate matches
        matches = github_analyzer.generate_matches(profiles, target_username)
        
        return jsonify({
            'target_user': target_username,
            'matches': matches[:5],  # Return top 5 matches
            'total_analyzed': len(profiles)
        })
        
    except Exception as e:
        logger.error(f"Error matching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze-job-description', methods=['POST'])
def analyze_job_description():
    """Analyze job description and find matching candidates"""
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        candidate_pool = data.get('candidates', [])
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
            
        if not matching_engine:
            return jsonify({'error': 'Matching engine not available'}), 503
        
        # Extract requirements from job description
        requirements = matching_engine.extract_tech_requirements(job_description)
        
        # If candidate pool provided, analyze and rank them
        if candidate_pool:
            rankings = []
            for username in candidate_pool:
                if github_analyzer:
                    profile = github_analyzer.analyze_user_profile(username)
                    if profile:
                        score = matching_engine.calculate_job_match_score(profile, requirements)
                        rankings.append({
                            'username': username,
                            'match_score': score,
                            'tech_overlap': list(set(profile.top_technologies) & set(requirements.get('technologies', []))),
                            'experience_level': profile.avg_complexity
                        })
            
            rankings.sort(key=lambda x: x['match_score'], reverse=True)
            
            return jsonify({
                'job_requirements': requirements,
                'candidate_rankings': rankings[:10],
                'total_candidates': len(candidate_pool)
            })
        
        return jsonify({
            'job_requirements': requirements,
            'message': 'Provide candidate pool for ranking'
        })
        
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/get-matching-data', methods=['GET'])
def get_matching_data():
    """Get sample matching data for demo purposes"""
    try:
        # This endpoint provides sample data for the frontend
        # In production, this would fetch from your database
        sample_data = [
            {
                'Username': 'sample_user_1',
                'Skills': {'Python': 45, 'JavaScript': 30, 'React': 25},
                'SkillSummary': 'Full-stack developer with Python and React expertise',
                'Commitment': 0.8,
                'TeamDynamics': 0.9,
                'WorkStyle': 0.7,
                'SkillsExperience': 0.75,
                'MotivationGoals': 0.85,
                'avatar': 'https://github.com/sample_user_1.png'
            },
            {
                'Username': 'sample_user_2',
                'Skills': {'Java': 50, 'Spring': 30, 'AWS': 20},
                'SkillSummary': 'Backend developer specializing in enterprise Java applications',
                'Commitment': 0.75,
                'TeamDynamics': 0.8,
                'WorkStyle': 0.9,
                'SkillsExperience': 0.8,
                'MotivationGoals': 0.7,
                'avatar': 'https://github.com/sample_user_2.png'
            }
        ]
        
        return jsonify(sample_data)
        
    except Exception as e:
        logger.error(f"Error getting matching data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of text (used for job descriptions and user profiles)"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        if not matching_engine:
            return jsonify({'error': 'Matching engine not available'}), 503
        
        sentiment_result = matching_engine.analyze_sentiment(text)
        
        return jsonify({
            'text': text[:100] + '...' if len(text) > 100 else text,
            'sentiment': sentiment_result.get('sentiment', 'neutral'),
            'confidence': sentiment_result.get('confidence', 0.5),
            'summary': sentiment_result.get('summary', 'Text analyzed successfully')
        })
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run in debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Hackd API server on port {port}")
    logger.info(f"🔧 Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 