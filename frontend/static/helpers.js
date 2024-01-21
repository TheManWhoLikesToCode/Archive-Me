function getConfig() {
    const config = {
        apiUrl: {
            dev: "http://devapi.archive-me.net",
            prod: "https://api.archive-me.net",
            local: "http://localhost:5003"
        }
    };
    return config;
}

function getEnv() {
    const hostname = window.location.hostname;
    if (hostname.includes('localhost')) return 'local';
    if (hostname.includes('dev')) return 'dev';
    return 'prod';
}

function getApiUrl() {
    const config = getConfig();
    const env = getEnv();

    if (!config.apiUrl[env]) {
        throw new Error('Api url not found.');
    }

    return config.apiUrl[env];
}

export { getEnv, getApiUrl };
