# 🔐 Demo Login Credentials

This document contains working login credentials for testing the Database Administration System.

## 🚀 Quick Access

### 🎯 Primary Test Accounts (Always Available)

| Role | Email | Username | Password | Access Level |
|------|-------|----------|----------|--------------|
| **Admin** | `admin@example.com` | `admin` | `admin123` | Full Access |
| **Staff** | `staff@example.com` | `staff1` | `staff123` | Limited Access |
| **Customer** | `customer@example.com` | `customer1` | `customer123` | Basic Access |

## 📋 Account Details

### 👑 Admin Account (Full System Access)
**Primary Admin Account:**
- **Email**: `admin@example.com`
- **Username**: `admin`  
- **Password**: `admin123`
- **Access**: Complete system control

**Features Available:**
- ✅ User Management (Create/Edit/Delete users)
- ✅ Database Operations (Backup/Restore)
- ✅ Analytics Dashboard
- ✅ SQL Query Console (SELECT, EXPLAIN)
- ✅ Performance Monitoring
- ✅ System Configuration

### 👤 Staff Account (Limited Access)
**Primary Staff Account:**
- **Email**: `staff@example.com`
- **Username**: `staff1`
- **Password**: `staff123`
- **Access**: Read-only operations

**Features Available:**
- ✅ View Analytics Dashboard
- ✅ Execute SELECT queries only
- ✅ View user information (limited)
- ✅ Access performance metrics
- ❌ Cannot modify users or system settings

### 🛒 Customer Account (Basic Access)
**Primary Customer Account:**
- **Email**: `customer@example.com`
- **Username**: `customer1`
- **Password**: `customer123`
- **Access**: Basic profile only

**Features Available:**
- ✅ Basic login access
- ❌ No administrative features
- ❌ Used primarily for user management testing

## 🔧 How to Login

1. **Access the system**: Navigate to `http://localhost:3000`
2. **Use email format**: Enter the full email address (not username)
3. **Choose your test scenario**:
   - **Admin testing**: Use `admin@example.com` / `admin123`
   - **Staff testing**: Use `staff@example.com` / `staff123`
   - **Customer testing**: Use `customer@example.com` / `customer123`
4. **Role verification**: Check the dashboard to confirm your access level

## 📊 System Statistics

- **Core Test Users**: 3 accounts (admin, staff, customer)
- **Additional Data**: Database reinitialized with clean schema
- **Database**: PostgreSQL with complete e-commerce schema
- **System Status**: ✅ Ready for evaluation

## 🛡️ Security Notes

- **Development Environment**: These are test credentials for evaluation only
- **Password Policy**: In production, enforce strong password requirements
- **Account Management**: Admin account can create additional users through the interface
- **Role-Based Access**: System enforces proper permission levels

## ✅ Verified Features

All accounts have been tested and verified to work with:
- ✅ Authentication system
- ✅ Role-based access control  
- ✅ Database operations
- ✅ Analytics dashboard
- ✅ Query execution
- ✅ User management interface

---

**Last Updated**: June 29, 2025  
**System Status**: ✅ All credentials verified and working
**Database Status**: ✅ Fresh schema with core test accounts
