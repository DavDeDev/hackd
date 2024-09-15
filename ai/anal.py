import os
import json
import re
import base64
import cohere
import pandas as pd
from github import Github
from github.GithubException import GithubException
from sklearn.preprocessing import MinMaxScaler

# -----------------------------------
# Configuration
# -----------------------------------

# Set your GitHub and Cohere API tokens
GITHUB_TOKEN = 'your_github_token'
COHERE_API_KEY = 'your_cohere_api_key'

# Path to your JSON file containing GitHub usernames
JSON_FILE_PATH = 'usernames.json'

# Output CSV file path
OUTPUT_FILE_PATH = 'user_code_analysis_results.csv'

# Supported code file extensions
CODE_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.ts']

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

# -----------------------------------
# Main Analysis Function
# -----------------------------------

def main():
    # Read usernames from JSON
    usernames = read_usernames(JSON_FILE_PATH)
    user_data = []

    # Loop through each user
    for username in usernames:
        print(f"Processing user: {username}")
        try:
            user = g.get_user(username)
            repos = user.get_repos()
            for repo in repos:
                try:
                    contents = repo.get_contents("")
                    while contents:
                        file_content = contents.pop(0)
                        if file_content.type == 'dir':
                            contents.extend(repo.get_contents(file_content.path))
                        else:
                            if is_code_file(file_content.name):
                                language = detect_language(file_content.name)
                                # Decode file content
                                code = base64.b64decode(file_content.content).decode('utf-8', errors='ignore')
                                # Analyze code using Cohere
                                analysis = analyze_code_with_cohere(code)
                                if analysis['complexity'] is not None and analysis['syntax_quality'] is not None:
                                    user_data.append({
                                        'username': username,
                                        'repository': repo.name,
                                        'file_path': file_content.path,
                                        'language': language,
                                        'complexity': analysis['complexity'],
                                        'syntax_quality': analysis['syntax_quality']
                                    })
                except GithubException as ge:
                    print(f"Error accessing repository {repo.name} for user {username}: {ge}")
                except Exception as e:
                    print(f"Error processing file in repository {repo.name} for user {username}: {e}")
        except GithubException as ge:
            print(f"Error accessing user {username}: {ge}")
        except Exception as e:
            print(f"Unexpected error with user {username}: {e}")

    if user_data:
        # Create DataFrame
        df = pd.DataFrame(user_data)

        # Normalize scores
        scaler = MinMaxScaler()
        df[['complexity_norm', 'syntax_quality_norm']] = scaler.fit_transform(df[['complexity', 'syntax_quality']])

        # Compute total points
        df['total_points'] = df['complexity_norm'] + df['syntax_quality_norm']

        # Group by username and language
        df_grouped = df.groupby(['username', 'language']).agg({
            'complexity': 'mean',
            'syntax_quality': 'mean',
            'total_points': 'sum'
        }).reset_index()

        # Assign relative points within each language group
        df_grouped['language_points'] = df_grouped.groupby('language')['total_points'].transform(
            lambda x: x / x.sum()
        )

        # Output results to CSV
        df_grouped.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"Analysis complete. Results saved to {OUTPUT_FILE_PATH}")
    else:
        print("No data was collected for analysis.")

# -----------------------------------
# Run the Script
# -----------------------------------

if __name__ == '__main__':
    main()
