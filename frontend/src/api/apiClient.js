import axios from 'axios';

// Token de acesso que você gerou
const DEV_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTc1NzAzNzI0Nn0.uWx0_f00fwp_avffHemTbHZ0EN7ZJ8ljqRNfm2I5hg4';

const apiClient = axios.create({
    baseURL: '/api/v1', // Usamos o prefixo padronizado da nossa API
});

// Intercepta TODAS as requisições antes de serem enviadas
// e adiciona o cabeçalho de autorização.
apiClient.interceptors.request.use(
    (config) => {
        if (DEV_ACCESS_TOKEN) {
            config.headers.Authorization = `Bearer ${DEV_ACCESS_TOKEN}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default apiClient;