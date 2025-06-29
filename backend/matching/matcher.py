"""
Hackd - AI Matching Engine
Uses Cohere AI for sentiment analysis, job requirement extraction, and candidate matching.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import cohere

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobRequirements:
    """Data class for job requirements extracted from job descriptions"""
    technologies: List[str]
    experience_level: str
    team_size: str
    work_style: str
    key_responsibilities: List[str]
    nice_to_have: List[str]

@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    sentiment: str
    confidence: float
    summary: str
    key_themes: List[str]

class MatchingEngine:
    """AI-powered matching engine for pairing candidates with jobs and teammates"""
    
    def __init__(self):
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")
            
        self.cohere_client = cohere.Client(self.cohere_api_key)
        
        # Technology keywords for job parsing
        self.tech_keywords = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'Flask',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch',
            'Machine Learning', 'AI', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'HTML', 'CSS', 'SASS', 'GraphQL', 'REST API', 'Microservices'
        ]
        
    def extract_tech_requirements(self, job_description: str) -> JobRequirements:
        """Extract technical requirements from a job description using Cohere AI"""
        try:
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

            response = self.cohere_client.generate(
                model='command',
                prompt=prompt,
                max_tokens=300,
                temperature=0.2
            )
            
            return self._parse_job_requirements(response.generations[0].text, job_description)
            
        except Exception as e:
            logger.warning(f"Job description analysis failed: {e}")
            return self._fallback_job_parsing(job_description)
    
    def _parse_job_requirements(self, ai_response: str, original_text: str) -> JobRequirements:
        """Parse the AI response to extract structured job requirements"""
        try:
            # Extract sections using regex
            technologies = self._extract_section(ai_response, 'TECHNOLOGIES')
            experience_level = self._extract_section(ai_response, 'EXPERIENCE_LEVEL')
            team_size = self._extract_section(ai_response, 'TEAM_SIZE')
            work_style = self._extract_section(ai_response, 'WORK_STYLE')
            responsibilities = self._extract_section(ai_response, 'KEY_RESPONSIBILITIES')
            nice_to_have = self._extract_section(ai_response, 'NICE_TO_HAVE')
            
            # Clean and split lists
            tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
            resp_list = [resp.strip() for resp in responsibilities.split(',') if resp.strip()]
            nth_list = [nth.strip() for nth in nice_to_have.split(',') if nth.strip()]
            
            return JobRequirements(
                technologies=tech_list,
                experience_level=experience_level.strip(),
                team_size=team_size.strip(),
                work_style=work_style.strip(),
                key_responsibilities=resp_list,
                nice_to_have=nth_list
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return self._fallback_job_parsing(original_text)
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the AI response"""
        pattern = rf'{section_name}:\s*([^\n]+(?:\n(?![\w\s]+:)[^\n]+)*)'
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _fallback_job_parsing(self, job_description: str) -> JobRequirements:
        """Fallback parsing using keyword matching"""
        text_lower = job_description.lower()
        
        # Find technologies mentioned
        found_technologies = []
        for tech in self.tech_keywords:
            if tech.lower() in text_lower:
                found_technologies.append(tech)
        
        # Determine experience level
        experience_level = "Mid-level"
        if any(word in text_lower for word in ['junior', 'entry', 'graduate', '0-2 years']):
            experience_level = "Junior"
        elif any(word in text_lower for word in ['senior', 'lead', 'principal', '5+ years', 'expert']):
            experience_level = "Senior"
        
        return JobRequirements(
            technologies=found_technologies,
            experience_level=experience_level,
            team_size="Unknown",
            work_style="Unknown",
            key_responsibilities=["See job description"],
            nice_to_have=[]
        )
    
    def calculate_job_match_score(self, profile, job_requirements: JobRequirements) -> float:
        """Calculate how well a candidate profile matches job requirements"""
        try:
            score = 0.0
            max_score = 1.0
            
            # Technology match (40% of score)
            if job_requirements.technologies:
                tech_overlap = set(profile.top_technologies) & set(job_requirements.technologies)
                tech_score = len(tech_overlap) / len(job_requirements.technologies)
                score += tech_score * 0.4
            
            # Experience level match (30% of score)
            experience_match = 0.0
            if job_requirements.experience_level.lower() == "junior" and profile.avg_complexity <= 4:
                experience_match = 1.0
            elif job_requirements.experience_level.lower() == "mid-level" and 4 < profile.avg_complexity <= 7:
                experience_match = 1.0
            elif job_requirements.experience_level.lower() == "senior" and profile.avg_complexity > 7:
                experience_match = 1.0
            else:
                experience_match = 0.5  # Partial match
            
            score += experience_match * 0.3
            
            # Collaboration score (20% of score)
            collaboration_normalized = profile.collaboration_score / 10.0
            score += collaboration_normalized * 0.2
            
            # Activity level (10% of score)
            activity_score = min(profile.repository_count / 10, 1.0)
            score += activity_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating job match score: {e}")
            return 0.5
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment and extract key themes from text"""
        try:
            prompt = f"""Analyze the sentiment and key themes of this text:

