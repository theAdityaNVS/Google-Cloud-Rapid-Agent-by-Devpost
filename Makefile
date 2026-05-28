# ==============================================================================
# ErgoFlow AI - Multi-Service Developer Makefile
# ==============================================================================
# Detect OS and set appropriate virtual environment executables
ifeq ($(OS),Windows_NT)
    VENV_PYTHON = venv\Scripts\python
    VENV_PIP = venv\Scripts\pip
    GLOBAL_PYTHON = python
    RM_DIR = rmdir /s /q
else
    VENV_PYTHON = venv/bin/python
    VENV_PIP = venv/bin/pip
    GLOBAL_PYTHON = python3
    RM_DIR = rm -rf
endif

.PHONY: help install install-backend install-frontend seed run run-backend run-frontend mcp-local clean

# ------------------------------------------------------------------------------
# Help Screen (Default Target)
# ------------------------------------------------------------------------------
help:
	@echo "=============================================================================="
	@echo "                    🪑 ErgoFlow AI - Development Commands                    "
	@echo "=============================================================================="
	@echo "Available commands:"
	@echo "  make install         - Set up both backend (venv) & frontend dependencies"
	@echo "  make seed            - Seed MongoDB Atlas with developer baseline telemetry"
	@echo "  make run             - Run both Backend & Frontend concurrently (Parallel)"
	@echo "  make run-backend     - Run FastAPI backend service only (http://localhost:8000)"
	@echo "  make run-frontend    - Run Next.js frontend client only (http://localhost:3000)"
	@echo "  make mcp-local       - Run local MongoDB MCP server (port 8080)"
	@echo "  make clean           - Remove virtual envs, node_modules, and cache files"
	@echo "=============================================================================="

# ------------------------------------------------------------------------------
# Installation & Setup
# ------------------------------------------------------------------------------
install: install-backend install-frontend
	@echo "✅ Full environment setup complete!"

backend/.env:
	@echo "📋 Creating backend/.env from .env.example..."
	@$(GLOBAL_PYTHON) -c "import os, shutil; shutil.copy2('backend/.env.example', 'backend/.env') if not os.path.exists('backend/.env') else print('backend/.env already exists')"

install-backend: backend/.env
	@echo "🐍 Setting up Python virtual environment & installing backend dependencies..."
	@cd backend && $(GLOBAL_PYTHON) -m venv venv
	@cd backend && $(VENV_PIP) install --upgrade pip
	@cd backend && $(VENV_PIP) install -r requirements.txt
	@echo "✅ Backend setup complete!"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ Frontend setup complete!"

# ------------------------------------------------------------------------------
# Database Operations
# ------------------------------------------------------------------------------
seed:
	@echo "🌱 Seeding MongoDB Atlas and establishing collection indexes..."
	@cd backend && $(VENV_PYTHON) -m app.utils.seed_data
	@echo "✅ Database seeding complete!"

# ------------------------------------------------------------------------------
# Running Services
# ------------------------------------------------------------------------------
# Parallel target to run both backend and frontend simultaneously
run:
	@echo "🚀 Starting both ErgoFlow AI Backend and Frontend concurrently..."
	@$(MAKE) -j 2 run-backend run-frontend

run-backend:
	@echo "🔥 Starting FastAPI Backend server on http://localhost:8000..."
	@cd backend && $(VENV_PYTHON) run.py

run-frontend:
	@echo "⚡ Starting Next.js Frontend client on http://localhost:3000..."
	@cd frontend && npm run dev

# ------------------------------------------------------------------------------
# MCP Server Actions
# ------------------------------------------------------------------------------
mcp-local:
	@echo "🔌 Starting MongoDB MCP Server locally on port 8080..."
	@npx -y mongodb-mcp-server@latest

# ------------------------------------------------------------------------------
# Cleaning & Resetting
# ------------------------------------------------------------------------------
clean:
	@echo "🧹 Cleaning up project artifacts..."
	@$(GLOBAL_PYTHON) -c "import os, shutil; [shutil.rmtree(os.path.join(p, 'node_modules'), ignore_errors=True) for p in ['.', 'frontend', 'mcp-server']]"
	@$(GLOBAL_PYTHON) -c "import os, shutil; [shutil.rmtree(os.path.join(p, '.next'), ignore_errors=True) for p in ['.', 'frontend']]"
	@$(GLOBAL_PYTHON) -c "import os, shutil; shutil.rmtree('backend/venv', ignore_errors=True)"
	@$(GLOBAL_PYTHON) -c "import os, shutil; [shutil.rmtree(os.path.join(r, d), ignore_errors=True) for r, ds, fs in os.walk('.') for d in ds if d == '__pycache__']"
	@echo "✨ Project cleaned!"
