@echo off
echo ================================
echo  E-Commerce DB Setup Script
echo ================================
echo.

REM Check if PostgreSQL is running
pg_isready >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ PostgreSQL is not running. Please start PostgreSQL service first.
    echo.
    echo To start PostgreSQL on Windows:
    echo 1. Open Services (services.msc)
    echo 2. Find "postgresql-x64-XX" service
    echo 3. Right-click and select "Start"
    echo.
    pause
    exit /b 1
)

echo ✅ PostgreSQL is running

REM Navigate to project directory
cd /d "%~dp0"

echo.
echo 📊 Setting up database...
echo.
echo Please enter your PostgreSQL credentials:
set /p DB_USER="PostgreSQL username (default: postgres): "
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_NAME="Database name (default: ecommerce_db): "
if "%DB_NAME%"=="" set DB_NAME=ecommerce_db

echo.
echo Creating database %DB_NAME%...
psql -U %DB_USER% -c "CREATE DATABASE %DB_NAME%;" 2>nul
if %ERRORLEVEL% equ 0 (
    echo ✅ Database created successfully
) else (
    echo ⚠️ Database might already exist or creation failed
)

echo.
echo 📄 Running database schema...
psql -U %DB_USER% -d %DB_NAME% -f "db\schema.sql"
if %ERRORLEVEL% equ 0 (
    echo ✅ Database schema created successfully
) else (
    echo ❌ Failed to create database schema
    pause
    exit /b 1
)

echo.
echo 🔧 Setting up backend...
cd backend
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul
    echo ✅ Environment file created
)

echo Installing backend dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

echo ✅ Backend setup complete

echo.
echo 🎨 Setting up frontend...
cd ..\frontend
echo Installing frontend dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo ✅ Frontend setup complete

echo.
echo 🐍 Setting up Python scripts...
cd ..\scripts
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo ✅ Python setup complete

cd ..

echo.
echo ========================================
echo  🎉 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend\.env with your database credentials
echo 2. Run: npm run dev (in backend folder)
echo 3. Run: npm start (in frontend folder)
echo 4. Optional: python data_generator.py (in scripts folder)
echo.
echo Access your application:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:3001
echo.
pause
