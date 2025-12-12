import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Download as DownloadIcon,
  PictureAsPdf as PdfIcon,
  TableChart as CsvIcon,
  Assessment as ReportIcon,
  Assessment as AssessmentIcon,  
  FilterList as FilterIcon,
  Warning as WarningIcon  
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';




function Reports() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [filters, setFilters] = useState({
    courseId: '',
    assignmentId: '',
    startDate: null,
    endDate: null,
    reportType: 'similarity',
    format: 'pdf'
  });

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    if (filters.courseId) {
      fetchAssignments(filters.courseId);
    }
  }, [filters.courseId]);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/courses');
      setCourses(response.data);
    } catch (err) {
      console.error('Error fetching courses:', err);
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
  };

  const generateReport = async () => {
    if (!filters.courseId) {
      setError('Please select a course');
      return;
    }

    setGenerating(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/reports/generate', filters, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const filename = `codespectra-report-${Date.now()}.${filters.format}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setSuccess(`Report downloaded: ${filename}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Error generating report');
    } finally {
      setGenerating(false);
    }
  };

  const reportTypes = [
    { value: 'similarity', label: 'Similarity Analysis', icon: <ReportIcon /> },
    { value: 'statistics', label: 'Course Statistics', icon: <AssessmentIcon /> },
    { value: 'plagiarism', label: 'Plagiarism Cases', icon: <WarningIcon /> }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Reports & Exports
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Report Filters
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Course</InputLabel>
                  <Select
                    value={filters.courseId}
                    label="Course"
                    onChange={(e) => handleFilterChange('courseId', e.target.value)}
                  >
                    <MenuItem value="">All Courses</MenuItem>
                    {courses.map((course) => (
                      <MenuItem key={course.course_id} value={course.course_id}>
                        {course.course_code} - {course.course_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
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

              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Report Type</InputLabel>
                  <Select
                    value={filters.reportType}
                    label="Report Type"
                    onChange={(e) => handleFilterChange('reportType', e.target.value)}
                  >
                    {reportTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Start Date"
                    value={filters.startDate}
                    onChange={(date) => handleFilterChange('startDate', date)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>

              <Grid item xs={12} md={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="End Date"
                    value={filters.endDate}
                    onChange={(date) => handleFilterChange('endDate', date)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>

              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Export Format</InputLabel>
                  <Select
                    value={filters.format}
                    label="Export Format"
                    onChange={(e) => handleFilterChange('format', e.target.value)}
                  >
                    <MenuItem value="pdf">
                      <PdfIcon sx={{ mr: 1 }} /> PDF Document
                    </MenuItem>
                    <MenuItem value="csv">
                      <CsvIcon sx={{ mr: 1 }} /> CSV Spreadsheet
                    </MenuItem>
                    <MenuItem value="json">
                      <ReportIcon sx={{ mr: 1 }} /> JSON Data
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>

          <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
            <Button
              variant="contained"
              startIcon={generating ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={generateReport}
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Report'}
            </Button>
          </CardActions>
        </Card>

        <Typography variant="h6" gutterBottom>
          Recent Reports
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Similarity Analysis - CS201
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Generated: Dec 10, 2024
                </Typography>
                <Typography variant="body2">
                  45 submissions analyzed, 3 high similarity cases
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" startIcon={<PdfIcon />}>
                  Download PDF
                </Button>
              </CardActions>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Course Statistics - Fall 2024
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Generated: Dec 5, 2024
                </Typography>
                <Typography variant="body2">
                  3 courses, 12 assignments, 150+ submissions
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" startIcon={<CsvIcon />}>
                  Download CSV
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}

export default Reports;