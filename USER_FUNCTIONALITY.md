# 👥 User Functionality Guide
## E-Commerce Database Administration Platform

This document outlines the specific functionalities available to each user role in the system.

---

## 🔒 **Admin Users**

### **Account Access**
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: `admin`

### **👥 User Management**
✅ **View All Users**
- Access complete user directory with pagination
- Search users by name or email address
- Filter users by role (admin/staff/customer)
- View comprehensive user details:
  - User ID, username, email
  - Full name and contact information
  - Account status (active/inactive)
  - Registration date and last login
  - User role and permissions

✅ **User Statistics Dashboard**
- Total registered users count
- User breakdown by role (admin/staff/customer)
- Active vs inactive user metrics
- New user registrations (last 30 days)
- User activity metrics (last 7 days)

✅ **User Profile Management**
- Edit any user's profile information
- Update names, phone numbers, birth dates
- **Change user roles** (admin exclusive privilege)
- Activate or deactivate user accounts
- View user activity history

### **🛡️ Administrative Privileges**
✅ **System Access Control**
- Access all admin-only API endpoints
- Manage user permissions and roles
- Override user access restrictions

✅ **Database Operations**
- Full read/write access to user data
- Execute administrative queries
- Access system performance metrics

### **📊 Reporting & Analytics**
✅ **User Analytics**
- Registration trends and patterns
- User engagement statistics
- Role distribution reports
- Account activity monitoring

---

## 👤 **Staff Users**

### **Account Access**
- **Email**: `staff@example.com`
- **Password**: `staff123`
- **Role**: `staff`

### **📊 Limited Analytics Access**
✅ **User Statistics**
- View user count and basic statistics
- Access user activity reports
- Monitor customer engagement metrics

✅ **Profile Management**
- Edit their own profile information
- Update personal details and contact info
- View their own activity history

### **🚫 Restrictions**
- Cannot change user roles
- Cannot access admin-only endpoints
- Cannot modify other users' accounts
- Limited to read-only user statistics

---

## 🛒 **Customer Users**

### **Account Access**
- **Email**: `customer@example.com`
- **Password**: `customer123`
- **Role**: `customer`

### **👤 Personal Account Management**
✅ **Profile Access**
- View their own profile information
- Edit personal details (name, phone, etc.)
- Update contact information
- View account activity history

### **🔐 Authentication**
✅ **Secure Login**
- JWT token-based authentication
- Password-protected account access
- Secure session management

### **🚫 Restrictions**
- Cannot access other users' data
- Cannot view system statistics
- Cannot access admin or staff functions
- Limited to personal account management only

---

## 🔍 **Common Features (All Users)**

### **🔐 Authentication System**
✅ **Secure Login**
- Email and password authentication
- JWT token generation and validation
- Session management and timeout
- Password security with bcrypt hashing

✅ **Profile Management**
- Update personal information
- Change contact details
- View account activity

### **🛡️ Security Features**
✅ **Data Protection**
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention
- Rate limiting and security headers

---

## 🌐 **API Endpoints Available**

### **Authentication Endpoints**
- `POST /api/users/login` - User login
- `POST /api/users/register` - New user registration

### **User Management Endpoints**
- `GET /api/users` - List users (Admin only)
- `GET /api/users/profile` - Get own profile (All users)
- `PUT /api/users/:userId` - Update user (Admin or own profile)
- `GET /api/users/stats` - User statistics (Admin/Staff only)

### **Security & Authorization**
- JWT token required for protected endpoints
- Role-based authorization middleware
- Input validation with Joi schemas

---

## 🚀 **Getting Started**

### **1. Login to Your Account**
```bash
# Test login API
curl -X POST http://localhost:3001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### **2. Access Your Dashboard**
- Backend API: http://localhost:3001
- Frontend Interface: http://localhost:3000 (when running)

### **3. Explore Your Permissions**
Use the JWT token from login to access role-specific endpoints.

---

## 🔮 **Future Enhancements** (Not Yet Implemented)

### **E-Commerce Features**
- 🛍️ Product catalog management
- 📦 Order processing and tracking  
- 💳 Payment processing integration
- 📊 Sales analytics and reporting
- 📋 Inventory management
- 🚚 Shipping and logistics

### **Advanced Admin Features**
- 🗑️ User account deletion
- 📝 Audit logging and activity tracking
- 📊 Advanced dashboard with charts
- 🔔 System notifications and alerts
- ⚙️ System configuration management
- 📈 Performance monitoring tools

### **Enhanced User Experience**
- 📱 Mobile-responsive interface
- 🌙 Dark/light theme toggle
- 🔍 Advanced search and filtering
- 📧 Email notifications
- 🔄 Real-time updates
- 💬 In-app messaging system

---

## 📞 **Support**

For technical issues or questions about user functionality:
1. Check the API documentation in `/backend/routes/`
2. Review the database schema in `/db/schema.sql`
3. Test functionality using the provided test scripts
4. Review error logs for troubleshooting

---

**Last Updated**: June 27, 2025
**System Version**: 1.0.0
**Database**: PostgreSQL with ecommerce_db
