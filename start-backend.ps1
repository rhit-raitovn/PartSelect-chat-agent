Write-Host "Starting PartSelect AI Agent Backend..." -ForegroundColor Cyan
Set-Location backend
& .\venv\Scripts\Activate.ps1
python main.py
