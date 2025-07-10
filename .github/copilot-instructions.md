<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Database Administration Project Instructions

This is a comprehensive database administration project for an e-commerce platform.

## Project Context
- **Database**: PostgreSQL with comprehensive e-commerce schema
- **Backend**: Node.js + Express.js for API and user management
- **Frontend**: React.js for administrative interface
- **Scripts**: Python for data generation and automation

## Code Generation Guidelines
1. **Database Operations**: Use parameterized queries and connection pooling
2. **RBAC**: Implement PostgreSQL roles with proper privilege separation
3. **Performance**: Include query optimization, indexing, and timing measurements
4. **Security**: Hash passwords, validate inputs, use environment variables
5. **Error Handling**: Comprehensive error handling and logging
6. **Documentation**: Include performance metrics and optimization explanations

## Technologies Used
- PostgreSQL 14+
- Node.js 18+ with Express.js
- React.js with modern hooks
- Python 3.9+ with Faker, psycopg2
- bcryptjs for password hashing
- jsonwebtoken for authentication
- pg for PostgreSQL connections

## File Organization
- Keep database scripts in `/db/`
- Backend API routes in `/backend/routes/`
- Frontend components in `/frontend/src/components/`
- Python automation in `/scripts/`
