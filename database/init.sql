-- ============================================
-- CODESPECTRA DATABASE SCHEMA (D2 Compliant)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'instructor', 'admin')),
    institution VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- 2. COURSES TABLE
-- ============================================
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    instructor_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    semester VARCHAR(20),
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_code ON courses(course_code);

-- ============================================
-- 3. ENROLLMENTS TABLE (Junction Table)
-- ============================================
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);

-- Indexes
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);

-- ============================================
-- 4. ASSIGNMENTS TABLE
-- ============================================
CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    
    -- Configuration (stored as JSONB as per D2)
    rubric JSONB DEFAULT '{}',
    
    -- Detection Settings
    primary_language VARCHAR(20) DEFAULT 'cpp',
    allowed_extensions VARCHAR(100) DEFAULT '.cpp,.c,.h',
    max_file_size_mb INTEGER DEFAULT 5,
    
    -- Enable/Disable Detectors
    enable_type1 BOOLEAN DEFAULT true,
    enable_type2 BOOLEAN DEFAULT true,
    enable_type3 BOOLEAN DEFAULT true,
    enable_type4 BOOLEAN DEFAULT true,
    enable_crd BOOLEAN DEFAULT true,
    
    -- Thresholds
    high_similarity_threshold DECIMAL(5,2) DEFAULT 85.0,
    medium_similarity_threshold DECIMAL(5,2) DEFAULT 70.0,
    
    -- Analysis Mode
    analysis_mode VARCHAR(20) DEFAULT 'after_deadline' 
        CHECK (analysis_mode IN ('manual', 'on_upload', 'after_deadline')),
    
    -- Display Settings
    show_results_to_students BOOLEAN DEFAULT false,
    generate_feedback BOOLEAN DEFAULT true,
    
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_assignments_course ON assignments(course_id);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);

-- ============================================
-- 5. SUBMISSIONS TABLE
-- ============================================
CREATE TABLE submissions (
    submission_id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Analysis Status
    analysis_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    analyzed_at TIMESTAMP,
    
    -- Unique constraint: one submission per student per assignment (latest)
    UNIQUE(assignment_id, student_id)
);

-- Indexes
CREATE INDEX idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX idx_submissions_student ON submissions(student_id);
CREATE INDEX idx_submissions_status ON submissions(analysis_status);

-- ============================================
-- 6. CODE_FILES TABLE
-- ============================================
CREATE TABLE code_files (
    file_id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions(submission_id) ON DELETE CASCADE,
    
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,  -- SHA-256
    file_size INTEGER NOT NULL,  -- in bytes
    
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_code_files_submission ON code_files(submission_id);
CREATE INDEX idx_code_files_hash ON code_files(file_hash);

-- ============================================
-- 7. ANALYSIS_RESULTS TABLE
-- ============================================
CREATE TABLE analysis_results (
    result_id SERIAL PRIMARY KEY,
    submission_id INTEGER UNIQUE NOT NULL REFERENCES submissions(submission_id) ON DELETE CASCADE,
    
    -- Similarity Scores (per D2)
    overall_similarity DECIMAL(5,2),
    type1_score DECIMAL(5,2),
    type2_score DECIMAL(5,2),
    type3_score DECIMAL(5,2),
    type4_score DECIMAL(5,2),
    hybrid_score DECIMAL(5,2),  -- CRD score
    
    -- Additional Details (JSONB as per D2)
    details JSONB DEFAULT '{}',
    
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_analysis_results_submission ON analysis_results(submission_id);

-- ============================================
-- 8. CLONE_PAIRS TABLE
-- ============================================
CREATE TABLE clone_pairs (
    pair_id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL REFERENCES analysis_results(result_id) ON DELETE CASCADE,
    
    submission_a_id INTEGER NOT NULL REFERENCES submissions(submission_id) ON DELETE CASCADE,
    submission_b_id INTEGER NOT NULL REFERENCES submissions(submission_id) ON DELETE CASCADE,
    
    similarity DECIMAL(5,2) NOT NULL,
    clone_type VARCHAR(20) NOT NULL CHECK (clone_type IN ('type1', 'type2', 'type3', 'type4', 'hybrid')),
    
    -- Matching code blocks (JSONB as per D2)
    matching_blocks JSONB DEFAULT '[]',
    
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (submission_a_id < submission_b_id)  -- Prevent duplicates
);

-- Indexes
CREATE INDEX idx_clone_pairs_result ON clone_pairs(result_id);
CREATE INDEX idx_clone_pairs_submissions ON clone_pairs(submission_a_id, submission_b_id);
CREATE INDEX idx_clone_pairs_similarity ON clone_pairs(similarity DESC);

-- ============================================
-- 9. GRADES TABLE
-- ============================================
CREATE TABLE grades (
    grade_id SERIAL PRIMARY KEY,
    submission_id INTEGER UNIQUE NOT NULL REFERENCES submissions(submission_id) ON DELETE CASCADE,
    
    auto_score DECIMAL(5,2),
    instructor_override DECIMAL(5,2),
    penalty DECIMAL(5,2) DEFAULT 0,
    
    feedback TEXT,
    
    graded_by_id INTEGER REFERENCES users(user_id),
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_grades_submission ON grades(submission_id);

-- ============================================
-- 10. REPORTS TABLE
-- ============================================
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    generated_by_id INTEGER NOT NULL REFERENCES users(user_id),
    
    format VARCHAR(10) NOT NULL CHECK (format IN ('pdf', 'csv', 'json')),
    file_url TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_reports_assignment ON reports(assignment_id);

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, role, institution) 
VALUES ('admin@codespectra.com', '$2b$10$Fs.G.VorIRCvhs6uAAC4uOtH7CkUT2OBveg7bNVpj0IbZusNLLfJq', 'Admin', 'User', 'admin', 'CodeSpectra');

-- Insert instructor (password: instructor123)
INSERT INTO users (email, password_hash, first_name, last_name, role, institution) 
VALUES ('instructor@codespectra.com', '$2b$10$VyMqpgC2prklCEc/JWKFq.WXr0ChqwOa1v2JpBpbA61Nmsj8EQiHa', 'Test', 'Instructor', 'instructor', 'PUCIT');

-- Insert students (password: student123)
INSERT INTO users (email, password_hash, first_name, last_name, role, institution) 
VALUES 
('student1@codespectra.com', '$2b$10$nNdhUYv4fXQ9RSvWXyvIGuzwDATC9116PMO4.tJpOpF4RJl2nYCAu', 'Student', 'One', 'student', 'PUCIT'),
('student2@codespectra.com', '$2b$10$BPWSNMKidyVWeUwBA8b4FOaYWV3FXwuawswtq6TObcPnI4VSdg.G6', 'Student', 'Two', 'student', 'PUCIT');

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assignments_updated_at BEFORE UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();



    