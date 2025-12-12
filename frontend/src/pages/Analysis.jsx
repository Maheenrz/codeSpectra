import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  CompareArrows as CompareIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

function Analysis() {
  const { assignmentId } = useParams();
  const { user } = useAuth();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (assignmentId) {
      fetchAnalysisData();
    }
  }, [assignmentId]);

  const fetchAnalysisData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/assignments/${assignmentId}/analysis`);
      setAnalysisData(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Error fetching analysis data');
    } finally {
      setLoading(false);
    }
  };

  const triggerAnalysis = async () => {
    try {
      await api.post(`/assignments/${assignmentId}/analyze`);
      alert('Analysis started! Check back in a few minutes.');
      fetchAnalysisData();
    } catch (err) {
      setError(err.response?.data?.message || 'Error triggering analysis');
    }
  };

  const getSimilarityColor = (score) => {
    if (score >= 85) return 'error';
    if (score >= 70) return 'warning';
    return 'success';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Similarity Analysis
          </Typography>
          {user?.role === 'instructor' && (
            <Button
              variant="contained"
              startIcon={<TimelineIcon />}
              onClick={triggerAnalysis}
            >
              Run Analysis
            </Button>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
          <Tab label="Overview" />
          <Tab label="Similarity Pairs" />
          <Tab label="Statistics" />
        </Tabs>

        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Submissions
                  </Typography>
                  <Typography variant="h3">
                    {analysisData?.summary?.totalSubmissions || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    High Similarity Cases
                  </Typography>
                  <Typography variant="h3" color="error">
                    {analysisData?.summary?.highSimilarity || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Analysis Status
                  </Typography>
                  <Chip
                    label={analysisData?.summary?.status || 'Pending'}
                    color={analysisData?.summary?.status === 'Completed' ? 'success' : 'warning'}
                    icon={analysisData?.summary?.status === 'Completed' ? <CheckCircleIcon /> : <WarningIcon />}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {activeTab === 1 && analysisData?.similarityPairs && (
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Student 1</TableCell>
                  <TableCell>Student 2</TableCell>
                  <TableCell>Similarity</TableCell>
                  <TableCell>Clone Type</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analysisData.similarityPairs.map((pair, index) => (
                  <TableRow key={index}>
                    <TableCell>{pair.student1}</TableCell>
                    <TableCell>{pair.student2}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${pair.similarity}%`}
                        color={getSimilarityColor(pair.similarity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={`Type ${pair.cloneType}`} size="small" />
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<CompareIcon />}
                        onClick={() => alert(`Compare ${pair.student1} and ${pair.student2}`)}
                      >
                        Compare
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Detection Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Clone Type Distribution
                  </Typography>
                  {/* Add chart or stats here */}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Similarity Score Distribution
                  </Typography>
                  {/* Add chart or stats here */}
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default Analysis;