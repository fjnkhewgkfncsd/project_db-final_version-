const bcrypt = require('bcryptjs');

// Test if the password hash is correct
const testPassword = 'admin123';
const hash = '$2b$10$rKjw.6QxEQsxZ5GvKjQxHOqXcXPKXP8Zd8WcE7Y3qYzRxZqK9WqDC';

bcrypt.compare(testPassword, hash, (err, result) => {
    if (err) {
        console.error('Error:', err);
    } else {
        console.log(`Password "admin123" matches hash: ${result}`);
    }
});

// Also test creating a new hash
bcrypt.hash('admin123', 10, (err, newHash) => {
    if (err) {
        console.error('Error creating hash:', err);
    } else {
        console.log('New hash for admin123:', newHash);
    }
});
