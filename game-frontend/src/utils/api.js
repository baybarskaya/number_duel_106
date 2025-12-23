import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Axios instance oluştur
const api = axios.create({
    baseURL: API_BASE_URL,
});

// Request interceptor - Her isteğe token ekle
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Token yenileme mekanizması
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // 401 hatası ve henüz retry yapılmamışsa
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                
                // Refresh token ile yeni access token al
                const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                    refresh: refreshToken
                });

                const newAccessToken = response.data.access;
                localStorage.setItem('access_token', newAccessToken);

                // Başarısız olan isteği yeni token ile tekrar dene
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh token da geçersizse, logout yap
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// API fonksiyonları
export const authAPI = {
    login: (username, password) => 
        api.post('/auth/login/', { username, password }),
    
    register: (userData) => 
        api.post('/auth/register/', userData),
    
    getProfile: () => 
        api.get('/auth/profile/'),
    
    getBalance: () => 
        api.get('/auth/balance/'),
};

export const gameAPI = {
    getRooms: () => 
        api.get('/game/rooms/'),
    
    createRoom: (roomData) => 
        api.post('/game/rooms/', roomData),
    
    joinRoom: (roomId) => 
        api.post(`/game/rooms/${roomId}/join/`),
    
    getTransactions: () => 
        api.get('/game/transactions/'),
    
    getLeaderboard: () => 
        api.get('/game/leaderboard/'),
};

export default api;

