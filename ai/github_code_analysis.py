import os
import json
import re
import base64
import cohere
import pandas as pd
from github import Github
from github.GithubException import GithubException
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------
# Configuration
# -----------------------------------

# Set your GitHub and Cohere API tokens
GITHUB_TOKEN = '***REMOVED***'  # Realistic-looking GitHub token
COHERE_API_KEY = 'your_cohere_api_key_12345' 

# Path to your JSON file containing GitHub usernames
JSON_FILE_PATH = '/home/user/github_analysis/usernames.json 

# Output CSV file path
OUTPUT_FILE_PATH = '/home/user/github_analysis/code_analysis_results.csv'   

# Supported code file extensions
CODE_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.ts', '.html', '.css']   

# -----------------------------------
# Initialize APIs
# -----------------------------------

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

# Initialize Cohere API client
co = cohere.Client(COHERE_API_KEY)

# -----------------------------------
# Helper Functions
# -----------------------------------

def read_usernames(json_file_path):
    """Read GitHub usernames from a JSON file."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        usernames = data.get('usernames', [])
    return [username.strip() for username in usernames]

def is_code_file(filename):
    """Check if a file is a code file based on its extension."""
    return os.path.splitext(filename)[1] in CODE_EXTENSIONS

def detect_language(filename):
    """Detect programming language based on file extension."""
    return os.path.splitext(filename)[1][1:]  # Returns extension without dot

def analyze_code_with_cohere(code):
    """Analyze code complexity and syntax quality using Cohere API."""
    prompt = f"""Analyze the following code and provide a numerical score between 0 and 10 for both code complexity and syntax quality.

Code:
{code}

Response Format:
Complexity Score: <number between 0 and 10>
Syntax Quality Score: <number between 0 and 10>

Analysis:"""

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        stop_sequences=["\n\n"]
    )

    analysis = response.generations[0].text.strip()
    return parse_cohere_response(analysis)

def parse_cohere_response(response_text):
    """Extract complexity and syntax quality scores from Cohere API response."""
    complexity = extract_score(response_text, 'Complexity Score')
    syntax_quality = extract_score(response_text, 'Syntax Quality Score')
    return {
        'complexity': complexity,
        'syntax_quality': syntax_quality
    }

def extract_score(text, score_name):
    """Extract numerical score from the response text."""
    pattern = rf'{score_name}:\s*([\d\.]+)'
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    else:
        return None

def get_cosine_similarity(embeddings1, embeddings2):
    """Calculate cosine similarity between two sets of embeddings."""
    return cosine_similarity([embeddings1], [embeddings2])[0][0]

def analyze_collaboration(pr_comments, code_comments):
    """Analyze the quality of collaboration using Cohere API."""
    collaboration_prompt = f"""Analyze the following collaboration quality based on code comments and pull request comments.

Code Comments:
{code_comments}

PR Comments:
{pr_comments}

Response Format:
Collaboration Quality Score: <number between 0 and 10>

Analysis:"""

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=collaboration_prompt,
        max_tokens=100,
        temperature=0.5,
        stop_sequences=["\n\n"]
    )

    analysis = response.generations[0].text.strip()
    return extract_score(analysis, 'Collaboration Quality Score')

# -----------------------------------
# Main Analysis Function
# -----------------------------------

def main():
    # Read usernames from JSON
    usernames = read_usernames(JSON_FILE_PATH)
    user_data = []

    all_tech_embeddings = []
    tech_languages = []
    tech_repos = {}

    # Loop through each user
    for username in usernames:
        print(f"Processing user: {username}")
        try:
            user = g.get_user(username)
            repos = user.get_repos()
            for repo in repos:
                try:
                    contents = repo.get_contents("")
                    repo_tech_data = {'repo_name': repo.name, 'languages': [], 'line_counts': {}, 'collab_scores': []}
                    while contents:
                        file_content = contents.pop(0)
                        if file_content.type == 'dir':
                            contents.extend(repo.get_contents(file_content.path))
                        else:
                            if is_code_file(file_content.name):
                                language = detect_language(file_content.name)
                                code = base64.b64decode(file_content.content).decode('utf-8', errors='ignore')
                                analysis = analyze_code_with_cohere(code)
                                if analysis['complexity'] is not None and analysis['syntax_quality'] is not None:
                                    # Store tech language, complexity, and syntax analysis
                                    tech_repos.setdefault(repo.name, []).append(language)
                                    repo_tech_data['languages'].append(language)
                                    repo_tech_data['line_counts'][file_content.path] = len(code.splitlines())
                                    
                                    # Store code comments and PR comments for collaboration analysis
                                    pr_comments = ""  # PR comments would be fetched here
                                    code_comments = ""  # Code comments would be fetched here
                                    collab_score = analyze_collaboration(pr_comments, code_comments)
                                    repo_tech_data['collab_scores'].append(collab_score)

                    user_data.append({
                        'username': username,
                        'repository': repo.name,
                        'tech_data': repo_tech_data
                    })
                except GithubException as ge:
                    print(f"Error accessing repository {repo.name} for user {username}: {ge}")
                except Exception as e:
                    print(f"Error processing file in repository {repo.name} for user {username}: {e}")
        except GithubException as ge:
            print(f"Error accessing user {username}: {ge}")
        except Exception as e:
            print(f"Unexpected error with user {username}: {e}")

    # Collect tech embeddings
    for username_data in user_data:
        for repo_data in username_data['tech_data']:
            for lang in repo_data['languages']:
                if lang not in tech_languages:
                    tech_languages.append(lang)

    # Create tech embeddings for cosine similarity calculations
    for lang in tech_languages:
        # Generate embedding for each tech/language
        response = co.embed(model="command-xlarge", texts=[lang])
        tech_embeddings = response.embeddings[0]
        all_tech_embeddings.append(tech_embeddings)

    # Calculate cosine similarity to identify complementary technologies
    for repo_name, languages in tech_repos.items():
        for i, lang1 in enumerate(languages):
            for j, lang2 in enumerate(languages):
                if i < j:
                    similarity = get_cosine_similarity(all_tech_embeddings[tech_languages.index(lang1)], all_tech_embeddings[tech_languages.index(lang2)])
                    print(f"Cosine similarity between {lang1} and {lang2} in repo {repo_name}: {similarity}")

    if user_data:
        # Create DataFrame
        df = pd.DataFrame(user_data)

        # Normalize scores
        scaler = MinMaxScaler()
        df[['collaboration_score']] = scaler.fit_transform(df[['collab_scores']])

        # Output results to CSV
        df.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"Analysis complete. Results saved to {OUTPUT_FILE_PATH}")
    else:
        print("No data was collected for analysis.")

# -----------------------------------
# Run the Script
# -----------------------------------

if __name__ == '__main__':
    main()
