# PartSelect AI Agent - Windows Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PartSelect AI Agent - Setup         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/8] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
    
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "  Python 3.11+ required. Please upgrade Python." -ForegroundColor Red
            exit 1
        }
    }
}
catch {
    Write-Host "  Python not found. Please install Python 3.11+." -ForegroundColor Red
    exit 1
}

# Check Node.js version
Write-Host "[2/8] Checking Node.js version..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "  Node.js not found. Please install Node.js 16+." -ForegroundColor Red
    exit 1
}

# Backend Setup
Write-Host "[3/8] Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
Write-Host "  Creating virtual environment..." -ForegroundColor Gray
python -m venv venv
if (-not $?) {
    Write-Host "  Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
pip install --upgrade pip
pip install -r requirements.txt
if (-not $?) {
    Write-Host "  Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "  Backend dependencies installed" -ForegroundColor Green

# Initialize vector database
Write-Host "[5/8] Initializing vector database..." -ForegroundColor Yellow
python scripts/setup_vector_db.py
if ($?) {
    Write-Host "  Vector database initialized" -ForegroundColor Green
}
else {
    Write-Host "  Failed to initialize vector database" -ForegroundColor Red
    exit 1
}

# Frontend Setup
Write-Host "[6/8] Setting up frontend..." -ForegroundColor Yellow
Set-Location ../frontend

# Install npm dependencies
Write-Host "  Installing Node.js dependencies..." -ForegroundColor Gray
npm install
if (-not $?) {
    Write-Host "  Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "  Frontend dependencies installed" -ForegroundColor Green

# Create frontend .env
if (-not (Test-Path ".env")) {
    "REACT_APP_API_URL=http://localhost:8000" | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "  Created frontend .env file" -ForegroundColor Green
}

Set-Location ..

# Create startup scripts
Write-Host "[7/8] Creating startup scripts..." -ForegroundColor Yellow

# Backend start script
$backendScript = @"
Write-Host "Starting PartSelect AI Agent Backend..." -ForegroundColor Cyan
Set-Location backend
& .\venv\Scripts\Activate.ps1
python main.py
"@
$backendScript | Out-File -FilePath "start-backend.ps1" -Encoding utf8

# Frontend start script
$frontendScript = @"
Write-Host "Starting PartSelect AI Agent Frontend..." -ForegroundColor Cyan
Set-Location frontend
npm start
"@
$frontendScript | Out-File -FilePath "start-frontend.ps1" -Encoding utf8

# Combined start script
$startAllScript = @"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PartSelect AI Agent - Starting      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start-backend.ps1"

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start-frontend.ps1"

Write-Host ""
Write-Host "Services starting..." -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop all services..."
`$null = `$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop services
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
"@
$startAllScript | Out-File -FilePath "start-all.ps1" -Encoding utf8

Write-Host "  Startup scripts created" -ForegroundColor Green

# Final instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Setup Complete!                     " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure your DeepSeek API key is set in backend\.env" -ForegroundColor White
Write-Host "  2. Run the application:" -ForegroundColor White
Write-Host ""
Write-Host "     .\start-all.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Or start services separately:" -ForegroundColor White
Write-Host "     .\start-backend.ps1   # Start backend only" -ForegroundColor Gray
Write-Host "     .\start-frontend.ps1  # Start frontend only" -ForegroundColor Gray
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""