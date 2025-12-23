#!/bin/bash

# EVTX Enterprise Application Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    EVTX Enterprise Application${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.12+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Found Python version: $PYTHON_VERSION"
    
    # Check if Python version is 3.12 or higher
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 12) else 1)'; then
        print_status "Python version meets requirements (3.12+)"
    else
        print_warning "Python version is below 3.12. Some features may not work correctly."
    fi
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        print_status "Virtual environment created successfully."
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated."
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    print_status "Dependencies installed successfully."
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating default one..."
        cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///evtx_enterprise.db
FLASK_ENV=development
EOF
        print_status "Default .env file created with random secret key."
    else
        print_status ".env file found."
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p uploads converted
    print_status "Directories created successfully."
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    python3 -c "from app import create_app; app = create_app(); app.app_context().push(); from models import db; db.create_all(); print('Database initialized successfully.')"
    print_status "Database initialized successfully."
}

# Start the application
start_app() {
    print_status "Starting EVTX Enterprise application..."
    print_status "Application will be available at: http://localhost:5000"
    print_status "Default admin credentials: admin / admin123"
    print_status "Press Ctrl+C to stop the application"
    echo
    python3 app.py
}

# Main execution
main() {
    print_header
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    check_python
    check_venv
    activate_venv
    install_dependencies
    check_env_file
    create_directories
    init_database
    start_app
}

# Handle script interruption
trap 'print_status "Shutting down application..."; exit 0' INT

# Run main function
main "$@"
