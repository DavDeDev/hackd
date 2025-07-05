# Hackd - Hacker Matching Platform

[![Deploy with Defang](https://defang.io/deploy-with-defang.png)](https://portal.defang.dev/redirect?url=https%3A%2F%2Fgithub.com%2Fnew%3Ftemplate_name%3Dhackd-template%26template_owner%3DHackTheNorthTeam)

## Overview

**Problem**: Finding teammates at hackathons is difficult. Slack channels get crowded and reaching out is awkward.

**Solution**: Hackd analyzes GitHub profiles and matches hackers using sentiment and code analysis.

## Features

- GitHub profile and coding pattern analysis
- AI-powered matching using Cohere
- Recruiter dashboard
- Collaboration scoring
- Clean React interface

## Architecture

```
hackd/
├── backend/
│   ├── api/main.py
│   ├── github-analyzer/github_analyzer.py
│   ├── matching/matcher.py
│   └── requirements.txt
├── frontend/hackd-web/
│   ├── app/{matching,recruiting,hacker}/
│   ├── convex/
│   └── lib/api.ts
└── config/docker-compose.yml
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git
- GitHub Personal Access Token
- Cohere API Key

### Setup

```bash
git clone https://github.com/your-username/hackd.git
cd hackd

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend/hackd-web
npm install
```

### Configuration

#### Backend

```bash
cp .env.example .env
# Edit with keys
```

#### Frontend

```bash
cp .env.local.example .env.local
# Edit with keys
```

### API Keys Needed

| Service | Use |
|---------|-----|
| GitHub  | Profile analysis |
| Cohere  | Matching |
| Convex  | Auth and DB |

### Run

**Dev Mode**

```bash
# Terminal 1
cd backend
python api/main.py

# Terminal 2
cd frontend/hackd-web
npm run dev
```

**Docker**

```bash
cd config
docker-compose up --build
```

Access at `http://localhost:3000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/analyze-github` | POST | GitHub profile analysis |
| `/api/match-users` | POST | Match hackers |
| `/api/analyze-job-description` | POST | Job parsing |
| `/api/analyze-sentiment` | POST | Sentiment |

### Example

```js
const res = await fetch('http://localhost:5000/api/analyze-github', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'octocat' })
});
const data = await res.json();
console.log(data.top_technologies);
```

## Matching Logic

```python
match_score = (
    tech_complementarity * 0.4 +
    experience_compatibility * 0.3 +
    collaboration_compatibility * 0.2 +
    activity_level * 0.1
)
```
