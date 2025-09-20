"""
Hackd Matching Engine - Pure execution with comprehensive logging
"""

import os
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter

import cohere

# Import comprehensive logging system
import sys
sys.path.append('..')
from logging_config import get_business_logger, get_logger

@dataclass
class JobRequirements:
    technologies: List[str]
    experience_level: str
    team_size: str
    work_style: str
    key_responsibilities: List[str]
    nice_to_have: List[str]

@dataclass
class SentimentResult:
    sentiment: str
    confidence: float
    summary: str
    key_themes: List[str]

class MatchingEngine:
    """AI-powered matching engine with comprehensive logging"""
    
    def __init__(self):
        self.logger = get_business_logger("matching")
        
        self.logger.log_function_entry("__init__")
        start_time = time.time()
        
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        self.logger.debug("Initializing Cohere client", extra_data={
            'cohere_api_key_configured': bool(self.cohere_api_key)
        })
        
        self.cohere_client = cohere.Client(self.cohere_api_key)
        
        self.tech_keywords = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'Flask',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch',
            'Machine Learning', 'AI', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'HTML', 'CSS', 'SASS', 'GraphQL', 'REST API', 'Microservices'
        ]
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("__init__", result="MatchingEngine instance", execution_time=execution_time)
        self.logger.info("Matching engine initialized successfully", extra_data={
            'tech_keywords_count': len(self.tech_keywords)
        })
    
    def extract_tech_requirements(self, job_description: str) -> JobRequirements:
        """Extract technical requirements from job description with comprehensive logging"""
        self.logger.log_function_entry("extract_tech_requirements", args={
            'job_description_length': len(job_description)
        })
        start_time = time.time()
        
        self.logger.debug("Processing job description", extra_data={
            'description_preview': job_description[:200] + '...' if len(job_description) > 200 else job_description,
            'description_length': len(job_description)
        })
        
        prompt = f"""Analyze this job description and extract key information:

Job Description:
{job_description}

Please provide the following information in a structured format:

TECHNOLOGIES: List specific technologies, programming languages, frameworks, and tools mentioned
EXPERIENCE_LEVEL: Junior/Mid-level/Senior/Lead based on requirements  
TEAM_SIZE: Solo/Small Team (2-4)/Medium Team (5-10)/Large Team (10+)
WORK_STYLE: Remote/Hybrid/On-site/Flexible
KEY_RESPONSIBILITIES: Main duties and responsibilities
NICE_TO_HAVE: Optional skills or qualifications

Format your response exactly as shown above with clear sections."""

        self.logger.log_ai_request("cohere", prompt, model="command", tokens=300)
        
        response = self.cohere_client.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.2
        )
        
        response_text = response.generations[0].text
        self.logger.log_ai_response("cohere", len(response_text))
        
        self.logger.debug("Raw AI response received", extra_data={
            'response_length': len(response_text),
            'response_preview': response_text[:300] + '...' if len(response_text) > 300 else response_text
        })
        
        result = self._parse_job_requirements(response_text)
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("extract_tech_requirements", result=result, execution_time=execution_time)
        
        self.logger.info("Job requirements extracted", extra_data={
            'technologies_found': len(result.technologies),
            'experience_level': result.experience_level,
            'team_size': result.team_size,
            'work_style': result.work_style,
            'execution_time': execution_time
        })
        
        return result
    
    def _parse_job_requirements(self, ai_response: str) -> JobRequirements:
        """Parse AI response to extract structured job requirements"""
        matcher_logger.debug("Parsing AI response for job requirements")
        
        technologies = self._extract_section(ai_response, 'TECHNOLOGIES')
        experience_level = self._extract_section(ai_response, 'EXPERIENCE_LEVEL')
        team_size = self._extract_section(ai_response, 'TEAM_SIZE')
        work_style = self._extract_section(ai_response, 'WORK_STYLE')
        responsibilities = self._extract_section(ai_response, 'KEY_RESPONSIBILITIES')
        nice_to_have = self._extract_section(ai_response, 'NICE_TO_HAVE')
        
        tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
        resp_list = [resp.strip() for resp in responsibilities.split(',') if resp.strip()]
        nth_list = [nth.strip() for nth in nice_to_have.split(',') if nth.strip()]
        
        result = JobRequirements(
            technologies=tech_list,
            experience_level=experience_level.strip(),
            team_size=team_size.strip(),
            work_style=work_style.strip(),
            key_responsibilities=resp_list,
            nice_to_have=nth_list
        )
        
        matcher_logger.info(f"Parsed requirements: {len(tech_list)} technologies, {experience_level} level")
        return result
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section from AI response"""
        pattern = rf'{section_name}:\s*([^\n]+(?:\n(?![\w\s]+:)[^\n]+)*)'
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def calculate_job_match_score(self, profile, job_requirements: JobRequirements) -> Tuple[float, Dict[str, float]]:
        """Calculate job match score using hybrid scoring system with comprehensive logging"""
        self.logger.log_function_entry("calculate_job_match_score", args={
            'username': profile.username,
            'required_technologies': job_requirements.technologies,
            'experience_level': job_requirements.experience_level
        })
        start_time = time.time()
        
        scores = {}
        detailed_breakdown = {}
        
        # 1. Hard Skills Matching (40%) - Exact technology matches
        self.logger.debug("Calculating technology match score", extra_data={
            'profile_technologies': profile.top_technologies,
            'required_technologies': job_requirements.technologies
        })
        tech_score = self._calculate_tech_match(profile, job_requirements)
        scores['technology'] = tech_score * 0.40
        detailed_breakdown['tech_raw_score'] = tech_score
        detailed_breakdown['tech_weighted_score'] = scores['technology']
        
        # 2. Experience Level Compatibility (25%)
        self.logger.debug("Calculating experience match score", extra_data={
            'profile_complexity': profile.avg_complexity,
            'required_experience': job_requirements.experience_level
        })
        exp_score = self._calculate_experience_match(profile, job_requirements)
        scores['experience'] = exp_score * 0.25
        detailed_breakdown['exp_raw_score'] = exp_score
        detailed_breakdown['exp_weighted_score'] = scores['experience']
        
        # 3. Collaboration Patterns (20%)
        self.logger.debug("Calculating collaboration match score", extra_data={
            'profile_collaboration_score': profile.collaboration_score,
            'required_team_size': job_requirements.team_size
        })
        collab_score = self._calculate_collaboration_match(profile, job_requirements)
        scores['collaboration'] = collab_score * 0.20
        detailed_breakdown['collab_raw_score'] = collab_score
        detailed_breakdown['collab_weighted_score'] = scores['collaboration']
        
        # 4. Activity & Engagement (15%)
        self.logger.debug("Calculating activity match score", extra_data={
            'repository_count': profile.repository_count,
            'total_lines': profile.total_lines
        })
        activity_score = self._calculate_activity_match(profile)
        scores['activity'] = activity_score * 0.15
        detailed_breakdown['activity_raw_score'] = activity_score
        detailed_breakdown['activity_weighted_score'] = scores['activity']
        
        total_score = sum(scores.values())
        confidence = self._calculate_confidence(profile, job_requirements)
        
        execution_time = time.time() - start_time
        
        # Log comprehensive match calculation
        self.logger.log_matching_calculation(
            f"JOB_MATCH_{job_requirements.experience_level}",
            profile.username,
            min(total_score, 1.0),
            {
                'technology_score': scores['technology'],
                'experience_score': scores['experience'], 
                'collaboration_score': scores['collaboration'],
                'activity_score': scores['activity'],
                'confidence': confidence
            }
        )
        
        self.logger.debug("Match calculation detailed breakdown", extra_data={
            'username': profile.username,
            'detailed_scores': detailed_breakdown,
            'final_score': min(total_score, 1.0),
            'confidence': confidence,
            'execution_time': execution_time
        })
        
        self.logger.log_function_exit("calculate_job_match_score", 
                                    result=min(total_score, 1.0), 
                                    execution_time=execution_time)
        
        return min(total_score, 1.0), {
            'scores': scores,
            'confidence': confidence,
            'execution_time': execution_time,
            'detailed_breakdown': detailed_breakdown
        }
    
    def _calculate_tech_match(self, profile, job_requirements: JobRequirements) -> float:
        """Calculate technology matching score"""
        profile_techs = set(tech.lower() for tech in profile.top_technologies)
        required_techs = set(tech.lower() for tech in job_requirements.technologies)
        
        exact_matches = profile_techs & required_techs
        exact_score = len(exact_matches) / len(required_techs) if required_techs else 0
        
        # Related technology matches
        partial_matches = self._find_related_technologies(profile_techs, required_techs)
        partial_score = len(partial_matches) * 0.5 / len(required_techs) if required_techs else 0
        
        tech_score = min(exact_score + partial_score, 1.0)
        
        matcher_logger.debug(f"Tech match: exact={exact_score:.3f}, partial={partial_score:.3f}, total={tech_score:.3f}")
        return tech_score
    
    def _find_related_technologies(self, profile_techs: set, required_techs: set) -> List[str]:
        """Find related technologies that complement required ones"""
        relations = {
            'react': ['javascript', 'typescript', 'node.js'],
            'angular': ['javascript', 'typescript'],
            'vue': ['javascript'],
            'django': ['python'],
            'flask': ['python'],
            'spring': ['java'],
            'express': ['javascript', 'node.js'],
            'rails': ['ruby'],
            'laravel': ['php'],
            'aws': ['docker', 'kubernetes', 'terraform'],
            'azure': ['docker', 'kubernetes'],
            'gcp': ['docker', 'kubernetes'],
        }
        
        partial_matches = []
        for required in required_techs:
            if required not in profile_techs:
                related = relations.get(required.lower(), [])
                for tech in profile_techs:
                    if tech in [r.lower() for r in related]:
                        partial_matches.append(f"{tech} (related to {required})")
                        break
        
        return partial_matches
    
    def _calculate_experience_match(self, profile, job_requirements: JobRequirements) -> float:
        """Calculate experience level compatibility"""
        experience_mapping = {
            'junior': (0, 4),
            'mid-level': (4, 7), 
            'senior': (7, 10),
            'lead': (8, 10)
        }
        
        required_level = job_requirements.experience_level.lower()
        profile_complexity = profile.avg_complexity
        
        min_exp, max_exp = experience_mapping.get(required_level, (0, 10))
        
        if min_exp <= profile_complexity <= max_exp:
            exp_score = 1.0
        elif abs(profile_complexity - min_exp) <= 1 or abs(profile_complexity - max_exp) <= 1:
            exp_score = 0.7
        else:
            exp_score = 0.4
        
        matcher_logger.debug(f"Experience match: required={required_level}, profile={profile_complexity}, score={exp_score}")
        return exp_score
    
    def _calculate_collaboration_match(self, profile, job_requirements: JobRequirements) -> float:
        """Calculate collaboration compatibility"""
        collab_normalized = min(profile.collaboration_score / 10.0, 1.0)
        
        team_size_modifier = 1.0
        team_size_lower = job_requirements.team_size.lower()
        if 'solo' in team_size_lower and profile.collaboration_score < 5:
            team_size_modifier = 1.2
        elif 'large' in team_size_lower and profile.collaboration_score > 7:
            team_size_modifier = 1.2
        
        collab_score = min(collab_normalized * team_size_modifier, 1.0)
        
        matcher_logger.debug(f"Collaboration match: raw={profile.collaboration_score}, normalized={collab_normalized}, final={collab_score}")
        return collab_score
    
    def _calculate_activity_match(self, profile) -> float:
        """Calculate activity and engagement score"""
        repo_score = min(profile.repository_count / 20, 1.0)
        lines_score = min(profile.total_lines / 50000, 1.0)
        activity_score = (repo_score * 0.6 + lines_score * 0.4)
        
        matcher_logger.debug(f"Activity match: repos={profile.repository_count}, lines={profile.total_lines}, score={activity_score}")
        return activity_score
    
    def _calculate_confidence(self, profile, job_requirements: JobRequirements) -> float:
        """Calculate confidence in matching result based on data quality"""
        confidence_factors = []
        
        if profile.repository_count >= 5:
            confidence_factors.append(0.3)
        if profile.total_lines >= 10000:
            confidence_factors.append(0.2)  
        if len(profile.top_technologies) >= 3:
            confidence_factors.append(0.2)
        if len(job_requirements.technologies) >= 2:
            confidence_factors.append(0.15)
        if job_requirements.experience_level.lower() in ['junior', 'mid-level', 'senior']:
            confidence_factors.append(0.15)
            
        return sum(confidence_factors)
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment and extract key themes from text with comprehensive logging"""
        self.logger.log_function_entry("analyze_sentiment", args={
            'text_length': len(text)
        })
        start_time = time.time()
        
        self.logger.debug("Processing sentiment analysis", extra_data={
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'text_length': len(text)
        })
        
        prompt = f"""Analyze the sentiment and key themes of this text:

Text: {text}

Provide:
1. SENTIMENT: positive/negative/neutral
2. CONFIDENCE: 0.0 to 1.0
3. SUMMARY: Brief summary of the text
4. KEY_THEMES: Main themes or topics (comma-separated)

Format your response with clear sections as shown above."""

        self.logger.log_ai_request("cohere", prompt, model="command", tokens=150)

        response = self.cohere_client.generate(
            model='command',
            prompt=prompt,
            max_tokens=150,
            temperature=0.2
        )
        
        response_text = response.generations[0].text
        self.logger.log_ai_response("cohere", len(response_text))
        
        self.logger.debug("Sentiment analysis AI response", extra_data={
            'response_length': len(response_text),
            'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text
        })
        
        result = self._parse_sentiment_response(response_text)
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("analyze_sentiment", result=result, execution_time=execution_time)
        
        self.logger.info("Sentiment analysis completed", extra_data={
            'sentiment': result.sentiment,
            'confidence': result.confidence,
            'themes_count': len(result.key_themes),
            'execution_time': execution_time
        })
        
        return result
    
    def _parse_sentiment_response(self, ai_response: str) -> SentimentResult:
        """Parse sentiment analysis response"""
        sentiment = self._extract_section(ai_response, 'SENTIMENT').lower()
        confidence_str = self._extract_section(ai_response, 'CONFIDENCE')
        summary = self._extract_section(ai_response, 'SUMMARY')
        themes_str = self._extract_section(ai_response, 'KEY_THEMES')
        
        try:
            confidence = float(confidence_str)
        except (ValueError, TypeError):
            confidence = 0.5
        
        themes = [theme.strip() for theme in themes_str.split(',') if theme.strip()]
        
        result = SentimentResult(
            sentiment=sentiment if sentiment in ['positive', 'negative', 'neutral'] else 'neutral',
            confidence=max(0.0, min(1.0, confidence)),
            summary=summary if summary else "No summary available",
            key_themes=themes
        )
        
        self.logger.info(f"Sentiment analysis completed: {sentiment} ({confidence:.2f} confidence)")
        return result
    
    def generate_team_recommendations(self, profiles: List, team_size: int = 3) -> List[Dict]:
        """Generate optimal team combinations based on complementary skills"""
        matcher_logger.debug(f"Generating team recommendations for {len(profiles)} profiles, team size {team_size}")
        
        sorted_profiles = sorted(profiles, key=lambda p: p.avg_complexity, reverse=True)
        
        teams = []
        remaining_profiles = sorted_profiles.copy()
        
        while len(remaining_profiles) >= team_size:
            team = [remaining_profiles.pop(0)]  # Team lead
            
            for _ in range(team_size - 1):
                if not remaining_profiles:
                    break
                
                best_match = None
                best_score = -1
                
                for candidate in remaining_profiles:
                    tech_diversity = len(set(team[0].top_technologies) - set(candidate.top_technologies))
                    collab_compatibility = abs(team[0].collaboration_score - candidate.collaboration_score)
                    
                    score = tech_diversity * 0.6 - collab_compatibility * 0.4
                    
                    if score > best_score:
                        best_score = score
                        best_match = candidate
                
                if best_match:
                    team.append(best_match)
                    remaining_profiles.remove(best_match)
            
            if len(team) == team_size:
                teams.append({
                    'team_members': [p.username for p in team],
                    'team_lead': team[0].username,
                    'combined_technologies': list(set(sum([p.top_technologies for p in team], []))),
                    'avg_collaboration_score': sum(p.collaboration_score for p in team) / len(team),
                    'team_diversity_score': len(set(sum([p.top_technologies for p in team], [])))
                })
        
        matcher_logger.info(f"Generated {len(teams)} team recommendations")
        return teams

def main():
    """Test the matching engine"""
    os.makedirs('logs', exist_ok=True)
    
    matcher = MatchingEngine()
    
    sample_job = """
    We are looking for a Senior Full Stack Developer to join our team.
    Requirements:
    - 5+ years of experience with Python and JavaScript
    - Experience with React and Django
    - AWS cloud experience
    - Strong collaboration skills
    """
    
    requirements = matcher.extract_tech_requirements(sample_job)
    print(f"Technologies: {requirements.technologies}")
    print(f"Experience Level: {requirements.experience_level}")
    
    sentiment = matcher.analyze_sentiment("I love working with innovative teams on challenging projects!")
    print(f"Sentiment Analysis: {sentiment.sentiment} (confidence: {sentiment.confidence})")

if __name__ == '__main__':
    main()