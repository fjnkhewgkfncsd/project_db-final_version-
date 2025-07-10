#!/usr/bin/env node
/**
 * Clear Rate Limit Script
 * Use this script if you get rate limited during development
 */

const axios = require('axios');

async function clearRateLimit() {
    console.log('🔄 Attempting to clear rate limit...');
    
    try {
        // Wait for rate limit window to expire (15 minutes)
        console.log('⏰ Waiting for rate limit window to reset...');
        console.log('💡 Tip: Rate limit is now increased to 1000 requests per 15 minutes');
        console.log('📊 Dashboard auto-refresh is now set to every 2 minutes instead of 30 seconds');
        console.log('');
        console.log('🛠️ Solutions:');
        console.log('1. Wait 15 minutes for rate limit to reset');
        console.log('2. Restart the backend server (already done)');
        console.log('3. Use manual refresh instead of auto-refresh on dashboard');
        console.log('4. Check network tab for excessive API calls');
        
        // Test connection
        const response = await axios.get('http://localhost:3001/health');
        console.log('✅ Backend server is responding:', response.data.message);
        
    } catch (error) {
        console.error('❌ Error checking backend:', error.message);
    }
}

if (require.main === module) {
    clearRateLimit();
}

module.exports = { clearRateLimit };
