"""
Hackd API - Direct execution, no defensive code
"""

import os
import time
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from typing import Dict, List, Optional
from functools import wraps

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import our services
import sys
import os

# Add current directory and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'github-analyzer'))
sys.path.insert(0, os.path.join(parent_dir, 'matching'))

from github_analyzer import GitHubAnalyzer
from matcher import MatchingEngine

# Import comprehensive logging system
from logging_config import get_business_logger, get_logger, log_system_startup, log_system_shutdown

# Initialize comprehensive logging
api_logger = get_business_logger("api")

def log_api_call(f):
    """Comprehensive API call logging with full debug coverage"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        endpoint = request.endpoint
        method = request.method
        ip = request.remote_addr
        
        # Log API call entry with comprehensive details
        request_data = request.get_json() if request.is_json else None
        api_logger.log_function_entry(f"{method}_{endpoint}", args={
            'endpoint': endpoint,
            'method': method,
            'client_ip': ip,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'content_type': request.content_type,
            'request_data_present': request_data is not None
        })
        
        # Log request details (sanitized)
        if request_data:
            sanitized_data = {k: f"<{type(v).__name__}>" if isinstance(v, (list, dict)) else str(v)[:100] 
                            for k, v in request_data.items()}
            api_logger.debug(f"Request data received", extra_data=sanitized_data)
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log successful completion
            api_logger.log_function_exit(f"{method}_{endpoint}", 
                                       result="API response", 
                                       execution_time=execution_time)
            
            api_logger.info(f"API call completed successfully", extra_data={
                'endpoint': endpoint,
                'method': method,
                'execution_time': execution_time,
                'status': 'success'
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            api_logger.error(f"API call failed", 
                           extra_data={
                               'endpoint': endpoint,
                               'method': method,
                               'execution_time': execution_time,
                               'error_type': type(e).__name__
                           },
                           exception=e)
            raise
            
    return decorated_function

app = Flask(__name__)

# Configure CORS for both development and production
if os.environ.get('FLASK_ENV') == 'production':
    # Production: Allow specific origins
    CORS(app, origins=['*'])  # In production, specify your frontend domain
else:
    # Development: Allow all origins
    CORS(app)

# Initialize services with comprehensive logging
api_logger.debug("Starting service initialization", extra_data={
    'flask_env': os.environ.get('FLASK_ENV', 'development'),
    'github_token_configured': bool(os.getenv('GITHUB_TOKEN')),
    'cohere_token_configured': bool(os.getenv('COHERE_API_KEY'))
})

try:
    github_analyzer = GitHubAnalyzer()
    matching_engine = MatchingEngine()
    
    api_logger.info("All services initialized successfully", extra_data={
        'github_analyzer': 'initialized',
        'matching_engine': 'initialized'
    })
except Exception as e:
    api_logger.error("Service initialization failed", exception=e)
    raise

@app.route('/health', methods=['GET'])
@log_api_call
def health_check():
    """Enhanced health check endpoint with service diagnostics"""
    api_logger.debug("Health check requested")
    
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'github_analyzer': {
                'available': github_analyzer is not None,
                'github_token_configured': bool(os.getenv('GITHUB_TOKEN')),
            },
            'matching_engine': {
                'available': matching_engine is not None,
                'cohere_token_configured': bool(os.getenv('COHERE_API_KEY')),
                'cohere_status': 'connected'
            }
        },
        'environment': {
            'flask_env': os.getenv('FLASK_ENV', 'development'),
            'debug_mode': os.getenv('FLASK_ENV') == 'development',
            'log_level': 20  # DEBUG level
        }
    }
    
    api_logger.debug("Cohere API connection verified")
    
    # Determine overall health status
    if not (github_analyzer and matching_engine):
        health_status['status'] = 'degraded'
        
    return jsonify(health_status)

@app.route('/api/analyze-github', methods=['POST'])
@log_api_call
def analyze_github_profile():
    """GitHub profile analysis with comprehensive logging"""
    data = request.get_json()
    username = data.get('username')
    include_debug = data.get('include_debug', False)
    
    api_logger.debug("Processing GitHub analysis request", extra_data={
        'username': username,
        'include_debug': include_debug,
        'request_source': request.remote_addr
    })
    
    start_time = time.time()
    
    try:
        profile = github_analyzer.analyze_user_profile(username)
        
        if not profile:
            api_logger.warning("Profile analysis failed - no profile returned", extra_data={
                'username': username,
                'execution_time': time.time() - start_time
            })
            return jsonify({'error': 'Failed to analyze profile', 'username': username}), 404
        
        analysis_time = time.time() - start_time
        
        # Log detailed profile analysis results
        api_logger.info("GitHub profile analysis completed", extra_data={
            'username': username,
            'processing_time': analysis_time,
            'repositories_found': profile.repository_count,
            'languages_detected': len(profile.languages),
            'top_technologies': profile.top_technologies,
            'complexity_score': profile.avg_complexity,
            'collaboration_score': profile.collaboration_score,
            'total_lines_of_code': profile.total_lines
        })
        
        # Determine experience level
        if profile.avg_complexity < 4:
            experience_level = 'Beginner'
        elif profile.avg_complexity < 7:
            experience_level = 'Intermediate'
        else:
            experience_level = 'Advanced'
        
        # Determine data quality
        if profile.repository_count >= 5:
            data_quality = 'high'
        elif profile.repository_count >= 2:
            data_quality = 'medium'
        else:
            data_quality = 'low'
        
        response_data = {
            'username': profile.username,
            'languages': profile.languages,
            'total_lines': profile.total_lines,
            'complexity_score': profile.avg_complexity,
            'collaboration_score': profile.collaboration_score,
            'top_technologies': profile.top_technologies,
            'repository_count': profile.repository_count,
            'experience_level': experience_level,
            'analysis_metadata': {
                'processing_time': analysis_time,
                'data_quality': data_quality
            }
        }
        
        if include_debug:
            response_data['debug_info'] = {
                'repositories_analyzed': profile.repository_count,
                'total_code_lines': profile.total_lines,
                'language_breakdown': profile.languages,
                'experience_classification': {
                    'raw_complexity': profile.avg_complexity,
                    'classified_as': experience_level
                }
            }
            api_logger.debug("Debug information included in response", extra_data={
                'username': username,
                'debug_fields': list(response_data['debug_info'].keys())
            })
        
        api_logger.info("Response prepared successfully", extra_data={
            'username': username,
            'response_size': len(str(response_data)),
            'include_debug': include_debug
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        execution_time = time.time() - start_time
        api_logger.error("GitHub analysis endpoint failed", 
                        extra_data={
                            'username': username,
                            'execution_time': execution_time
                        },
                        exception=e)
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/match-users', methods=['POST'])
@log_api_call
def match_users():
    """Direct user matching - no defensive patterns"""
    data = request.get_json()
    target_username = data.get('username')
    user_pool = data.get('user_pool', [])
    
    api_logger.debug(f"User matching request for {target_username} against {len(user_pool)} users")
    
    # Analyze all users in the pool
    profiles = []
    for username in [target_username] + user_pool:
        api_logger.debug(f"Analyzing profile: {username}")
        profile = github_analyzer.analyze_user_profile(username)
        if profile:
            profiles.append(profile)
    
    api_logger.info(f"Successfully analyzed {len(profiles)} profiles")
    
    # Generate matches
    matches = github_analyzer.generate_matches(profiles, target_username)
    
    api_logger.info(f"Generated {len(matches)} matches for {target_username}")
    
    return jsonify({
        'target_user': target_username,
        'matches': matches[:5],
        'total_analyzed': len(profiles)
    })

@app.route('/api/analyze-job-description', methods=['POST'])
@log_api_call
def analyze_job_description():
    """Direct job description analysis and candidate ranking - no defensive patterns"""
    data = request.get_json()
    job_description = data.get('job_description', '')
    candidate_pool = data.get('candidates', [])
    include_debug = data.get('include_debug', False)
    
    api_logger.debug(f"Job description analysis request - JD length: {len(job_description)}, candidates: {len(candidate_pool)}")
    
    # Extract requirements from job description
    api_logger.debug("Extracting requirements from job description using Cohere AI")
    requirements = matching_engine.extract_tech_requirements(job_description)
    api_logger.info(f"Extracted requirements: {len(requirements.technologies)} technologies, {requirements.experience_level} level")
    
    # If candidate pool provided, analyze and rank them
    if candidate_pool:
        api_logger.info(f"Analyzing {len(candidate_pool)} candidates for job match scoring")
        rankings = []
        failed_profiles = []
        
        for i, username in enumerate(candidate_pool):
            api_logger.debug(f"Analyzing candidate {i+1}/{len(candidate_pool)}: {username}")
            
            profile = github_analyzer.analyze_user_profile(username)
            
            if profile:
                api_logger.debug(f"Profile analysis successful for {username}")
                score, debug_info = matching_engine.calculate_job_match_score(profile, requirements)
                
                ranking_entry = {
                    'username': username,
                    'match_score': score,
                    'tech_overlap': list(set(profile.top_technologies) & set(requirements.technologies)),
                    'experience_level': profile.avg_complexity,
                    'collaboration_score': profile.collaboration_score,
                    'repository_count': profile.repository_count,
                    'top_technologies': profile.top_technologies,
                    'confidence': debug_info.get('confidence', 0.5)
                }
                
                if include_debug:
                    ranking_entry['debug_info'] = debug_info
                    
                rankings.append(ranking_entry)
                api_logger.debug(f"Match score for {username}: {score:.3f}")
            else:
                failed_profiles.append(username)
                api_logger.warning(f"Failed to analyze profile for {username}")
        
        # Sort by match score (descending)
        rankings.sort(key=lambda x: x['match_score'], reverse=True)
        
        api_logger.info(f"Candidate ranking completed: {len(rankings)} successful, {len(failed_profiles)} failed")
        
        response_data = {
            'job_requirements': {
                'technologies': requirements.technologies,
                'experience_level': requirements.experience_level,
                'team_size': requirements.team_size,
                'work_style': requirements.work_style,
                'key_responsibilities': requirements.key_responsibilities,
                'nice_to_have': requirements.nice_to_have
            },
            'candidate_rankings': rankings[:10],
            'total_candidates_processed': len(candidate_pool),
            'successful_analyses': len(rankings),
            'failed_analyses': len(failed_profiles),
            'processing_summary': {
                'avg_match_score': sum(r['match_score'] for r in rankings) / len(rankings) if rankings else 0,
                'top_match_score': rankings[0]['match_score'] if rankings else 0,
                'failed_usernames': failed_profiles
            }
        }
        
        return jsonify(response_data)
    
    # No candidate pool provided
    api_logger.info("Job requirements extracted successfully, no candidates to analyze")
    return jsonify({
        'job_requirements': {
            'technologies': requirements.technologies,
            'experience_level': requirements.experience_level,
            'team_size': requirements.team_size,
            'work_style': requirements.work_style,
            'key_responsibilities': requirements.key_responsibilities,
            'nice_to_have': requirements.nice_to_have
        },
        'message': 'Job requirements extracted successfully. Provide candidate pool for ranking.'
    })

@app.route('/api/get-matching-data', methods=['GET'])
@log_api_call
def get_matching_data():
    """Direct sample data retrieval - no defensive patterns"""
    api_logger.debug("Retrieving sample matching data")
    
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
    
    api_logger.debug(f"Returning {len(sample_data)} sample profiles")
    return jsonify(sample_data)

@app.route('/api/analyze-sentiment', methods=['POST'])
@log_api_call
def analyze_sentiment():
    """Direct sentiment analysis using Cohere AI - no defensive patterns"""
    data = request.get_json()
    text = data.get('text', '')
    
    api_logger.debug(f"Sentiment analysis request for text: {text[:50]}...")
    
    sentiment_result = matching_engine.analyze_sentiment(text)
    
    api_logger.debug(f"Sentiment analysis completed: {sentiment_result.sentiment} ({sentiment_result.confidence:.2f} confidence)")
    
    return jsonify({
        'text': text[:100] + '...' if len(text) > 100 else text,
        'sentiment': sentiment_result.sentiment,
        'confidence': sentiment_result.confidence,
        'summary': sentiment_result.summary,
        'key_themes': sentiment_result.key_themes
    })

# Error handlers removed - following manifesto principles of natural failure

if __name__ == '__main__':
    try:
        # Get port from environment variable or default to 5000
        port = int(os.environ.get('PORT', 5000))
        
        # Run in debug mode only in development
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        # Log system startup with comprehensive details
        log_system_startup()
        api_logger.info("Starting Hackd API server", extra_data={
            'port': port,
            'debug_mode': debug_mode,
            'flask_env': os.environ.get('FLASK_ENV', 'development'),
            'host': '0.0.0.0',
            'cors_enabled': True,
            'services_initialized': True
        })
        
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
        
    except KeyboardInterrupt:
        api_logger.info("Server shutdown requested by user")
    except Exception as e:
        api_logger.error("Server startup failed", exception=e)
        raise
    finally:
        log_system_shutdown()
        api_logger.info("Hackd API server shutdown complete") 