# Database Setup Guide

## Prerequisites
- PostgreSQL 14+
- Node.js 18+
- Python 3.9+
- npm or yarn

## Quick Setup

### 1. Database Setup
```bash
# Create database
createdb ecommerce_db

# Run schema
psql -d ecommerce_db -f db/schema.sql

# Generate sample data (optional)
cd scripts
pip install -r requirements.txt
python data_generator.py
```

### 2. Backend Setup
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your database credentials
npm start
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Environment Variables

Create `.env` files in the backend directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret
```

## Default Admin Account
- Email: `admin@ecommerce.com`
- Password: `admin123`

## Development Commands

### Backend
- `npm start` - Start server
- `npm run dev` - Start with nodemon
- `npm test` - Run tests

### Frontend
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests

### Database
- `python db/backup.py` - Create backup
- `python db/restore.py --list` - List backups
- `python scripts/data_generator.py` - Generate test data

## Performance Testing

### Run Complex Queries
```sql
-- Execute queries from db/queries.sql
psql -d ecommerce_db -f db/queries.sql
```

### Monitor Performance
```sql
-- Enable query timing
\timing

-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC;
```

## Backup and Recovery

### Create Backup
```bash
python db/backup.py --type full
```

### Restore from Backup
```bash
python db/restore.py --latest
```

## RBAC Testing

### Test Different Roles
1. Admin: Full access to all features
2. Staff: Limited admin access, cannot manage other admins
3. Customer: Basic access, profile management only

### Database Roles
- `db_admin`: Full database access
- `db_staff`: Limited table access
- `db_customer`: Read-only access to own data

## Troubleshooting

### Common Issues
1. **Database connection failed**: Check PostgreSQL is running and credentials are correct
2. **Permission denied**: Ensure user has proper database privileges
3. **Port conflicts**: Make sure ports 3000 (frontend) and 3001 (backend) are available

### Performance Issues
1. Run `ANALYZE` on tables after data generation
2. Check index usage with `pg_stat_user_indexes`
3. Monitor query plans with `EXPLAIN ANALYZE`

## Production Deployment

### Database Optimization
- Enable connection pooling
- Configure shared_buffers (25% of RAM)
- Set work_mem appropriately
- Enable query plan caching

### Security
- Use SSL connections
- Implement proper firewall rules
- Regular security updates
- Monitor failed login attempts

### Monitoring
- Set up automated backups
- Monitor disk space
- Track query performance
- Set up alerting for errors
