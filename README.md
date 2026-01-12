# BakerySpotGourmet

A gourmet bakery management API built with FastAPI, adhering to strict architectural and security standards.

## Prerequisites

- **Python 3.11+**
- **Virtual Environment** (Recommended)

## Installation

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Environment Configuration:
   - Ensure the `.env` file is present in the root directory.
   - Default values are provided for development.

## Running the API

You can start the development server using the provided helper script or manually.

### Option 1: Helper Script (Recommended)

Run the PowerShell script which handles environment activation and PYTHONPATH:

```powershell
.\run_dev.ps1
```

### Option 2: Manual Execution

Ensure you are at the project root and run:

```powershell
.\.venv\Scripts\uvicorn backend.bakerySpotGourmet.main:app --reload
```

The API will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

To run the test suite:

```powershell
.\.venv\Scripts\python -m pytest
```

## Project Structure

This project follows a Clean / Hexagonal Architecture:

### Root Layout
- `/backend`: API, domain, services, infrastructure.
- `/frontend`: Web client (placeholder).

### Backend Details
- `backend/bakerySpotGourmet/api`: HTTP Layer (Controllers/Routers)
- `backend/bakerySpotGourmet/core`: Configuration, Logging, Exceptions
- `backend/bakerySpotGourmet/services`: Business Logic
- `backend/bakerySpotGourmet/repositories`: Data Access
- `backend/bakerySpotGourmet/domain`: Domain Models