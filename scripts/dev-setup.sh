#!/bin/bash

# Hackd Development Setup Script
# Automates the setup process for new developers

set -e

echo "🚀 Setting up Hackd development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    print_status "Python 3 found"
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    print_status "Node.js found"
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    print_status "npm found"
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_status "Git found"
}

# Setup backend
setup_backend() {
    echo "🐍 Setting up Python backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Activated virtual environment"
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Setup environment file
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_warning "Created .env file from template. Please add your API keys!"
    else
        print_status ".env file already exists"
    fi
    
    cd ..
}

# Setup frontend
setup_frontend() {
    echo "⚛️ Setting up React frontend..."
    
    cd frontend/hackd-web
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Setup environment file
    if [ ! -f ".env.local" ]; then
        cp .env.local.example .env.local
        print_warning "Created .env.local file from template. Please configure your settings!"
    else
        print_status ".env.local file already exists"
    fi
    
    cd ../..
}

# Create development scripts
create_dev_scripts() {
    echo "📝 Creating development scripts..."
    
    # Backend start script
    cat > scripts/start-backend.sh << 'EOF'
#!/bin/bash
echo "🐍 Starting Hackd backend..."
cd backend
source venv/bin/activate
python api/main.py
EOF
    chmod +x scripts/start-backend.sh
    
    # Frontend start script
    cat > scripts/start-frontend.sh << 'EOF'
#!/bin/bash
echo "⚛️ Starting Hackd frontend..."
cd frontend/hackd-web
npm run dev
EOF
    chmod +x scripts/start-frontend.sh
    
    # Full stack start script
    cat > scripts/start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Hackd full-stack development..."

# Function to handle cleanup
cleanup() {
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🐍 Starting backend..."
cd backend && source venv/bin/activate && python api/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️ Starting frontend..."
cd frontend/hackd-web && npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "   • Backend: http://localhost:5000"
echo "   • Frontend: http://localhost:3000"
echo "   • Health Check: http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background processes
wait
EOF
    chmod +x scripts/start-dev.sh
    
    print_status "Created development scripts"
}

# Run health checks
run_health_checks() {
    echo "🏥 Running health checks..."
    
    # Check if .env files have been configured
    if grep -q "your_github_personal_access_token_here" backend/.env 2>/dev/null; then
        print_warning "Backend .env file needs configuration"
    else
        print_status "Backend environment configured"
    fi
    
    if grep -q "your_convex_deployment_id" frontend/hackd-web/.env.local 2>/dev/null; then
        print_warning "Frontend .env.local file needs configuration"
    else
        print_status "Frontend environment configured"
    fi
}

# Main setup process
main() {
    echo "🎯 Hackd Development Setup"
    echo "=========================="
    
    check_dependencies
    setup_backend
    setup_frontend
    create_dev_scripts
    run_health_checks
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your API keys in backend/.env"
    echo "2. Configure your settings in frontend/hackd-web/.env.local"
    echo "3. Run: ./scripts/start-dev.sh"
    echo ""
    echo "For individual services:"
    echo "• Backend only: ./scripts/start-backend.sh"
    echo "• Frontend only: ./scripts/start-frontend.sh"
    echo ""
    echo "Happy hacking! 🚀"
}

# Run main function
main "$@" 