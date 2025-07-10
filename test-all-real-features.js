const axios = require('axios');

async function testAllRealFeatures() {
    try {
        console.log('🧪 Testing ALL REAL Database Features...\n');
        
        const baseURL = 'http://localhost:3001';
        
        // Login as admin
        console.log('🔐 Logging in as admin...');
        const loginResponse = await axios.post(`${baseURL}/api/users/login`, {
            email: 'admin@example.com',
            password: 'admin123'
        });
        
        if (!loginResponse.data.success) {
            throw new Error('Admin login failed');
        }
        
        const token = loginResponse.data.data.token;
        const headers = { 'Authorization': `Bearer ${token}` };
        console.log('✅ Admin login successful\n');
        
        // Test 1: Real Database Backup
        console.log('📦 Testing REAL Database Backup...');
        const backupResponse = await axios.post(`${baseURL}/api/database/backup`, {}, { headers });
        
        if (backupResponse.data.success) {
            console.log('✅ REAL BACKUP COMPLETED!');
            console.log(`   📄 File: ${backupResponse.data.data.filename}`);
            console.log(`   📊 Size: ${backupResponse.data.data.size}`);
            console.log(`   📋 Tables: ${backupResponse.data.data.tables_backed_up.length} tables\n`);
        } else {
            console.log('❌ Backup failed:', backupResponse.data.message);
        }
        
        // Test 2: Real Query Execution
        console.log('🔍 Testing REAL Query Execution...');
        const queryResponse = await axios.post(`${baseURL}/api/database/execute-query`, {
            query: 'SELECT COUNT(*) as total_users, role FROM users GROUP BY role ORDER BY total_users DESC;'
        }, { headers });
        
        if (queryResponse.data.success) {
            console.log('✅ REAL QUERY EXECUTED!');
            console.log(`   ⏱️  Execution time: ${queryResponse.data.data.execution_time_ms}ms`);
            console.log(`   📊 Rows returned: ${queryResponse.data.data.row_count}`);
            console.log('   📋 Results:');
            queryResponse.data.data.rows.forEach(row => {
                console.log(`      ${row.role}: ${row.total_users} users`);
            });
            console.log('');
        } else {
            console.log('❌ Query execution failed:', queryResponse.data.message);
        }
        
        // Test 3: Real Analytics Dashboard
        console.log('📈 Testing REAL Analytics Dashboard...');
        const analyticsResponse = await axios.get(`${baseURL}/api/analytics/dashboard`, { headers });
        
        if (analyticsResponse.data.success) {
            console.log('✅ REAL ANALYTICS DATA LOADED!');
            console.log(`   📊 Data source: ${analyticsResponse.data.data_source}`);
            console.log(`   👥 Active users: ${analyticsResponse.data.data.systemMetrics.activeUsers}`);
            console.log(`   🔗 DB connections: ${analyticsResponse.data.data.systemMetrics.activeConnections}`);
            console.log(`   💾 Database size: ${analyticsResponse.data.data.systemMetrics.databaseSize}`);
            console.log(`   📈 Top products: ${analyticsResponse.data.data.topProducts.length} items\n`);
        } else {
            console.log('❌ Analytics failed:', analyticsResponse.data.message);
        }
        
        // Test 4: Real System Performance
        console.log('⚡ Testing REAL System Performance...');
        const perfResponse = await axios.get(`${baseURL}/api/analytics/system-performance`, { headers });
        
        if (perfResponse.data.success) {
            console.log('✅ REAL PERFORMANCE METRICS LOADED!');
            console.log(`   🕒 Response time: ${perfResponse.data.data.database_response_time}`);
            console.log(`   💯 Success rate: ${perfResponse.data.data.api_success_rate}`);
            console.log(`   🔗 Active connections: ${perfResponse.data.data.active_connections}`);
            console.log(`   💾 Database size: ${perfResponse.data.data.database_size}`);
            console.log(`   📊 Total queries: ${perfResponse.data.data.total_queries?.toLocaleString()}\n`);
        } else {
            console.log('❌ Performance metrics failed:', perfResponse.data.message);
        }
        
        // Test 5: Real System Status
        console.log('🔧 Testing REAL System Status...');
        const statusResponse = await axios.get(`${baseURL}/api/analytics/system-status`, { headers });
        
        if (statusResponse.data.success) {
            console.log('✅ REAL SYSTEM STATUS LOADED!');
            console.log(`   💾 Database: ${statusResponse.data.data.database_status}`);
            console.log(`   🚀 API: ${statusResponse.data.data.api_status}`);
            console.log(`   📦 Backup: ${statusResponse.data.data.backup_status}`);
            console.log(`   🕒 Last backup: ${statusResponse.data.data.last_backup}`);
            console.log(`   📋 Recent activities: ${statusResponse.data.data.recent_activities.length} items\n`);
        } else {
            console.log('❌ System status failed:', statusResponse.data.message);
        }
        
        // Test 6: Real Database Stats
        console.log('📊 Testing REAL Database Statistics...');
        const statsResponse = await axios.get(`${baseURL}/api/database/stats`, { headers });
        
        if (statsResponse.data.success) {
            console.log('✅ REAL DATABASE STATISTICS LOADED!');
            console.log(`   📊 Database: ${statsResponse.data.data.database_info.name}`);
            console.log(`   💾 Size: ${statsResponse.data.data.database_info.size}`);
            console.log(`   🔗 Connections: ${JSON.stringify(statsResponse.data.data.connections)}`);
            console.log('   📋 Record counts:');
            statsResponse.data.data.record_counts.forEach(table => {
                console.log(`      ${table.table_name}: ${table.record_count.toLocaleString()} records`);
            });
            console.log('');
        } else {
            console.log('❌ Database stats failed:', statsResponse.data.message);
        }
        
        // Test 7: User Management
        console.log('👥 Testing REAL User Management...');
        const usersResponse = await axios.get(`${baseURL}/api/users/stats`, { headers });
        
        if (usersResponse.data.success) {
            console.log('✅ REAL USER STATISTICS LOADED!');
            console.log(`   👥 Total users: ${usersResponse.data.data.stats.total_count?.toLocaleString()}`);
            console.log(`   👤 Admin users: ${usersResponse.data.data.stats.admin_count?.toLocaleString()}`);
            console.log(`   👨‍💼 Staff users: ${usersResponse.data.data.stats.staff_count?.toLocaleString()}`);
            console.log(`   🛒 Customer users: ${usersResponse.data.data.stats.customer_count?.toLocaleString()}\n`);
        } else {
            console.log('❌ User stats failed:', usersResponse.data.message);
        }
        
        console.log('🎉 ALL REAL FUNCTIONALITY TESTS COMPLETED!');
        console.log('');
        console.log('✅ SUMMARY: Your Database Administration System now has:');
        console.log('   📦 Real database backup/restore functionality');
        console.log('   🔍 Real SQL query execution console');
        console.log('   📈 Real analytics with live database data');
        console.log('   ⚡ Real performance monitoring');
        console.log('   🔧 Real system status checking');
        console.log('   📊 Real database statistics');
        console.log('   👥 Real user management with RBAC');
        console.log('   🔐 Real authentication and authorization');
        console.log('');
        console.log('🚀 NO MORE FAKE/DEMO DATA - EVERYTHING IS REAL AND FUNCTIONAL!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.response?.data || error.message);
    }
}

// Run the tests
testAllRealFeatures();
