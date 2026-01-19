$ErrorActionPreference = "Stop"

# Activate virtual environment if not already active
if (-not (Get-Command "uvicorn" -ErrorAction SilentlyContinue)) {
    Write-Host "Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
}

# Add current directory and backend to PYTHONPATH to ensure package resolution works
$env:PYTHONPATH = "$PWD;$PWD\backend"

Write-Host "Starting BakerySpotGourmet API..."
Write-Host "Swagger UI: http://127.0.0.1:8000/docs"

# Run with uvicorn
# --reload: Auto-reload on code changes
# --host 127.0.0.1: Localhost
# --port 8000: Standard port
uvicorn bakerySpotGourmet.main:app --reload --host 127.0.0.1 --port 8000
