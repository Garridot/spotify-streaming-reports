async function fetchData(url, options = {}, retries = 3, timeout = 9000) {
    try {
        const controller = new AbortController(); // Control to manage the waiting time
        const signal = controller.signal;

        // Create a timeout to abort the request if it takes longer than expected
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        // Attempt the request with fetch
        const response = await fetch(url, { ...options, signal, credentials: 'include', });

        clearTimeout(timeoutId); // Clear the timeout if the request is successful

        // Check if the response was successful (status 2xx)
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }        

        const data = await response.json(); // Parse the JSON
        return data;
    } catch (error) {
                
        if (!error.message.includes('404')){

            if (retries > 0) { // If the request fails and retries are available
                console.warn(`Attempt failed, retrying... (${retries} left)`);
                return fetchData(url, options, retries - 1, timeout);
            } else if (error.name === 'AbortError') {
                console.error('Request timeout, aborting.');
                throw new Error('Request timeout');
            } else {
                console.error(`Request failed: ${error.message}`);
                throw error; // Throw the error to be handled outside the function
            }
        } else { 
            throw error;
        }
    }
}

export async function getSpotyAuth() {
    const url = '/api/auth/spotify/login';
    try {
        const data = await fetchData(url);        
        return data;
    } catch (error) {
        console.error('Failed to fetch Spotify Auth:', error);
    }
}

export async function getUserInfo() {
    const url = '/api/auth/get_user_info';
    try {
        const data = await fetchData(url);        
        return data;
    } catch (error) {
        console.error('Failed to fetch User Info:', error);
    }
}

export async function getUserStats(id) {    
    const url = '/api/user_stats/weekly_stats';
    const options = {
        headers: {
            'X-Weekly-Id': id,              
        }
    };    
    try {
        const data = await fetchData(url, options);        
        return data;
    } catch (error) {
        console.error('Failed to fetch User Stats:', error);
    }
}

export async function getUserWeeklyReports () {
    const url = '/api/user_stats/weekly_history';
    try {
        const data = await fetchData(url);        
        return data;
    } catch (error) {
        console.error('Failed to fetch User Weekly History:', error);
    }
}

export async function getUserActivity () {
    const url = '/api/user_stats/user_last_activity';
    try {
        const data = await fetchData(url);        
        return data;
    } catch (error) {
        console.error('Failed to fetch User Last Activity:', error);
    }
}