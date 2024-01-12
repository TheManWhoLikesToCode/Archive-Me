import config from 'frontend/config.json'

function getEnv() {
    if (!process.env) {
        throw new Error('Process environment not found.');
    }
    return process.env.ENVIRONMENT
}

function getApiUrl() {
    return config.apiUrl[getEnv()]
}

export { getEnv, getApiUrl }