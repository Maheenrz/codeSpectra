-- ========================================
-- CodeSpectra Complete Database Schema
-- Combines existing backend + new analysis engine
-- ========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- ========================================
-- PART 1: EXISTING BACKEND TABLES
-- (Your original schema)
-- ========================================

-- Users table (from your existing backend)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'student',  -- student, teacher, admin
    institution VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    course_code VARCHAR(50) UNIQUE NOT NULL,
    instructor_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    semester VARCHAR(50),
    year INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    max_score DECIMAL(5,2) DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
    submission_id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score DECIMAL(5,2),
    feedback TEXT,
    status VARCHAR(50) DEFAULT 'submitted'  -- submitted, graded, pending_review
);

-- ========================================
-- PART 2: NEW ANALYSIS ENGINE TABLES
-- (Clone detection system)
-- ========================================

-- Projects table (for clone detection)
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    submission_id INTEGER REFERENCES submissions(submission_id) ON DELETE SET NULL,  -- Link to submission if applicable
    repository_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files table (source code files)
CREATE TABLE IF NOT EXISTS files (
    file_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),  -- python, java, javascript, etc.
    file_size BIGINT,
    content_hash VARCHAR(64),  -- SHA256 hash
    lines_of_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, file_path)
);

-- Analysis sessions
CREATE TABLE IF NOT EXISTS analysis_sessions (
    session_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    analysis_type VARCHAR(50),  -- full, incremental, type1, type2, type3, type4
    config JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0
);

-- Clone groups
CREATE TABLE IF NOT EXISTS clone_groups (
    group_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES analysis_sessions(session_id) ON DELETE CASCADE,
    clone_type VARCHAR(10) NOT NULL,  -- type1, type2, type3, type4
    similarity_score DECIMAL(5,2),  -- 0.00 to 100.00
    clone_count INTEGER DEFAULT 0,
    lines_of_code INTEGER,
    tokens_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clone instances
CREATE TABLE IF NOT EXISTS clone_instances (
    instance_id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES clone_groups(group_id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES files(file_id) ON DELETE CASCADE,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    start_column INTEGER,
    end_column INTEGER,
    code_snippet TEXT,
    normalized_code TEXT,
    token_sequence TEXT,
    ast_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detection metrics
CREATE TABLE IF NOT EXISTS detection_metrics (
    metric_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES analysis_sessions(session_id) ON DELETE CASCADE,
    clone_type VARCHAR(10) NOT NULL,
    detector_name VARCHAR(100),
    total_comparisons BIGINT,
    clones_found INTEGER,
    execution_time_ms INTEGER,
    memory_used_mb DECIMAL(10,2),
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code metrics
CREATE TABLE IF NOT EXISTS code_metrics (
    metric_id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files(file_id) ON DELETE CASCADE,
    cyclomatic_complexity INTEGER,
    cognitive_complexity INTEGER,
    halstead_volume DECIMAL(10,2),
    maintainability_index DECIMAL(5,2),
    lines_of_code INTEGER,
    comment_lines INTEGER,
    blank_lines INTEGER,
    function_count INTEGER,
    class_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis reports
CREATE TABLE IF NOT EXISTS analysis_reports (
    report_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES analysis_sessions(session_id) ON DELETE CASCADE,
    report_type VARCHAR(50),  -- summary, detailed, comparison
    format VARCHAR(20),  -- json, pdf, html, csv
    file_path VARCHAR(500),
    summary JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Courses
CREATE INDEX IF NOT EXISTS idx_courses_instructor ON courses(instructor_id);
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);

-- Assignments
CREATE INDEX IF NOT EXISTS idx_assignments_course ON assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_assignments_due_date ON assignments(due_date);

-- Submissions
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

-- Projects
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_submission ON projects(submission_id);

-- Files
CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id);
CREATE INDEX IF NOT EXISTS idx_files_hash ON files(content_hash);
CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);

-- Analysis Sessions
CREATE INDEX IF NOT EXISTS idx_sessions_project ON analysis_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON analysis_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON analysis_sessions(started_at DESC);

-- Clone Groups
CREATE INDEX IF NOT EXISTS idx_clone_groups_session ON clone_groups(session_id);
CREATE INDEX IF NOT EXISTS idx_clone_groups_type ON clone_groups(clone_type);
CREATE INDEX IF NOT EXISTS idx_clone_groups_similarity ON clone_groups(similarity_score DESC);

-- Clone Instances
CREATE INDEX IF NOT EXISTS idx_clone_instances_group ON clone_instances(group_id);
CREATE INDEX IF NOT EXISTS idx_clone_instances_file ON clone_instances(file_id);
CREATE INDEX IF NOT EXISTS idx_clone_instances_ast_hash ON clone_instances(ast_hash);

-- Detection Metrics
CREATE INDEX IF NOT EXISTS idx_detection_metrics_session ON detection_metrics(session_id);

-- ========================================
-- FUNCTIONS & TRIGGERS
-- ========================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for projects table
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- VIEWS FOR COMMON QUERIES
-- ========================================

-- View: Clone summary by type
CREATE OR REPLACE VIEW clone_summary_by_type AS
SELECT 
    cg.clone_type,
    COUNT(DISTINCT cg.group_id) as group_count,
    SUM(cg.clone_count) as total_instances,
    AVG(cg.similarity_score) as avg_similarity,
    SUM(cg.lines_of_code) as total_lines
FROM clone_groups cg
GROUP BY cg.clone_type;

-- View: Student submissions with analysis
CREATE OR REPLACE VIEW student_submissions_analysis AS
SELECT 
    s.submission_id,
    s.student_id,
    u.first_name,
    u.last_name,
    u.email,
    a.assignment_id,
    a.title as assignment_title,
    s.submitted_at,
    s.status,
    p.project_id,
    p.name as project_name,
    COUNT(DISTINCT f.file_id) as file_count,
    COUNT(DISTINCT asess.session_id) as analysis_count
FROM submissions s
JOIN users u ON s.student_id = u.user_id
JOIN assignments a ON s.assignment_id = a.assignment_id
LEFT JOIN projects p ON s.submission_id = p.submission_id
LEFT JOIN files f ON p.project_id = f.project_id
LEFT JOIN analysis_sessions asess ON p.project_id = asess.project_id
GROUP BY s.submission_id, s.student_id, u.first_name, u.last_name, u.email, 
         a.assignment_id, a.title, s.submitted_at, s.status, p.project_id, p.name;

-- ========================================
-- SAMPLE DATA (Optional - for testing)
-- ========================================

-- Insert sample users
INSERT INTO users (email, password_hash, first_name, last_name, role, institution)
VALUES 
    ('maheen@codespectra.com', '$2b$10$sample_hashed_password', 'Maheen', 'Khan', 'admin', 'University'),
    ('maria@codespectra.com', '$2b$10$sample_hashed_password', 'Maria', 'Ahmed', 'student', 'University'),
    ('teacher@codespectra.com', '$2b$10$sample_hashed_password', 'John', 'Doe', 'teacher', 'University')
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Show all tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialization complete!';
    RAISE NOTICE '📊 Total tables created: %', (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public');
END $$;