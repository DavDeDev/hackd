"""
Hackd - GitHub Profile Analyzer Service
Analyzes GitHub profiles for tech stack, collaboration patterns, and code complexity.
"""

import os
import json
import re
import base64
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import cohere
import pandas as pd
from github import Github
from github.GithubException import GithubException
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported code file extensions
CODE_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.html', '.css', '.jsx', '.tsx']

@dataclass
class TechProfile:
    """Data class for user's technical profile"""
    username: str
    languages: Dict[str, float]
    total_lines: int
    avg_complexity: float
    collaboration_score: float
    top_technologies: List[str]
    repository_count: int

@dataclass
class MatchingCriteria:
    """Data class for matching algorithm criteria"""
    tech_complementarity: float
    collaboration_compatibility: float
    experience_level: float
    activity_score: float

class GitHubAnalyzer:
    """Main class for analyzing GitHub profiles and generating matches"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")
            
        self.github_client = Github(self.github_token)
        self.cohere_client = cohere.Client(self.cohere_api_key)
        
    def is_code_file(self, filename: str) -> bool:
        """Check if a file is a code file based on its extension"""
        return os.path.splitext(filename)[1].lower() in CODE_EXTENSIONS
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.rb': 'Ruby', '.go': 'Go', '.php': 'PHP', '.html': 'HTML',
            '.css': 'CSS', '.jsx': 'React', '.tsx': 'TypeScript React'
        }
        return language_map.get(ext, ext[1:].upper() if ext else 'Unknown')
    
    def analyze_code_complexity(self, code: str, language: str) -> Dict[str, float]:
        """Analyze code complexity using Cohere AI"""
        try:
            prompt = f"""Analyze this {language} code and provide scores (0-10):

Code:
{code[:1000]}  # Limit code sample to avoid token limits

