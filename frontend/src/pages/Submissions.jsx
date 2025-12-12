import React, { useState, useEffect } from 'react';
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
  IconButton,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

function Submissions() {
  const { user } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    courseId: '',
    assignmentId: '',
    status: '',
    search: ''
  });
  const [courses, setCourses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  useEffect(() => {
    fetchCourses();
    fetchSubmissions();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/courses');
      setCourses(response.data);
    } catch (err) {
      console.error('Error fetching courses:', err);
    }
  };

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      if (filters.courseId) queryParams.append('courseId', filters.courseId);
      if (filters.assignmentId) queryParams.append('assignmentId', filters.assignmentId);
      if (filters.status) queryParams.append('status', filters.status);

      const response = await api.get(`/submissions?${queryParams}`);
      setSubmissions(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Error fetching submissions');
    } finally {
      setLoading(false);
    }
  };

  const fetchAssignments = async (courseId) => {
    try {
      const response = await api.get(`/courses/${courseId}/assignments`);
      setAssignments(response.data);
    } catch (err) {
      console.error('Error fetching assignments:', err);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));

    if (field === 'courseId') {
      setFilters(prev => ({ ...prev, assignmentId: '' }));
      if (value) {
        fetchAssignments(value);
      } else {
        setAssignments([]);
      }
    }
  };

  const handleSearch = () => {
    fetchSubmissions();
  };

  const handleViewSubmission = (submission) => {
    setSelectedSubmission(submission);
    setViewDialog(true);
  };

  const handleDownload = async (submissionId, filename) => {
    try {
      const response = await api.get(`/submissions/${submissionId}/download`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Error downloading file');
    }
  };

  const handleDelete = async (submissionId) => {
    if (!window.confirm('Are you sure you want to delete this submission?')) return;

    try {
      await api.delete(`/submissions/${submissionId}`);
      fetchSubmissions();
    } catch (err) {
      setError(err.response?.data?.message || 'Error deleting submission');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  if (loading && submissions.length === 0) {
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
        <Typography variant="h4" component="h1" gutterBottom>
          Submissions
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Card sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Course</InputLabel>
                <Select
                  value={filters.courseId}
                  label="Course"
                  onChange={(e) => handleFilterChange('courseId', e.target.value)}
                >
                  <MenuItem value="">All Courses</MenuItem>
                  {courses.map((course) => (
                    <MenuItem key={course.course_id} value={course.course_id}>
                      {course.course_code}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Assignment</InputLabel>
                <Select
                  value={filters.assignmentId}
                  label="Assignment"
                  onChange={(e) => handleFilterChange('assignmentId', e.target.value)}
                  disabled={!filters.courseId}
                >
                  <MenuItem value="">All Assignments</MenuItem>
                  {assignments.map((assignment) => (
                    <MenuItem key={assignment.assignment_id} value={assignment.assignment_id}>
                      {assignment.title}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  label="Status"
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Search by student or file"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </Grid>

            <Grid item xs={12} md={1}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </Card>

        {/* Submissions Table */}
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Student</TableCell>
                <TableCell>Assignment</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Submitted</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Similarity</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {submissions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No submissions found
                  </TableCell>
                </TableRow>
              ) : (
                submissions.map((submission) => (
                  <TableRow key={submission.submission_id}>
                    <TableCell>
                      {submission.first_name} {submission.last_name}
                      <br />
                      <Typography variant="caption" color="textSecondary">
                        {submission.email}
                      </Typography>
                    </TableCell>
                    <TableCell>{submission.assignment_title}</TableCell>
                    <TableCell>{submission.course_code}</TableCell>
                    <TableCell>
                      {new Date(submission.submitted_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={submission.analysis_status}
                        color={getStatusColor(submission.analysis_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {submission.similarity_score ? (
                        <Chip
                          label={`${submission.similarity_score}%`}
                          color={submission.similarity_score >= 85 ? 'error' : 'default'}
                          size="small"
                        />
                      ) : (
                        '--'
                      )}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleViewSubmission(submission)}
                        title="View Details"
                      >
                        <ViewIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(submission.submission_id, submission.filename)}
                        title="Download"
                      >
                        <DownloadIcon />
                      </IconButton>
                      {user?.role === 'instructor' && (
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(submission.submission_id)}
                          title="Delete"
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* View Submission Dialog */}
        <Dialog
          open={viewDialog}
          onClose={() => setViewDialog(false)}
          maxWidth="md"
          fullWidth
        >
          {selectedSubmission && (
            <>
              <DialogTitle>
                Submission Details
                <Typography variant="subtitle2" color="textSecondary">
                  {selectedSubmission.filename}
                </Typography>
              </DialogTitle>
              <DialogContent>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Student</Typography>
                    <Typography>
                      {selectedSubmission.first_name} {selectedSubmission.last_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Submitted</Typography>
                    <Typography>
                      {new Date(selectedSubmission.submitted_at).toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Assignment</Typography>
                    <Typography>{selectedSubmission.assignment_title}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Course</Typography>
                    <Typography>{selectedSubmission.course_name}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Code Preview
                      </Typography>
                      <pre style={{ margin: 0, fontSize: '0.9rem', maxHeight: '300px', overflow: 'auto' }}>
                        {/* Code preview would go here */}
                        {`// ${selectedSubmission.filename}\n// File size: ${Math.round(selectedSubmission.file_size_bytes / 1024)} KB`}
                      </pre>
                    </Box>
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogActions>
                <Button
                  onClick={() => handleDownload(selectedSubmission.submission_id, selectedSubmission.filename)}
                  startIcon={<DownloadIcon />}
                >
                  Download
                </Button>
                <Button onClick={() => setViewDialog(false)}>Close</Button>
              </DialogActions>
            </>
          )}
        </Dialog>
      </Paper>
    </Container>
  );
}

export default Submissions;