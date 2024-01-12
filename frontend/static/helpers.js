import config from 'frontend/config.json'

function getEnv() {
    if (!process.env) {
        throw new Error('Process environment not found.');
    }
    return process.env.ENVIRONMENT
}

function getApiUrl() {
    
    if (!config.apiUrl[getEnv()]) {
        throw new Error('Api url not found.');
    }

    return config.apiUrl[getEnv()]
}

export { getEnv, getApiUrl }