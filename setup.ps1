# E-Commerce Database Project - Quick Start Script

Write-Host "================================" -ForegroundColor Cyan
Write-Host " E-Commerce DB Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is running
try {
    $pgStatus = pg_isready
    Write-Host "[OK] PostgreSQL is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] PostgreSQL is not running. Please start PostgreSQL service first." -ForegroundColor Red
    Write-Host ""
    Write-Host "To start PostgreSQL on Windows:" -ForegroundColor Yellow
    Write-Host "1. Open Services (services.msc)" -ForegroundColor Yellow
    Write-Host "2. Find 'postgresql-x64-XX' service" -ForegroundColor Yellow
    Write-Host "3. Right-click and select 'Start'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Navigate to project directory
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "[INFO] Setting up database..." -ForegroundColor Yellow
Write-Host ""

# Get database credentials
$DB_USER = Read-Host "PostgreSQL username (default: postgres)"
if ([string]::IsNullOrEmpty($DB_USER)) { $DB_USER = "postgres" }

$DB_NAME = Read-Host "Database name (default: ecommerce_db)"
if ([string]::IsNullOrEmpty($DB_NAME)) { $DB_NAME = "ecommerce_db" }

Write-Host ""
Write-Host "Creating database $DB_NAME..." -ForegroundColor Yellow

# Create database
try {
    $result = psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>&1
    Write-Host "[OK] Database created successfully" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Database might already exist or creation failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[INFO] Running database schema..." -ForegroundColor Yellow

# Run schema
try {
    psql -U $DB_USER -d $DB_NAME -f "db\schema.sql"
    Write-Host "[OK] Database schema created successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create database schema" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Setting up backend..." -ForegroundColor Yellow

Set-Location "backend"

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Environment file created" -ForegroundColor Green
}

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
try {
    npm install
    Write-Host "[OK] Backend setup complete" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install backend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Setting up frontend..." -ForegroundColor Yellow

Set-Location "..\frontend"

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
try {
    npm install
    Write-Host "[OK] Frontend setup complete" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install frontend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Setting up Python scripts..." -ForegroundColor Yellow

Set-Location "..\scripts"

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "[OK] Python setup complete" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location ".."

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env with your database credentials" -ForegroundColor White
Write-Host "2. Run: npm run dev (in backend folder)" -ForegroundColor White
Write-Host "3. Run: npm start (in frontend folder)" -ForegroundColor White
Write-Host "4. Optional: python data_generator.py (in scripts folder)" -ForegroundColor White
Write-Host ""

Write-Host "Access your application:" -ForegroundColor Cyan
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "- Backend API: http://localhost:3001" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"
