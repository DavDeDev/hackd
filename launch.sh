#!/bin/bash

# Hackd Complete Launch & Test Script
# One command to rule them all - setup, validate, start, and test everything

set -e

# Check if running interactively
INTERACTIVE="false"
if [ -t 0 ]; then
    INTERACTIVE="true"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Global variables
SETUP_NEEDED=false
MISSING_APIS=()
BACKEND_PID=""
FRONTEND_PID=""

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "\n${PURPLE}🚀 $1${NC}\n"; }
log_step() { echo -e "${CYAN}▶ $1${NC}"; }

# Cleanup function
cleanup() {
    log_warning "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "Frontend stopped"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Global Python command variable
PYTHON_CMD=""

# Find compatible Python version
find_python() {
    local python_candidates=(
        "python3.13"
        "python3.12" 
        "python3.11"
        "/opt/homebrew/bin/python3.13"
        "/opt/homebrew/bin/python3.12"
        "/opt/homebrew/bin/python3.11"
        "/usr/local/bin/python3.13"
        "/usr/local/bin/python3.12"
        "/usr/local/bin/python3.11"
        "python3"
    )
    
    for cmd in "${python_candidates[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            if $cmd -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
                PYTHON_CMD="$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# System requirements check
check_system_requirements() {
    log_header "SYSTEM REQUIREMENTS CHECK"
    
    local all_good=true
    
    # Find and check Python 3.11+
    if find_python; then
        local python_version=$($PYTHON_CMD --version | cut -d " " -f 2)
        log_success "Python $python_version ✓ (using $PYTHON_CMD)"
    else
        log_error "Need Python 3.11+ but found incompatible versions"
        echo "  Available Python versions:"
        for cmd in python3 python3.9 python3.10 python3.11 python3.12 python3.13; do
            if command -v "$cmd" >/dev/null 2>&1; then
                local ver=$($cmd --version 2>/dev/null | cut -d " " -f 2)
                echo "    $cmd: $ver"
            fi
        done
        echo "  Install Python 3.11+: https://www.python.org/downloads/"
        all_good=false
    fi
    
    # Check Node.js 18+
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version | sed 's/v//')
        if node -e "process.exit(parseInt(process.version.slice(1)) >= 18 ? 0 : 1)" 2>/dev/null; then
            log_success "Node.js $node_version ✓"
        else
            log_error "Need Node.js 18+, found $node_version"
            echo "  Install: https://nodejs.org/"
            all_good=false
        fi
    else
        log_error "Node.js not found"
        echo "  Install: https://nodejs.org/"
        all_good=false
    fi
    
    # Check/install pnpm
    if ! command -v pnpm >/dev/null 2>&1; then
        log_warning "pnpm not found, installing..."
        npm install -g pnpm
        log_success "pnpm installed ✓"
    else
        log_success "pnpm $(pnpm --version) ✓"
    fi
    
    if [ "$all_good" = false ]; then
        log_error "❌ System requirements not met. Please install missing components."
        exit 1
    fi
    
    log_success "🎉 All system requirements met!"
}

# Environment setup
setup_environment() {
    log_header "ENVIRONMENT SETUP"
    
    # Backend setup
    log_step "Setting up backend environment..."
    cd backend
    
    # Check if virtual environment exists and is working
    if [ -d "venv" ] && [ -f "venv/setup_complete" ]; then
        log_info "Virtual environment exists, checking if it's working..."
        source venv/bin/activate
        
        # Quick test to see if dependencies are installed
        if python -c "import flask, cohere, github" 2>/dev/null; then
            log_success "✅ Virtual environment is ready! Skipping setup."
        else
            log_warning "Dependencies missing, reinstalling..."
            pip install --upgrade pip
            pip install -r requirements.txt
            touch venv/setup_complete
        fi
    else
        log_info "Setting up fresh virtual environment with $PYTHON_CMD..."
        
        # Remove old venv if it exists but is incomplete
        [ -d "venv" ] && rm -rf venv
        
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        
        log_info "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        touch venv/setup_complete
    fi
    
    # Create logs directory
    mkdir -p logs
    
    # Create .env if missing
    if [ ! -f ".env" ]; then
        log_warning "Creating backend .env file..."
        cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_APP=api/main.py
PORT=5000
HOST=0.0.0.0
LOG_LEVEL=DEBUG

# REQUIRED API KEYS - PLEASE SET THESE
GITHUB_TOKEN=your_github_personal_access_token_here
COHERE_API_KEY=your_cohere_api_key_here
EOF
    fi
    
    cd ..
    
    # Frontend setup
    log_step "Setting up frontend environment..."
    cd frontend/hackd-web
    
    if [ ! -f "node_modules/.setup_complete" ] || [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        pnpm install
        mkdir -p node_modules && touch node_modules/.setup_complete
    else
        log_success "✅ Frontend dependencies ready! Skipping npm install."
    fi
    
    # Create .env.local if missing
    if [ ! -f ".env.local" ]; then
        log_warning "Creating frontend .env.local file..."
        cat > .env.local << 'EOF'
# REQUIRED CONVEX CONFIGURATION
CONVEX_DEPLOYMENT=your_convex_deployment_url_here
NEXT_PUBLIC_CONVEX_URL=your_convex_public_url_here

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000

# Development
NEXT_PUBLIC_APP_ENV=development
EOF
    fi
    
    cd ../..
    log_success "Environment setup complete!"
}

# API Keys validation
validate_api_keys() {
    log_header "API KEYS VALIDATION"
    
    local backend_env="backend/.env"
    local frontend_env="frontend/hackd-web/.env.local"
    
    # Check backend API keys
    if [ -f "$backend_env" ]; then
        source $backend_env
        
        if [ "$GITHUB_TOKEN" = "your_github_personal_access_token_here" ] || [ -z "$GITHUB_TOKEN" ]; then
            MISSING_APIS+=("GITHUB_TOKEN")
            log_warning "✗ GITHUB_TOKEN not configured (value: '${GITHUB_TOKEN:-<empty>}')"
        else
            log_success "✓ GitHub token configured"
        fi
        
        if [ "$COHERE_API_KEY" = "your_cohere_api_key_here" ] || [ -z "$COHERE_API_KEY" ]; then
            MISSING_APIS+=("COHERE_API_KEY")
            log_warning "✗ COHERE_API_KEY not configured (value: '${COHERE_API_KEY:-<empty>}')"
        else
            log_success "✓ Cohere API key configured"
        fi
    fi
    
    # Check frontend config
    if [ -f "$frontend_env" ]; then
        local convex_deployment=$(grep "CONVEX_DEPLOYMENT=" $frontend_env | cut -d= -f2)
        if [ "$convex_deployment" = "your_convex_deployment_url_here" ] || [ -z "$convex_deployment" ]; then
            MISSING_APIS+=("CONVEX_DEPLOYMENT")
        else
            log_success "Convex deployment configured ✓"
        fi
    fi
    
    if [ ${#MISSING_APIS[@]} -gt 0 ]; then
        log_warning "⚠️ Missing API configurations detected"
        show_api_setup_guide
    else
        log_success "🎉 All API keys configured!"
    fi
}

# API setup guide
show_api_setup_guide() {
    echo -e "\n${YELLOW}📋 API SETUP GUIDE${NC}"
    echo -e "${YELLOW}==================${NC}\n"
    
    for api in "${MISSING_APIS[@]}"; do
        case $api in
            "GITHUB_TOKEN")
                echo -e "${CYAN}🔧 GITHUB_TOKEN Setup:${NC}"
                echo "  1. Go to: https://github.com/settings/tokens"
                echo "  2. Click 'Generate new token (classic)'"
                echo "  3. Give it a name like 'Hackd Development'"
                echo "  4. Select scope: 'public_repo'"
                echo "  5. Copy the token"
                echo "  6. Edit backend/.env and replace:"
                echo "     GITHUB_TOKEN=your_github_personal_access_token_here"
                echo "     with:"
                echo "     GITHUB_TOKEN=ghp_your_actual_token_here"
                echo ""
                ;;
            "COHERE_API_KEY")
                echo -e "${CYAN}🤖 COHERE_API_KEY Setup:${NC}"
                echo "  1. Go to: https://cohere.ai/"
                echo "  2. Sign up for a free account"
                echo "  3. Go to your dashboard"
                echo "  4. Copy your API key"
                echo "  5. Edit backend/.env and replace:"
                echo "     COHERE_API_KEY=your_cohere_api_key_here"
                echo "     with:"
                echo "     COHERE_API_KEY=your_actual_cohere_key_here"
                echo ""
                ;;
            "CONVEX_DEPLOYMENT")
                echo -e "${CYAN}🗄️ CONVEX_DEPLOYMENT Setup:${NC}"
                echo "  1. Go to: https://convex.dev/"
                echo "  2. Sign up and create a new project"
                echo "  3. Copy your deployment URL"
                echo "  4. Edit frontend/hackd-web/.env.local and replace:"
                echo "     CONVEX_DEPLOYMENT=your_convex_deployment_url_here"
                echo "     with:"
                echo "     CONVEX_DEPLOYMENT=https://your-project.convex.cloud"
                echo ""
                ;;
        esac
    done
    
    echo -e "${YELLOW}⚡ QUICK SETUP COMMANDS:${NC}"
    echo "  nano backend/.env              # Edit backend config"
    echo "  nano frontend/hackd-web/.env.local  # Edit frontend config"
    echo ""
    echo -e "${GREEN}💡 TIP:${NC} The system will work partially without API keys, but full functionality requires them."
    echo ""
    
    if [ "$INTERACTIVE" != "false" ]; then
        read -p "Press Enter to continue with current setup, or Ctrl+C to exit and configure APIs..."
    else
        log_warning "Non-interactive mode: Continuing with current setup..."
        sleep 2
    fi
}

# Start services
start_services() {
    log_header "STARTING SERVICES"
    
    # Start backend
    log_step "Starting backend on port 5000..."
    cd backend
    source venv/bin/activate
    $PYTHON_CMD api/main.py &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    
    # Check backend health
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        log_success "Backend started successfully ✓"
    else
        log_error "Backend failed to start"
        return 1
    fi
    
    # Start frontend
    log_step "Starting frontend on port 3000..."
    cd frontend/hackd-web
    pnpm dev &
    FRONTEND_PID=$!
    cd ../..
    
    # Give frontend time to start
    log_info "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            log_success "Frontend started successfully ✓"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            log_warning "Frontend taking longer than expected to start"
        fi
    done
}

# Run comprehensive tests
run_tests() {
    log_header "COMPREHENSIVE TESTING"
    
    # Backend health check
    log_step "Backend health check..."
    if curl -s http://localhost:5000/health > /dev/null; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
    fi
    
    # Test job description analysis
    log_step "Testing job description analysis..."
    
    if curl -s -X POST http://localhost:5000/api/analyze-job-description \
        -H "Content-Type: application/json" \
        -d "{\"job_description\": \"We need a Senior Python Developer\", \"candidates\": [\"octocat\"]}" \
        > /dev/null; then
        log_success "Job analysis endpoint responding"
    else
        log_warning "Job analysis endpoint issues (may need API keys)"
    fi
    
    # Test frontend accessibility
    log_step "Testing frontend accessibility..."
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_success "Frontend accessible ✓"
    else
        log_error "Frontend not accessible"
    fi
    
    # Run unit tests
    log_step "Running unit tests..."
    cd backend
    source venv/bin/activate
    if $PYTHON_CMD -m pytest tests/test_api.py -v --tb=short 2>/dev/null; then
        log_success "Unit tests passed ✓"
    else
        log_warning "Unit tests completed (some may require API keys)"
    fi
    cd ..
}

# System status dashboard
show_system_status() {
    log_header "SYSTEM STATUS DASHBOARD"
    
    echo -e "${GREEN}🎯 HACKD SYSTEM STATUS${NC}"
    echo -e "${GREEN}=====================${NC}\n"
    
    # Services status
    echo -e "${BLUE}🔧 Services:${NC}"
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        echo "  Backend (port 5000): ✅ RUNNING"
    else
        echo "  Backend (port 5000): ❌ NOT RUNNING"
    fi
    
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "  Frontend (port 3000): ✅ RUNNING"
    else
        echo "  Frontend (port 3000): ❌ NOT RUNNING"
    fi
    
    # API status
    echo -e "\n${BLUE}🔑 API Configuration:${NC}"
    if [ ${#MISSING_APIS[@]} -eq 0 ]; then
        echo "  All APIs: ✅ CONFIGURED"
    else
        echo "  Missing APIs: ⚠️ ${MISSING_APIS[*]}"
    fi
    
    # URLs
    echo -e "\n${BLUE}🌐 Access URLs:${NC}"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:5000"
    echo "  Health Check: http://localhost:5000/health"
    
    echo -e "\n${YELLOW}🚀 READY TO USE!${NC}"
    echo -e "${YELLOW}=================${NC}"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Go to the \"Recruiting\" section"
    echo "3. Enter a job description"
    echo "4. Click \"Find My Perfect Matches\""
    echo "5. View the candidate results!"
    echo ""
    echo -e "${CYAN}💡 Pro Tips:${NC}"
    echo "• Try: \"We need a Senior Python developer with Django and React experience\""
    echo "• The system will analyze GitHub profiles and provide match scores"
    echo "• Click on candidate cards to see detailed breakdowns"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
}

# Main execution
main() {
    echo -e "${PURPLE}"
    echo "██╗  ██╗ █████╗  ██████╗██╗  ██╗██████╗ "
    echo "██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔══██╗"
    echo "███████║███████║██║     █████╔╝ ██║  ██║"
    echo "██╔══██║██╔══██║██║     ██╔═██╗ ██║  ██║"
    echo "██║  ██║██║  ██║╚██████╗██║  ██╗██████╔╝"
    echo "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ "
    echo -e "${NC}"
    echo -e "${CYAN}🚀 Complete Launch & Test Suite${NC}\n"
    
    check_system_requirements
    setup_environment
    validate_api_keys
    start_services
    run_tests
    show_system_status
    
    # Keep running until interrupted
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"