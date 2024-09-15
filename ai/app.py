from flask import Flask, jsonify, request
import cohere
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

app = Flask(__name__)

# Initialize Cohere client
COHERE_API_KEY = 'your-cohere-api-key'
co = cohere.Client(COHERE_API_KEY)

# Load and preprocess data
df = pd.read_csv('your_data.csv')  # Replace with your actual CSV file

# Function to process and prepare data
def process_data():
    # Extract skills and create a summary
    language_columns = [col for col in df.columns if '%' in col]
    df['Skills'] = df.apply(
        lambda row: {lang.replace('%', ''): row[lang] for lang in language_columns if row[lang] > 0},
        axis=1
    )
    df['SkillSummary'] = df.apply(generate_summary, axis=1)

    # Identify weaknesses using Cohere
    df['Weaknesses'] = df['SkillSummary'].apply(identify_weakness)

    # Generate embeddings
    embeddings = co.embed(texts=df['SkillSummary'].tolist(), model='large').embeddings
    df['Embeddings'] = embeddings

    # Compute similarity matrix
    similarity_matrix = cosine_similarity(embeddings)

    # Find complementary users
    df['ComplementaryUsers'] = df.index.map(lambda idx: find_complementary_users(idx, similarity_matrix))

    # Generate recommendations
    df['Recommendation'] = df.apply(generate_recommendation, axis=1)

    # Normalize scores for visualizations
    scaler = MinMaxScaler()
    score_columns = ['Commitment', 'TeamDynamics', 'WorkStyle', 'SkillsExperience', 'MotivationGoals']
    df[score_columns] = scaler.fit_transform(df[score_columns])

    return df

def generate_summary(row):
    skills = row['Skills']
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    skill_descriptions = [f"{skill} ({percentage}%)" for skill, percentage in sorted_skills]
    return f"User {row['Username']} is proficient in {', '.join(skill_descriptions)}."

def identify_weakness(summary):
    prompt = f"{summary}\n\nIdentify the user's weaknesses and areas for improvement."
    response = co.generate(model='command', prompt=prompt, max_tokens=50)
    return response.generations[0].text.strip()

def find_complementary_users(user_index, similarity_matrix):
    user_similarities = similarity_matrix[user_index]
    complementary_indices = np.argsort(user_similarities)
    complementary_indices = complementary_indices[complementary_indices != user_index]
    return df.iloc[complementary_indices[:5]]['Username'].tolist()

def generate_recommendation(row):
    recommendation = f"User {row['Username']} could improve in {row['Weaknesses']}.\n"
    recommendation += f"Potential teammates to complement their skills: {', '.join(row['ComplementaryUsers'])}."
    return recommendation

# API endpoint to get matching data
@app.route('/get-matching-data', methods=['GET'])
def get_matching_data():
    processed_df = process_data()
    data = processed_df.to_dict(orient='records')
    return jsonify(data)

# API endpoint to analyze job description
@app.route('/analyze-job-description', methods=['POST'])
def analyze_job_description():
    data = request.json
    job_description = data.get('job_description', '')
    # Use Cohere to analyze the job description or perform matching logic
    # For simplicity, we'll just return the job description
    return jsonify({'job_description': job_description})

if __name__ == '__main__':
    app.run(debug=True)
