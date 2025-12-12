
import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, Container, CircularProgress } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';
import { useAuth } from '../../contexts/AuthContext';

function Layout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return (
    <Box display="flex" minHeight="100vh">
      <Sidebar />
      <Box flex={1} display="flex" flexDirection="column">
        <Header />
        <Container maxWidth="xl" sx={{ flex: 1, py: 3 }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}

export default Layout;