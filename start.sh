#!/bin/bash

# Finance RAG Application Startup Script
# This script sets up and runs the finance RAG application on a completely new machine

set -e  # Exit on any error

# Default model
DEFAULT_MODEL="llama3.1:latest"
MODEL=${1:-$DEFAULT_MODEL}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [MODEL_NAME]"
    echo ""
    echo "Arguments:"
    echo "  MODEL_NAME    The Ollama model to use (default: $DEFAULT_MODEL)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use default model ($DEFAULT_MODEL)"
    echo "  $0 llama3.1:latest    # Use Llama 3.1"
    echo "  $0 llama3.2:latest    # Use Llama 3.2"
    echo "  $0 mistral:latest     # Use Mistral"
    echo "  $0 codellama:latest   # Use Code Llama"
    echo ""
    echo "Available models can be found at: https://ollama.ai/library"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python if not present
install_python() {
    if command_exists python3; then
        print_success "Python 3 is already installed"
        return
    fi
    
    print_status "Installing Python 3..."
    
    OS=$(detect_os)
    if [[ "$OS" == "macos" ]]; then
        if command_exists brew; then
            brew install python3
        else
            print_error "Homebrew not found. Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-pip
        else
            print_error "Unsupported package manager. Please install Python 3 manually."
            exit 1
        fi
    else
        print_error "Unsupported operating system. Please install Python 3 manually."
        exit 1
    fi
    
    print_success "Python 3 installed successfully"
}

# Function to install Ollama if not present
install_ollama() {
    if command_exists ollama; then
        print_success "Ollama is already installed"
        return
    fi
    
    print_status "Installing Ollama..."
    
    OS=$(detect_os)
    if [[ "$OS" == "macos" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_error "Unsupported operating system. Please install Ollama manually: https://ollama.ai/"
        exit 1
    fi
    
    print_success "Ollama installed successfully"
}

# Function to start Ollama service
start_ollama() {
    print_status "Starting Ollama service..."
    
    if ! pgrep -x "ollama" > /dev/null; then
        ollama serve &
        sleep 3  # Wait for Ollama to start
    fi
    
    print_success "Ollama service is running"
}

# Function to pull the required model
pull_model() {
    print_status "Pulling model: $MODEL (this may take a while)..."
    
    if ollama list | grep -q "$MODEL"; then
        print_success "Model $MODEL is already available"
    else
        print_status "Downloading model $MODEL from Ollama library..."
        ollama pull "$MODEL"
        print_success "Model $MODEL pulled successfully"
    fi
}

# Function to create and activate virtual environment
setup_virtual_environment() {
    print_status "Setting up Python virtual environment..."
    
    if [[ -d "finance_rag_venv" ]]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf finance_rag_venv
    fi
    
    python3 -m venv finance_rag_venv
    print_success "Virtual environment created"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    source finance_rag_venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed successfully"
}

# Function to check environment variables
check_environment() {
    print_status "Checking environment setup..."
    
    # Check if .env file exists, create if not
    if [[ ! -f ".env" ]]; then
        print_warning ".env file not found. Creating a basic one..."
        cat > .env << EOF
# LangSmith API Key (optional - for tracing and monitoring)
# LANGCHAIN_API_KEY=your_langsmith_api_key_here
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=finance-rag

# Model configuration
OLLAMA_MODEL=$MODEL

# Other environment variables can be added here
EOF
        print_success ".env file created"
    else
        # Update .env file with the current model if it doesn't have it
        if ! grep -q "OLLAMA_MODEL" .env; then
            echo "OLLAMA_MODEL=$MODEL" >> .env
            print_success "Added model configuration to .env file"
        else
            # Update existing OLLAMA_MODEL line
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS requires different sed syntax
                sed -i '' "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" .env
            else
                # Linux sed syntax
                sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" .env
            fi
            print_success "Updated model configuration in .env file"
        fi
    fi
}

# Function to run the application
run_application() {
    print_status "Starting Finance RAG Application with model: $MODEL"
    print_status "Make sure you have the necessary knowledge base files in the project directory."
    
    source finance_rag_venv/bin/activate
    python app.py
}

# Handle script interruption
cleanup() {
    print_error "Setup interrupted. Cleaning up..."
    exit 1
}

trap cleanup INT TERM

# Main execution
main() {
    echo "🚀 Finance RAG Application Setup"
    echo "================================="
    echo ""
    
    # Show help if requested
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check if we're in the right directory
    if [[ ! -f "app.py" ]] || [[ ! -f "requirements.txt" ]]; then
        print_error "Please run this script from the finance-rag project directory"
        exit 1
    fi
    
    print_status "Using model: $MODEL"
    echo ""
    
    # Install system dependencies
    install_python
    install_ollama
    
    # Start Ollama service
    start_ollama
    
    # Pull the required model
    pull_model
    
    # Setup Python environment
    setup_virtual_environment
    install_dependencies
    
    # Check environment
    check_environment
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    print_status "Starting the application..."
    echo ""
    
    # Run the application
    run_application
}

# Run main function
main "$@" 