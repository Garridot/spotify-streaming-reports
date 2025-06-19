async function fetchData(url, options = {}, retries = 3, timeout = 5000) {
    try {
        const controller = new AbortController(); // Control para manejar el timeout
        const signal = controller.signal;

        // Crear un timeout para abortar la solicitud si se demora más de lo esperado
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        // Intentar la solicitud con fetch
        const response = await fetch(url, { ...options, signal, credentials: 'include', });

        clearTimeout(timeoutId); // Limpiar el timeout si la solicitud es exitosa

        // Comprobar si la respuesta fue exitosa (status 2xx)
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }        

        const data = await response.json(); // Parsear el JSON
        return data;
    } catch (error) {
                
        if (!error.message.includes('404')){

            if (retries > 0) { // Si la solicitud falla y hay reintentos disponibles
                console.warn(`Attempt failed, retrying... (${retries} left)`);
                return fetchData(url, options, retries - 1, timeout);
            } else if (error.name === 'AbortError') {
                console.error('Request timeout, aborting.');
                throw new Error('Request timeout');
            } else {
                console.error(`Request failed: ${error.message}`);
                throw error; // Lanza el error para que se maneje fuera de la función
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