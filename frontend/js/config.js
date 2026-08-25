// Override with window.APP_CONFIG before this script when deploying elsewhere.
const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL || (isLocal ? 'http://127.0.0.1:5000' : '/api');
