import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  LinearProgress,
  Avatar
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  School as SchoolIcon,
  Upload as UploadIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalAssignments: 0,
    totalSubmissions: 0,
    pendingAnalysis: 0,
    highSimilarity: 0
  });
  const [recentAssignments, setRecentAssignments] = useState([]);
  const [submissionTrend, setSubmissionTrend] = useState([]);
  const [similarityDistribution, setSimilarityDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, assignmentsRes, trendRes, distRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/dashboard/recent-assignments'),
        api.get('/dashboard/submission-trend'),
        api.get('/dashboard/similarity-distribution')
      ]);

      setStats(statsRes.data);
      setRecentAssignments(assignmentsRes.data);
      setSubmissionTrend(trendRes.data);
      setSimilarityDistribution(distRes.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRoleBasedWelcome = () => {
    const name = user?.firstName || user?.email?.split('@')[0];
    switch (user?.role) {
      case 'instructor':
        return `Welcome, Professor ${name}`;
      case 'admin':
        return `Welcome, Administrator ${name}`;
      default:
        return `Welcome, ${name}`;
    }
  };

  const getRoleBasedDescription = () => {
    switch (user?.role) {
      case 'instructor':
        return 'Monitor assignments, analyze submissions, and detect code similarity';
      case 'admin':
        return 'Manage system configuration and user accounts';
      default:
        return 'Submit assignments and track your progress';
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <Container>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Welcome Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
            {user?.firstName?.[0] || user?.email?.[0]}
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1">
              {getRoleBasedWelcome()}
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {getRoleBasedDescription()}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip icon={<SchoolIcon />} label={`Institution: ${user?.institution}`} />
          <Chip icon={<AssignmentIcon />} label={`Role: ${user?.role}`} />
          <Chip icon={<AccessTimeIcon />} label={`Member since: ${new Date(user?.createdAt).toLocaleDateString()}`} />
        </Box>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SchoolIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Courses
                </Typography>
              </Box>
              <Typography variant="h4">{stats.totalCourses}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssignmentIcon color="secondary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Assignments
                </Typography>
              </Box>
              <Typography variant="h4">{stats.totalAssignments}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <UploadIcon color="success" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Submissions
                </Typography>
              </Box>
              <Typography variant="h4">{stats.totalSubmissions}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccessTimeIcon color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Pending Analysis
                </Typography>
              </Box>
              <Typography variant="h4">{stats.pendingAnalysis}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WarningIcon color="error" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  High Similarity
                </Typography>
              </Box>
              <Typography variant="h4">{stats.highSimilarity}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Submission Trend Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Submission Trend (Last 7 Days)
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={submissionTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="submissions" stroke="#8884d8" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="analyzed" stroke="#82ca9d" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Similarity Distribution Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Similarity Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={similarityDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {similarityDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Assignments */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            Recent Assignments
          </Typography>
          <Button href="/assignments">
            View All
          </Button>
        </Box>

        <List>
          {recentAssignments.map((assignment, index) => (
            <React.Fragment key={assignment.assignment_id}>
              <ListItem>
                <ListItemIcon>
                  {assignment.analysis_complete ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <AccessTimeIcon color="warning" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={assignment.title}
                  secondary={
                    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                      <span>{assignment.course_name}</span>
                      <span>Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                      <span>Submissions: {assignment.submission_count || 0}</span>
                      {assignment.high_similarity_count > 0 && (
                        <span style={{ color: '#f44336' }}>
                          {assignment.high_similarity_count} potential plagiarism cases
                        </span>
                      )}
                    </Box>
                  }
                />
                <Box>
                  <Button
                    size="small"
                    variant="outlined"
                    href={`/assignments/${assignment.assignment_id}`}
                    sx={{ mr: 1 }}
                  >
                    View
                  </Button>
                  {user?.role === 'instructor' && (
                    <Button
                      size="small"
                      variant="contained"
                      href={`/analysis/${assignment.assignment_id}`}
                    >
                      Analyze
                    </Button>
                  )}
                </Box>
              </ListItem>
              {index < recentAssignments.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Paper>

      {/* Quick Actions */}
      {user?.role === 'instructor' && (
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SchoolIcon />}
                href="/courses"
                sx={{ py: 2 }}
              >
                Create Course
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AssignmentIcon />}
                href="/assignments"
                sx={{ py: 2 }}
              >
                Create Assignment
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<TrendingUpIcon />}
                href="/reports"
                sx={{ py: 2 }}
              >
                View Reports
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<UploadIcon />}
                href="/submissions"
                sx={{ py: 2 }}
              >
                Manage Submissions
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
}

export default Dashboard;