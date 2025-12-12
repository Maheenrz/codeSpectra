import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Switch,
  FormControlLabel,
  Chip,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

function Assignments() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [course, setCourse] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    primaryLanguage: 'cpp',
    allowedExtensions: '.cpp,.h',
    maxFileSizeMb: 5,
    enableType1: true,
    enableType2: true,
    enableType3: true,
    enableType4: true,
    enableCrd: true,
    highSimilarityThreshold: 85,
    mediumSimilarityThreshold: 70,
    analysisMode: 'after_deadline',
    showResultsToStudents: false,
    generateFeedback: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (courseId) {
      fetchCourse();
      fetchAssignments();
    }
  }, [courseId]);

  const fetchCourse = async () => {
    try {
      const response = await api.get(`/courses/${courseId}`);
      setCourse(response.data);
    } catch (err) {
      console.error('Error fetching course:', err);
      navigate('/courses');
    }
  };

  const fetchAssignments = async () => {
    try {
      const response = await api.get(`/courses/${courseId}/assignments`);
      setAssignments(response.data);
    } catch (err) {
      console.error('Error fetching assignments:', err);
    }
  };

  const handleOpenDialog = (assignment = null) => {
    if (assignment) {
      setEditingAssignment(assignment);
      setFormData({
        title: assignment.title,
        description: assignment.description,
        dueDate: new Date(assignment.due_date),
        primaryLanguage: assignment.primary_language,
        allowedExtensions: assignment.allowed_extensions,
        maxFileSizeMb: assignment.max_file_size_mb,
        enableType1: assignment.enable_type1,
        enableType2: assignment.enable_type2,
        enableType3: assignment.enable_type3,
        enableType4: assignment.enable_type4,
        enableCrd: assignment.enable_crd,
        highSimilarityThreshold: assignment.high_similarity_threshold,
        mediumSimilarityThreshold: assignment.medium_similarity_threshold,
        analysisMode: assignment.analysis_mode,
        showResultsToStudents: assignment.show_results_to_students,
        generateFeedback: assignment.generate_feedback
      });
    } else {
      setEditingAssignment(null);
      setFormData({
        title: '',
        description: '',
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        primaryLanguage: 'cpp',
        allowedExtensions: '.cpp,.h',
        maxFileSizeMb: 5,
        enableType1: true,
        enableType2: true,
        enableType3: true,
        enableType4: true,
        enableCrd: true,
        highSimilarityThreshold: 85,
        mediumSimilarityThreshold: 70,
        analysisMode: 'after_deadline',
        showResultsToStudents: false,
        generateFeedback: true
      });
    }
    setOpenDialog(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = {
        ...formData,
        courseId: parseInt(courseId)
      };

      if (editingAssignment) {
        await api.put(`/assignments/${editingAssignment.assignment_id}`, data);
        setSuccess('Assignment updated successfully');
      } else {
        await api.post('/assignments', data);
        setSuccess('Assignment created successfully');
      }
      handleCloseDialog();
      fetchAssignments();
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (assignmentId) => {
    if (!window.confirm('Are you sure you want to delete this assignment?')) return;

    try {
      await api.delete(`/assignments/${assignmentId}`);
      setSuccess('Assignment deleted successfully');
      fetchAssignments();
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const isAssignmentActive = (dueDate) => {
    return new Date(dueDate) > new Date();
  };

  if (!course) return null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {course.course_code}: {course.course_name}
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {course.semester} {course.year}
            </Typography>
          </Box>
          {user?.role === 'instructor' && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Create Assignment
            </Button>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {assignments.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No assignments found
            </Typography>
            {user?.role === 'instructor' && (
              <Typography variant="body2" color="textSecondary">
                Create your first assignment to get started
              </Typography>
            )}
          </Box>
        ) : (
          <Grid container spacing={3}>
            {assignments.map((assignment) => (
              <Grid item xs={12} md={6} key={assignment.assignment_id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="h2">
                        {assignment.title}
                      </Typography>
                      <Chip
                        label={isAssignmentActive(assignment.due_date) ? 'Active' : 'Completed'}
                        color={isAssignmentActive(assignment.due_date) ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {assignment.description?.substring(0, 150)}
                      {assignment.description?.length > 150 ? '...' : ''}
                    </Typography>

                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Due Date
                        </Typography>
                        <Typography variant="body2">
                          {formatDate(assignment.due_date)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Language
                        </Typography>
                        <Typography variant="body2">
                          {assignment.primary_language.toUpperCase()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Submissions
                        </Typography>
                        <Typography variant="body2">
                          {assignment.submission_count || 0} submitted
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Analysis
                        </Typography>
                        <Typography variant="body2">
                          {assignment.analyzed_count || 0} analyzed
                        </Typography>
                      </Grid>
                    </Grid>

                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                      {assignment.enable_type1 && <Chip label="Type 1" size="small" />}
                      {assignment.enable_type2 && <Chip label="Type 2" size="small" />}
                      {assignment.enable_type3 && <Chip label="Type 3" size="small" />}
                      {assignment.enable_type4 && <Chip label="Type 4" size="small" />}
                      {assignment.enable_crd && <Chip label="CRD" size="small" />}
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      href={`/assignments/${assignment.assignment_id}`}
                    >
                      View
                    </Button>
                    {user?.role === 'instructor' && (
                      <>
                        <Button
                          size="small"
                          startIcon={<AnalyticsIcon />}
                          href={`/analysis/${assignment.assignment_id}`}
                        >
                          Analyze
                        </Button>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(assignment)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(assignment.assignment_id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </>
                    )}
                    {user?.role === 'student' && isAssignmentActive(assignment.due_date) && (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<UploadIcon />}
                        href={`/assignments/${assignment.assignment_id}/submit`}
                      >
                        Submit
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Create/Edit Assignment Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAssignment ? 'Edit Assignment' : 'Create New Assignment'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Assignment Title"
                  name="title"
                  fullWidth
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  name="description"
                  multiline
                  rows={4}
                  fullWidth
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Due Date"
                    value={formData.dueDate}
                    onChange={(date) => setFormData({ ...formData, dueDate: date })}
                    renderInput={(params) => <TextField {...params} fullWidth required />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Primary Language"
                  name="primaryLanguage"
                  select
                  fullWidth
                  required
                  value={formData.primaryLanguage}
                  onChange={(e) => setFormData({ ...formData, primaryLanguage: e.target.value })}
                  SelectProps={{ native: true }}
                >
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                  <option value="python">Python</option>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Clone Detection Settings
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableType1}
                      onChange={(e) => setFormData({ ...formData, enableType1: e.target.checked })}
                    />
                  }
                  label="Enable Type 1 Detection"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableType2}
                      onChange={(e) => setFormData({ ...formData, enableType2: e.target.checked })}
                    />
                  }
                  label="Enable Type 2 Detection"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableType3}
                      onChange={(e) => setFormData({ ...formData, enableType3: e.target.checked })}
                    />
                  }
                  label="Enable Type 3 Detection"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableType4}
                      onChange={(e) => setFormData({ ...formData, enableType4: e.target.checked })}
                    />
                  }
                  label="Enable Type 4 Detection"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableCrd}
                      onChange={(e) => setFormData({ ...formData, enableCrd: e.target.checked })}
                    />
                  }
                  label="Enable Clone-Resilient Detection (CRD)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="High Similarity Threshold (%)"
                  name="highSimilarityThreshold"
                  type="number"
                  fullWidth
                  value={formData.highSimilarityThreshold}
                  onChange={(e) => setFormData({ ...formData, highSimilarityThreshold: e.target.value })}
                  inputProps={{ min: 0, max: 100, step: 0.1 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Medium Similarity Threshold (%)"
                  name="mediumSimilarityThreshold"
                  type="number"
                  fullWidth
                  value={formData.mediumSimilarityThreshold}
                  onChange={(e) => setFormData({ ...formData, mediumSimilarityThreshold: e.target.value })}
                  inputProps={{ min: 0, max: 100, step: 0.1 }}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Visibility Settings
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.showResultsToStudents}
                      onChange={(e) => setFormData({ ...formData, showResultsToStudents: e.target.checked })}
                    />
                  }
                  label="Show Analysis Results to Students"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.generateFeedback}
                      onChange={(e) => setFormData({ ...formData, generateFeedback: e.target.checked })}
                    />
                  }
                  label="Generate Educational Feedback"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? 'Saving...' : editingAssignment ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess('')}
        message={success}
      />
    </Container>
  );
}

export default Assignments;