Provide only numerical scores:
Complexity: [0-10]
Quality: [0-10]
Maintainability: [0-10]"""

            response = self.cohere_client.generate(
                model='command',
                prompt=prompt,
                max_tokens=50,
                temperature=0.3
            )
            
            return self._parse_code_analysis(response.generations[0].text)
            
        except Exception as e:
            logger.warning(f"Code analysis failed: {e}")
            return {'complexity': 5.0, 'quality': 5.0, 'maintainability': 5.0}
    
    def _parse_code_analysis(self, response: str) -> Dict[str, float]:
        """Parse Cohere response for code analysis scores"""
        scores = {'complexity': 5.0, 'quality': 5.0, 'maintainability': 5.0}
        
        # Extract numerical scores using regex
        complexity_match = re.search(r'Complexity:\s*(\d+(?:\.\d+)?)', response)
        quality_match = re.search(r'Quality:\s*(\d+(?:\.\d+)?)', response)
        maintainability_match = re.search(r'Maintainability:\s*(\d+(?:\.\d+)?)', response)
        
        if complexity_match:
            scores['complexity'] = float(complexity_match.group(1))
        if quality_match:
            scores['quality'] = float(quality_match.group(1))
        if maintainability_match:
            scores['maintainability'] = float(maintainability_match.group(1))
            
        return scores
    
    def analyze_collaboration_quality(self, repo_data: Dict) -> float:
        """Analyze collaboration quality from repository data"""
        try:
            # Factors for collaboration score
            factors = {
                'has_readme': 1.0 if repo_data.get('has_readme') else 0.0,
                'commit_frequency': min(repo_data.get('commit_count', 0) / 100, 1.0),
                'contributor_count': min(repo_data.get('contributors', 1) / 5, 1.0),
                'issue_participation': min(repo_data.get('issues_count', 0) / 20, 1.0),
                'pr_activity': min(repo_data.get('pr_count', 0) / 10, 1.0)
            }
            
            # Weighted average
            weights = [0.2, 0.3, 0.25, 0.15, 0.1]
            collaboration_score = sum(score * weight for score, weight in zip(factors.values(), weights))
            
            return min(collaboration_score * 10, 10.0)  # Scale to 0-10
            
        except Exception as e:
            logger.warning(f"Collaboration analysis failed: {e}")
            return 5.0
    
    def analyze_user_profile(self, username: str) -> Optional[TechProfile]:
        """Analyze a single user's GitHub profile"""
        try:
            user = self.github_client.get_user(username)
            repos = list(user.get_repos(type='owner'))[:10]  # Limit to 10 most recent repos
            
            language_stats = {}
            total_lines = 0
            complexity_scores = []
            collaboration_scores = []
            
            for repo in repos:
                try:
                    # Get repository languages
                    repo_languages = repo.get_languages()
                    for lang, lines in repo_languages.items():
                        language_stats[lang] = language_stats.get(lang, 0) + lines
                        total_lines += lines
                    
                    # Analyze repository characteristics
                    repo_data = {
                        'has_readme': self._has_readme(repo),
                        'commit_count': repo.get_commits().totalCount,
                        'contributors': repo.get_contributors().totalCount,
                        'issues_count': repo.get_issues(state='all').totalCount,
                        'pr_count': repo.get_pulls(state='all').totalCount
                    }
                    
                    collab_score = self.analyze_collaboration_quality(repo_data)
                    collaboration_scores.append(collab_score)
                    
                    # Sample code files for complexity analysis
                    try:
                        contents = repo.get_contents("")
                        for content in contents[:5]:  # Limit file analysis
                            if content.type == 'file' and self.is_code_file(content.name):
                                code = base64.b64decode(content.content).decode('utf-8', errors='ignore')
                                language = self.detect_language(content.name)
                                analysis = self.analyze_code_complexity(code, language)
                                complexity_scores.append(analysis['complexity'])
                    except:
                        pass  # Skip if can't access files
                        
                except Exception as e:
                    logger.warning(f"Error analyzing repo {repo.name}: {e}")
                    continue
            
            # Calculate percentages for languages
            language_percentages = {}
            if total_lines > 0:
                for lang, lines in language_stats.items():
                    language_percentages[lang] = (lines / total_lines) * 100
            
            # Get top technologies (languages with >5% usage)
            top_technologies = [lang for lang, pct in language_percentages.items() if pct >= 5.0]
            
            return TechProfile(
                username=username,
                languages=language_percentages,
                total_lines=total_lines,
                avg_complexity=sum(complexity_scores) / len(complexity_scores) if complexity_scores else 5.0,
                collaboration_score=sum(collaboration_scores) / len(collaboration_scores) if collaboration_scores else 5.0,
                top_technologies=top_technologies,
                repository_count=len(repos)
            )
            
        except GithubException as e:
            logger.error(f"GitHub API error for user {username}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error analyzing {username}: {e}")
            return None
    
    def _has_readme(self, repo) -> bool:
        """Check if repository has a README file"""
        try:
            repo.get_readme()
            return True
        except:
            return False
    
    def calculate_tech_complementarity(self, profile1: TechProfile, profile2: TechProfile) -> float:
        """Calculate how well two tech profiles complement each other"""
        try:
            # Get all unique technologies
            all_techs = set(profile1.top_technologies + profile2.top_technologies)
            
            if not all_techs:
                return 0.5
            
            # Create vectors for each profile
            vector1 = [1 if tech in profile1.top_technologies else 0 for tech in all_techs]
            vector2 = [1 if tech in profile2.top_technologies else 0 for tech in all_techs]
            
            # Calculate complementarity (inverse of similarity for diversity)
            if sum(vector1) == 0 or sum(vector2) == 0:
                return 0.5
                
            similarity = cosine_similarity([vector1], [vector2])[0][0]
            complementarity = 1 - similarity  # More different = more complementary
            
            return max(0.0, min(1.0, complementarity))
            
        except Exception as e:
            logger.warning(f"Error calculating complementarity: {e}")
            return 0.5
    
    def generate_matches(self, profiles: List[TechProfile], target_username: str) -> List[Dict]:
        """Generate matches for a target user based on complementarity and collaboration"""
        target_profile = next((p for p in profiles if p.username == target_username), None)
        if not target_profile:
            return []
        
        matches = []
        for profile in profiles:
            if profile.username == target_username:
                continue
                
            # Calculate matching criteria
            tech_complementarity = self.calculate_tech_complementarity(target_profile, profile)
            collab_compatibility = abs(target_profile.collaboration_score - profile.collaboration_score) / 10
            experience_diff = abs(target_profile.avg_complexity - profile.avg_complexity) / 10
            
            # Combined match score (weighted)
            match_score = (
                tech_complementarity * 0.4 +  # Complementary skills
                (1 - collab_compatibility) * 0.3 +  # Similar collaboration style
                (1 - experience_diff) * 0.2 +  # Similar experience level
                (profile.repository_count / 20) * 0.1  # Activity level
            )
            
            matches.append({
                'username': profile.username,
                'match_score': match_score,
                'tech_complementarity': tech_complementarity,
                'collaboration_score': profile.collaboration_score,
                'top_technologies': profile.top_technologies,
                'experience_level': profile.avg_complexity
            })
        
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:10]  # Return top 10 matches

def main():
    """Main function for testing the GitHub analyzer"""
    analyzer = GitHubAnalyzer()
    
    # Example usage
    test_usernames = ['octocat', 'torvalds', 'gaearon']  # Replace with actual usernames
    profiles = []
    
    for username in test_usernames:
        print(f"Analyzing {username}...")
        profile = analyzer.analyze_user_profile(username)
        if profile:
            profiles.append(profile)
            print(f"✓ Analyzed {username}: {len(profile.top_technologies)} technologies")
        else:
            print(f"✗ Failed to analyze {username}")
    
    # Generate matches for first user
    if profiles:
        matches = analyzer.generate_matches(profiles, profiles[0].username)
        print(f"\nTop matches for {profiles[0].username}:")
        for match in matches[:3]:
            print(f"- {match['username']}: {match['match_score']:.2f}")

if __name__ == '__main__':
    main() 