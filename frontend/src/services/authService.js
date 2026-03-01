import api from '../utils/api';
import { setToken, setUser, removeToken, removeUser } from '../utils/auth';

const authService = {
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    if (response.data.token) {
      setToken(response.data.token);
      setUser(response.data.user);
    }
    return response.data;
  },

  async login(credentials) {
    const response = await api.post('/auth/login', credentials);
    if (response.data.token) {
      setToken(response.data.token);
      setUser(response.data.user);
    }
    return response.data;
  },

  async logout() {
    removeToken();
    removeUser();
  },

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  async updateProfile(updates) {
    const response = await api.put('/auth/profile', updates);
    setUser(response.data.user);
    return response.data;
  },
};

export default authService;