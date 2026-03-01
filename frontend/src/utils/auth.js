export const getToken = () => {
  return localStorage.getItem('token');
};

export const setToken = (token) => {
  localStorage.setItem('token', token);
};

export const removeToken = () => {
  localStorage.removeItem('token');
};

export const getUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

export const removeUser = () => {
  localStorage.removeItem('user');
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const getUserRole = () => {
  const user = getUser();
  return user?.role;
};

export const isStudent = () => getUserRole() === 'student';
export const isInstructor = () => getUserRole() === 'instructor';
export const isAdmin = () => getUserRole() === 'admin';