import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // FastAPI Backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Watchlists
  getWatchlists: () => 
    apiClient.get('/api/watchlists'),
  
  // Screener
  runScreener: (params: {
    watchlist_name: string;
    screener_type: string;
    parameters?: Record<string, any>;
  }) => 
    apiClient.post('/api/screener/run', params),
  
  getScreenerResults: (screenerId: number) =>
    apiClient.get(`/api/screener/results/${screenerId}`),
};

export default api;