Text: {text}

Provide:
1. SENTIMENT: positive/negative/neutral
2. CONFIDENCE: 0.0 to 1.0
3. SUMMARY: Brief summary of the text
4. KEY_THEMES: Main themes or topics (comma-separated)

Format your response with clear sections as shown above."""

            response = self.cohere_client.generate(
                model='command',
                prompt=prompt,
                max_tokens=150,
                temperature=0.2
            )
            
            return self._parse_sentiment_response(response.generations[0].text)
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return SentimentResult(
                sentiment="neutral",
                confidence=0.5,
                summary="Analysis not available",
                key_themes=[]
            )
    
    def _parse_sentiment_response(self, ai_response: str) -> SentimentResult:
        """Parse sentiment analysis response"""
        try:
            sentiment = self._extract_section(ai_response, 'SENTIMENT').lower()
            confidence_str = self._extract_section(ai_response, 'CONFIDENCE')
            summary = self._extract_section(ai_response, 'SUMMARY')
            themes_str = self._extract_section(ai_response, 'KEY_THEMES')
            
            # Parse confidence
            confidence = 0.5
            try:
                confidence = float(confidence_str)
            except:
                pass
            
            # Parse themes
            themes = [theme.strip() for theme in themes_str.split(',') if theme.strip()]
            
            return SentimentResult(
                sentiment=sentiment if sentiment in ['positive', 'negative', 'neutral'] else 'neutral',
                confidence=max(0.0, min(1.0, confidence)),
                summary=summary if summary else "No summary available",
                key_themes=themes
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse sentiment response: {e}")
            return SentimentResult(
                sentiment="neutral",
                confidence=0.5,
                summary="Analysis not available",
                key_themes=[]
            )
    
    def generate_team_recommendations(self, profiles: List, team_size: int = 3) -> List[Dict]:
        """Generate optimal team combinations based on complementary skills"""
        try:
            if len(profiles) < team_size:
                return []
            
            # Simple greedy algorithm for team formation
            # Start with most experienced person as team lead
            sorted_profiles = sorted(profiles, key=lambda p: p.avg_complexity, reverse=True)
            
            teams = []
            remaining_profiles = sorted_profiles.copy()
            
            while len(remaining_profiles) >= team_size:
                team = [remaining_profiles.pop(0)]  # Team lead
                
                # Find complementary team members
                for _ in range(team_size - 1):
                    if not remaining_profiles:
                        break
                    
                    best_match = None
                    best_score = -1
                    
                    for candidate in remaining_profiles:
                        # Calculate team complementarity
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
            
            return teams
            
        except Exception as e:
            logger.error(f"Error generating team recommendations: {e}")
            return []

def main():
    """Test the matching engine"""
    try:
        matcher = MatchingEngine()
        
        # Test job description analysis
        sample_job = """
        We are looking for a Senior Full Stack Developer to join our team.
        Requirements:
        - 5+ years of experience with Python and JavaScript
        - Experience with React and Django
        - AWS cloud experience
        - Strong collaboration skills
        """
        
        requirements = matcher.extract_tech_requirements(sample_job)
        print("✓ Job Requirements Analysis:")
        print(f"  Technologies: {requirements.technologies}")
        print(f"  Experience Level: {requirements.experience_level}")
        
        # Test sentiment analysis
        sentiment = matcher.analyze_sentiment("I love working with innovative teams on challenging projects!")
        print(f"\n✓ Sentiment Analysis: {sentiment.sentiment} (confidence: {sentiment.confidence})")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")

if __name__ == '__main__':
    main() 