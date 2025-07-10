const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Joi = require('joi');
const { query, transaction } = require('../config/database');
const auth = require('../middleware/auth');
const { authorizeRoles } = require('../middleware/authorize');

const router = express.Router();

// Validation schemas
const userSchema = Joi.object({
    username: Joi.string().alphanum().min(3).max(50).required(),
    email: Joi.string().email().required(),
    password: Joi.string().min(6).required(),
    firstName: Joi.string().min(1).max(50).required(),
    lastName: Joi.string().min(1).max(50).required(),
    phone: Joi.string().optional(),
    dateOfBirth: Joi.date().optional(),
    role: Joi.string().valid('admin', 'staff', 'customer').default('customer')
});

const loginSchema = Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required()
});

const updateUserSchema = Joi.object({
    firstName: Joi.string().min(1).max(50).optional(),
    lastName: Joi.string().min(1).max(50).optional(),
    phone: Joi.string().optional(),
    dateOfBirth: Joi.date().optional(),
    role: Joi.string().valid('admin', 'staff', 'customer').optional()
});

// Register new user
router.post('/register', async (req, res) => {
    try {
        const { error, value } = userSchema.validate(req.body);
        if (error) {
            return res.status(400).json({ 
                success: false, 
                message: error.details[0].message 
            });
        }

        const { username, email, password, firstName, lastName, phone, dateOfBirth, role } = value;

        // Check if user already exists
        const existingUser = await query(
            'SELECT user_id FROM users WHERE email = $1 OR username = $2',
            [email, username]
        );

        if (existingUser.rows.length > 0) {
            return res.status(409).json({
                success: false,
                message: 'User with this email or username already exists'
            });
        }

        // Hash password
        const saltRounds = 12;
        const passwordHash = await bcrypt.hash(password, saltRounds);

        // Create user in transaction
        const result = await transaction(async (client) => {
            // Insert user
            const userResult = await client.query(`
                INSERT INTO users (username, email, password_hash, first_name, last_name, phone, date_of_birth, role)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING user_id, username, email, first_name, last_name, role, created_at
            `, [username, email, passwordHash, firstName, lastName, phone, dateOfBirth, role]);

            // Create shopping cart for the user
            await client.query(
                'INSERT INTO cart (user_id) VALUES ($1)',
                [userResult.rows[0].user_id]
            );

            return userResult.rows[0];
        });

        // Generate JWT token
        const token = jwt.sign(
            { 
                userId: result.user_id, 
                role: result.role,
                email: result.email 
            },
            process.env.JWT_SECRET,
            { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
        );

        res.status(201).json({
            success: true,
            message: 'User created successfully',
            data: {
                user: result,
                token
            }
        });

    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Login user
router.post('/login', async (req, res) => {
    try {
        const { error, value } = loginSchema.validate(req.body);
        if (error) {
            return res.status(400).json({
                success: false,
                message: error.details[0].message
            });
        }

        const { email, password } = value;

        // Find user
        const result = await query(`
            SELECT user_id, username, email, password_hash, first_name, last_name, role, is_active
            FROM users 
            WHERE email = $1
        `, [email]);

        if (result.rows.length === 0) {
            return res.status(401).json({
                success: false,
                message: 'Invalid credentials'
            });
        }

        const user = result.rows[0];

        if (!user.is_active) {
            return res.status(401).json({
                success: false,
                message: 'Account is deactivated'
            });
        }

        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password_hash);
        if (!isValidPassword) {
            return res.status(401).json({
                success: false,
                message: 'Invalid credentials'
            });
        }

        // Update last login
        await query(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = $1',
            [user.user_id]
        );

        // Generate JWT token
        const token = jwt.sign(
            { 
                userId: user.user_id, 
                role: user.role,
                email: user.email 
            },
            process.env.JWT_SECRET,
            { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
        );

        // Remove password hash from response
        delete user.password_hash;

        res.json({
            success: true,
            message: 'Login successful',
            data: {
                user,
                token
            }
        });

    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Get all users (admin only)
router.get('/', auth, authorizeRoles(['admin']), async (req, res) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        const offset = (page - 1) * limit;
        const search = req.query.search || '';
        const role = req.query.role || '';

        let whereClause = 'WHERE 1=1';
        const params = [];

        if (search) {
            whereClause += ' AND (first_name ILIKE $' + (params.length + 1) + ' OR last_name ILIKE $' + (params.length + 2) + ' OR email ILIKE $' + (params.length + 3) + ')';
            params.push(`%${search}%`, `%${search}%`, `%${search}%`);
        }

        if (role) {
            whereClause += ' AND role = $' + (params.length + 1);
            params.push(role);
        }

        // Get total count
        const countResult = await query(`
            SELECT COUNT(*) as total FROM users ${whereClause}
        `, params);

        // Get users
        const usersResult = await query(`
            SELECT user_id, username, email, first_name, last_name, phone, 
                   date_of_birth, role, is_active, created_at, last_login
            FROM users 
            ${whereClause}
            ORDER BY created_at DESC
            LIMIT $${params.length + 1} OFFSET $${params.length + 2}
        `, [...params, limit, offset]);

        const totalUsers = parseInt(countResult.rows[0].total);
        const totalPages = Math.ceil(totalUsers / limit);

        res.json({
            success: true,
            data: {
                users: usersResult.rows,
                pagination: {
                    currentPage: page,
                    totalPages,
                    totalUsers,
                    hasNextPage: page < totalPages,
                    hasPrevPage: page > 1
                }
            }
        });

    } catch (error) {
        console.error('Get users error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Get user profile
router.get('/profile', auth, async (req, res) => {
    try {
        const result = await query(`
            SELECT user_id, username, email, first_name, last_name, phone, 
                   date_of_birth, role, created_at, last_login
            FROM users 
            WHERE user_id = $1
        `, [req.user.userId]);

        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.json({
            success: true,
            data: { user: result.rows[0] }
        });

    } catch (error) {
        console.error('Get profile error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Update user
router.put('/:userId', auth, async (req, res) => {
    try {
        const { userId } = req.params;
        
        // Check if user can update this profile
        if (req.user.role !== 'admin' && req.user.userId !== userId) {
            return res.status(403).json({
                success: false,
                message: 'Access denied'
            });
        }

        const { error, value } = updateUserSchema.validate(req.body);
        if (error) {
            return res.status(400).json({
                success: false,
                message: error.details[0].message
            });
        }

        // Only admins can change roles
        if (value.role && req.user.role !== 'admin') {
            delete value.role;
        }

        const updateFields = Object.keys(value).map((key, index) => 
            `${key.replace(/([A-Z])/g, '_$1').toLowerCase()} = $${index + 1}`
        ).join(', ');

        if (updateFields.length === 0) {
            return res.status(400).json({
                success: false,
                message: 'No valid fields to update'
            });
        }

        const result = await query(`
            UPDATE users 
            SET ${updateFields}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $${Object.keys(value).length + 1}
            RETURNING user_id, username, email, first_name, last_name, phone, 
                     date_of_birth, role, updated_at
        `, [...Object.values(value), userId]);

        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.json({
            success: true,
            message: 'User updated successfully',
            data: { user: result.rows[0] }
        });

    } catch (error) {
        console.error('Update user error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Deactivate user (admin only)
router.patch('/:userId/deactivate', auth, authorizeRoles(['admin']), async (req, res) => {
    try {
        const { userId } = req.params;

        const result = await query(`
            UPDATE users 
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
            RETURNING user_id, username, email, is_active
        `, [userId]);

        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.json({
            success: true,
            message: 'User deactivated successfully',
            data: { user: result.rows[0] }
        });

    } catch (error) {
        console.error('Deactivate user error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Get user statistics (admin/staff only)
router.get('/stats', auth, authorizeRoles(['admin', 'staff']), async (req, res) => {
    try {
        const statsResult = await query(`
            SELECT 
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE role = 'admin') as admin_count,
                COUNT(*) FILTER (WHERE role = 'staff') as staff_count,
                COUNT(*) FILTER (WHERE role = 'customer') as customer_count,
                COUNT(*) FILTER (WHERE is_active = true) as active_users,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as new_users_last_30_days,
                COUNT(*) FILTER (WHERE last_login >= CURRENT_DATE - INTERVAL '7 days') as active_last_7_days
            FROM users
        `);

        res.json({
            success: true,
            data: { stats: statsResult.rows[0] }
        });

    } catch (error) {
        console.error('Get user stats error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

module.exports = router;
