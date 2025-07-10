# 🚀 Quick Start Guide (Manual Setup)

## ✅ **Current Status**
- Database server: ✅ Running  
- Backend dependencies: ✅ Installed
- Frontend dependencies: ✅ Installed
- Python packages: ⚠️ Partial (psycopg2 needs build tools)

## 🔧 **Next Steps**

### 1. Configure Backend Environment

Edit `backend\.env` with your database credentials:

```env
NODE_ENV=development
PORT=3001
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
FRONTEND_URL=http://localhost:3000
```

### 2. Create Database Schema

Since authentication is required, try one of these methods:

#### Option A: Use pgAdmin or another PostgreSQL client
1. Open pgAdmin or your preferred PostgreSQL client
2. Connect to your PostgreSQL server
3. Create a new database called `ecommerce_db`
4. Run the SQL script from `db\schema.sql`

#### Option B: Use command line with correct credentials
```powershell
# Replace 'your_username' with your actual PostgreSQL username
psql -U your_username -c "CREATE DATABASE ecommerce_db;"
psql -U your_username -d ecommerce_db -f "db\schema.sql"
```

#### Option C: Use localhost connection (if configured)
```powershell
psql -h localhost -d postgres -c "CREATE DATABASE ecommerce_db;"
psql -h localhost -d ecommerce_db -f "db\schema.sql"
```

### 3. Start the Applications

#### Terminal 1 - Backend:
```powershell
cd backend
npm run dev
```

#### Terminal 2 - Frontend:
```powershell
cd frontend  
npm start
```

### 4. Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **Health Check**: http://localhost:3001/health

## 🔧 **Troubleshooting**

### PostgreSQL Authentication Issues
If you're having trouble with PostgreSQL authentication:

1. **Check PostgreSQL configuration** in `pg_hba.conf`:
   - Usually located in: `C:\Program Files\PostgreSQL\XX\data\pg_hba.conf`
   - Look for lines with `localhost` and change `md5` to `trust` (for development only)

2. **Restart PostgreSQL service**:
   - Open Services (services.msc)
   - Find "postgresql-x64-XX" service
   - Right-click → Restart

3. **Use default credentials**:
   - Often PostgreSQL is installed with default user `postgres`
   - Check if you set a password during installation

### Python psycopg2 Issues (Optional)
If you want to use the Python data generator:

1. **Install Visual C++ Build Tools**: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. **Or use pre-compiled wheel**:
   ```powershell
   cd scripts
   pip install psycopg2-binary --no-deps --force-reinstall
   ```

## 🎉 **Without Python Data Generation**

The application will work perfectly fine without the Python data generator. You can:

1. **Use the application normally** - create users through the frontend
2. **Add sample data manually** through the web interface
3. **Skip the data generation step** entirely

The core application (backend + frontend) is fully functional!
