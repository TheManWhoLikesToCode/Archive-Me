function getConfig() {
    const config = {
        apiUrl: {
            dev: "http://localhost:5003",
            prod: "https://api.archive-me.net"
        }
    };
    return config;
}

function getEnv() {
    const hostname = window.location.hostname;
    return hostname.includes('localhost') ? 'dev' : 'prod';
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
