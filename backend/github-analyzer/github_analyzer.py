"""
Hackd GitHub Profile Analyzer - Direct execution, no defensive code
"""

import os
import json
import re
import base64
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import cohere
from github import Github

# Import comprehensive logging system
import sys
sys.path.append('..')
from logging_config import get_business_logger, get_logger

CODE_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.html', '.css', '.jsx', '.tsx']

@dataclass
class TechProfile:
    username: str
    languages: Dict[str, float]
    total_lines: int
    avg_complexity: float
    collaboration_score: float
    top_technologies: List[str]
    repository_count: int

@dataclass
class MatchingCriteria:
    tech_complementarity: float
    collaboration_compatibility: float
    experience_level: float
    activity_score: float

class GitHubAnalyzer:
    """Direct GitHub profile analysis with comprehensive logging"""
    
    def __init__(self):
        self.logger = get_business_logger("github-analyzer")
        
        self.logger.log_function_entry("__init__")
        start_time = time.time()
        
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        self.logger.debug("Initializing API clients", extra_data={
            'github_token_configured': bool(self.github_token),
            'cohere_token_configured': bool(self.cohere_api_key)
        })
        
        self.github_client = Github(self.github_token)
        self.cohere_client = cohere.Client(self.cohere_api_key)
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("__init__", result="GitHubAnalyzer instance", execution_time=execution_time)
        self.logger.info("GitHub analyzer initialized successfully")
        
    def is_code_file(self, filename: str) -> bool:
        """Check if file is a code file based on extension"""
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
        self.logger.log_function_entry("analyze_code_complexity", args={
            'language': language,
            'code_length': len(code)
        })
        start_time = time.time()
        
        prompt = f"""Analyze this {language} code and provide scores (0-10):

Code:
{code[:1000]}

Provide only numerical scores:
Complexity: [0-10]
Quality: [0-10]  
Maintainability: [0-10]"""

        self.logger.log_ai_request("cohere", prompt, model="command", tokens=50)
        
        response = self.cohere_client.generate(
            model='command',
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )
        
        response_text = response.generations[0].text
        self.logger.log_ai_response("cohere", len(response_text))
        
        result = self._parse_code_analysis(response_text)
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("analyze_code_complexity", result=result, execution_time=execution_time)
        self.logger.debug(f"Code complexity analysis completed", extra_data={
            'language': language,
            'scores': result,
            'processing_time': execution_time
        })
        
        return result
        
    def _parse_code_analysis(self, response: str) -> Dict[str, float]:
        """Parse Cohere response for code analysis scores"""
        scores = {'complexity': 5.0, 'quality': 5.0, 'maintainability': 5.0}
        
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
        github_logger.debug("Analyzing collaboration quality")
        
        factors = {
            'has_readme': 1.0 if repo_data.get('has_readme') else 0.0,
            'commit_frequency': min(repo_data.get('commit_count', 0) / 100, 1.0),
            'contributor_count': min(repo_data.get('contributors', 1) / 5, 1.0),
            'issue_participation': min(repo_data.get('issues_count', 0) / 20, 1.0),
            'pr_activity': min(repo_data.get('pr_count', 0) / 10, 1.0)
        }
        
        weights = [0.2, 0.3, 0.25, 0.15, 0.1]
        collaboration_score = sum(score * weight for score, weight in zip(factors.values(), weights))
        
        result = min(collaboration_score * 10, 10.0)
        github_logger.debug(f"Collaboration score calculated: {result}")
        return result
        
    def analyze_user_profile(self, username: str) -> Optional[TechProfile]:
        """Analyze a single user's GitHub profile with comprehensive logging"""
        self.logger.log_function_entry("analyze_user_profile", args={'username': username})
        start_time = time.time()
        
        try:
            # GitHub API call for user data
            self.logger.log_github_api_call(f"/users/{username}", username=username)
            user = self.github_client.get_user(username)
            
            # Log user basic info
            self.logger.debug("Retrieved user data", extra_data={
                'username': username,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following,
                'account_created': str(user.created_at)
            })
            
            # Get repositories
            self.logger.log_github_api_call(f"/users/{username}/repos", username=username)
            repos = list(user.get_repos(type='owner'))[:10]
            
            language_stats = {}
            total_lines = 0
            complexity_scores = []
            collaboration_scores = []
            
            self.logger.debug(f"Processing {len(repos)} repositories", extra_data={
                'username': username,
                'repo_count': len(repos),
                'repo_names': [repo.name for repo in repos]
            })
            
            for i, repo in enumerate(repos):
                repo_start_time = time.time()
                self.logger.debug(f"Processing repository {i+1}/{len(repos)}: {repo.name}", extra_data={
                    'repo_name': repo.name,
                    'repo_language': repo.language,
                    'repo_size': repo.size,
                    'repo_stars': repo.stargazers_count,
                    'repo_forks': repo.forks_count
                })
                
                # Get repository languages
                self.logger.log_github_api_call(f"/repos/{username}/{repo.name}/languages", username=username, repo=repo.name)
                repo_languages = repo.get_languages()
                
                self.logger.log_data_processing("language_aggregation", len(repo_languages))
                for lang, lines in repo_languages.items():
                    language_stats[lang] = language_stats.get(lang, 0) + lines
                    total_lines += lines
                
                # Analyze repository characteristics
                self.logger.debug("Analyzing repository collaboration metrics", extra_data={
                    'repo_name': repo.name
                })
                
                repo_data = {
                    'has_readme': self._has_readme(repo),
                    'commit_count': repo.get_commits().totalCount,
                    'contributors': repo.get_contributors().totalCount,
                    'issues_count': repo.get_issues(state='all').totalCount,
                    'pr_count': repo.get_pulls(state='all').totalCount
                }
                
                self.logger.debug("Repository metrics collected", extra_data={
                    'repo_name': repo.name,
                    'metrics': repo_data
                })
                
                collab_score = self.analyze_collaboration_quality(repo_data)
                collaboration_scores.append(collab_score)
                
                # Sample code files for complexity analysis
                try:
                    self.logger.log_github_api_call(f"/repos/{username}/{repo.name}/contents", username=username, repo=repo.name)
                    contents = repo.get_contents("")
                    code_files_analyzed = 0
                    
                    for content in contents[:5]:
                        if content.type == 'file' and self.is_code_file(content.name):
                            try:
                                code = base64.b64decode(content.content).decode('utf-8', errors='ignore')
                                language = self.detect_language(content.name)
                                
                                self.logger.debug("Analyzing code file", extra_data={
                                    'file_name': content.name,
                                    'file_size': len(code),
                                    'detected_language': language
                                })
                                
                                analysis = self.analyze_code_complexity(code, language)
                                complexity_scores.append(analysis['complexity'])
                                code_files_analyzed += 1
                                
                            except Exception as e:
                                self.logger.error(f"Failed to analyze file {content.name}", exception=e)
                    
                    self.logger.debug(f"Repository processing completed", extra_data={
                        'repo_name': repo.name,
                        'code_files_analyzed': code_files_analyzed,
                        'processing_time': time.time() - repo_start_time
                    })
                    
                except Exception as e:
                    self.logger.error(f"Failed to get repository contents for {repo.name}", exception=e)
            
            # Calculate language percentages
            self.logger.log_data_processing("language_percentage_calculation", len(language_stats))
            language_percentages = {}
            if total_lines > 0:
                for lang, lines in language_stats.items():
                    language_percentages[lang] = (lines / total_lines) * 100
            
            # Get top technologies (languages with >5% usage)
            top_technologies = [lang for lang, pct in language_percentages.items() if pct >= 5.0]
            
            # Create profile
            avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 5.0
            avg_collaboration = sum(collaboration_scores) / len(collaboration_scores) if collaboration_scores else 5.0
            
            profile = TechProfile(
                username=username,
                languages=language_percentages,
                total_lines=total_lines,
                avg_complexity=avg_complexity,
                collaboration_score=avg_collaboration,
                top_technologies=top_technologies,
                repository_count=len(repos)
            )
            
            execution_time = time.time() - start_time
            
            self.logger.debug("Profile analysis completed", extra_data={
                'username': username,
                'total_repositories': len(repos),
                'total_lines_of_code': total_lines,
                'languages_found': len(language_percentages),
                'top_technologies': top_technologies,
                'avg_complexity_score': avg_complexity,
                'avg_collaboration_score': avg_collaboration,
                'complexity_samples': len(complexity_scores),
                'execution_time': execution_time
            })
            
            self.logger.log_function_exit("analyze_user_profile", result=profile, execution_time=execution_time)
            return profile
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Profile analysis failed for {username}", 
                            extra_data={'username': username, 'execution_time': execution_time}, 
                            exception=e)
            self.logger.log_function_exit("analyze_user_profile", result=None, execution_time=execution_time)
            return None
    
    def _has_readme(self, repo) -> bool:
        """Check if repository has a README file"""
        repo.get_readme()
        return True
    
    def calculate_tech_complementarity(self, profile1: TechProfile, profile2: TechProfile) -> float:
        """Calculate how well two tech profiles complement each other"""
        github_logger.debug(f"Calculating tech complementarity between {profile1.username} and {profile2.username}")
        
        all_techs = set(profile1.top_technologies + profile2.top_technologies)
        
        vector1 = [1 if tech in profile1.top_technologies else 0 for tech in all_techs]
        vector2 = [1 if tech in profile2.top_technologies else 0 for tech in all_techs]
        
        # Calculate dot product similarity
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5
        
        similarity = dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 > 0 else 0
        complementarity = 1 - similarity  # More different = more complementary
        
        result = max(0.0, min(1.0, complementarity))
        github_logger.debug(f"Tech complementarity calculated: {result:.3f}")
        return result
    
    def generate_matches(self, profiles: List[TechProfile], target_username: str) -> List[Dict]:
        """Generate matches for a target user based on complementarity and collaboration"""
        self.logger.log_function_entry("generate_matches", args={
            'target_username': target_username,
            'total_profiles': len(profiles)
        })
        start_time = time.time()
        
        target_profile = next((p for p in profiles if p.username == target_username), None)
        
        if not target_profile:
            self.logger.error(f"Target profile not found", extra_data={
                'target_username': target_username,
                'available_profiles': [p.username for p in profiles]
            })
            return []
        
        matches = []
        for i, profile in enumerate(profiles):
            if profile.username == target_username:
                continue
            
            match_start_time = time.time()    
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
            
            match_data = {
                'username': profile.username,
                'match_score': match_score,
                'tech_complementarity': tech_complementarity,
                'collaboration_score': profile.collaboration_score,
                'top_technologies': profile.top_technologies,
                'experience_level': profile.avg_complexity
            }
            
            # Log detailed matching calculation
            self.logger.log_matching_calculation(
                target_username, 
                profile.username, 
                match_score,
                {
                    'tech_complementarity': tech_complementarity,
                    'collab_compatibility': 1 - collab_compatibility,
                    'experience_compatibility': 1 - experience_diff,
                    'activity_score': profile.repository_count / 20
                }
            )
            
            matches.append(match_data)
        
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        execution_time = time.time() - start_time
        self.logger.log_function_exit("generate_matches", result=matches[:10], execution_time=execution_time)
        
        self.logger.info(f"Generated {len(matches)} matches for {target_username}", extra_data={
            'target_username': target_username,
            'matches_generated': len(matches),
            'top_match_score': matches[0]['match_score'] if matches else 0,
            'execution_time': execution_time
        })
        
        return matches[:10]

def main():
    """Test the GitHub analyzer"""
    os.makedirs('logs', exist_ok=True)
    
    analyzer = GitHubAnalyzer()
    
    test_usernames = ['octocat', 'torvalds', 'gaearon']
    profiles = []
    
    for username in test_usernames:
        print(f"Analyzing {username}...")
        profile = analyzer.analyze_user_profile(username)
        if profile:
            profiles.append(profile)
            print(f"Analyzed {username}: {len(profile.top_technologies)} technologies")
        else:
            print(f"Failed to analyze {username}")
    
    if profiles:
        matches = analyzer.generate_matches(profiles, profiles[0].username)
        print(f"Top matches for {profiles[0].username}:")
        for match in matches[:3]:
            print(f"- {match['username']}: {match['match_score']:.2f}")

if __name__ == '__main__':
    main()