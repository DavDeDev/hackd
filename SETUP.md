# 🚀 Hackd Setup Guide

## Quick Start

### 1. Dependencies
- Python 3.11+
- Node.js 18+
- Git

### 2. API Keys Required
- GitHub Personal Access Token
- Cohere API Key  
- Convex Project

### 3. Installation

```bash
# Run the automated setup
./scripts/dev-setup.sh

# Configure your environment
cp backend/.env.example backend/.env
cp frontend/hackd-web/.env.local.example frontend/hackd-web/.env.local

# Add your API keys to the .env files

# Start development
./scripts/start-dev.sh
```

### 4. Verify Installation

- Backend: http://localhost:5000/health
- Frontend: http://localhost:3000

## Architecture

- `backend/` - Python Flask API
- `frontend/hackd-web/` - Next.js React app  
- `config/` - Docker & deployment configs
- `scripts/` - Development utilities

Built with ❤️ for Hack the North 2024 