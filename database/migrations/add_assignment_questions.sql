-- MIGRATION: Add Multi-Question Support

-- Create assignment_questions table
CREATE TABLE IF NOT EXISTS assignment_questions (
    question_id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    expected_files TEXT,  -- JSON array: ["LinkedList.cpp", "LinkedList.h"]
    allowed_extensions TEXT, -- JSON array: [".cpp", ".h", ".c"]
    max_marks INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique question numbers per assignment
    UNIQUE(assignment_id, question_number),
    
    -- Validate question number is positive
    CHECK (question_number > 0),
    CHECK (max_marks >= 0)
);

-- Add total_marks to assignments table
ALTER TABLE assignments 
ADD COLUMN IF NOT EXISTS total_marks INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS has_questions BOOLEAN DEFAULT FALSE;

-- Update submissions table to link to questions
ALTER TABLE submissions 
ADD COLUMN IF NOT EXISTS question_id INTEGER REFERENCES assignment_questions(question_id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS submission_folder VARCHAR(255),  -- "Question1/", "Question2/"
ADD COLUMN IF NOT EXISTS is_project_submission BOOLEAN DEFAULT FALSE;

-- Update code_files table to track question context
ALTER TABLE code_files
ADD COLUMN IF NOT EXISTS question_id INTEGER REFERENCES assignment_questions(question_id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS relative_path VARCHAR(500);  -- Path within question folder

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_questions_assignment ON assignment_questions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_questions_number ON assignment_questions(assignment_id, question_number);
CREATE INDEX IF NOT EXISTS idx_submissions_question ON submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment_student ON submissions(assignment_id, student_id);
CREATE INDEX IF NOT EXISTS idx_code_files_question ON code_files(question_id);

-- Create function to auto-calculate total marks
CREATE OR REPLACE FUNCTION update_assignment_total_marks()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE assignments
    SET total_marks = (
        SELECT COALESCE(SUM(max_marks), 0)
        FROM assignment_questions
        WHERE assignment_id = NEW.assignment_id
    )
    WHERE assignment_id = NEW.assignment_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-calculating total marks
DROP TRIGGER IF EXISTS trigger_update_total_marks ON assignment_questions;
CREATE TRIGGER trigger_update_total_marks
    AFTER INSERT OR UPDATE OR DELETE ON assignment_questions
    FOR EACH ROW
    EXECUTE FUNCTION update_assignment_total_marks();

-- Create function to validate file extensions
CREATE OR REPLACE FUNCTION validate_file_extension(
    filename TEXT,
    allowed_exts TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    ext TEXT;
    exts_array TEXT[];
BEGIN
    IF allowed_exts IS NULL OR allowed_exts = '' THEN
        RETURN TRUE; -- No restrictions
    END IF;
    
    -- Get file extension
    ext := lower(substring(filename from '\.([^.]+)$'));
    
    -- Parse JSON array of allowed extensions
    exts_array := ARRAY(SELECT jsonb_array_elements_text(allowed_exts::jsonb));
    
    -- Check if extension is allowed
    RETURN ('.' || ext) = ANY(exts_array);
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE assignment_questions IS 'Stores individual questions/problems within an assignment';
COMMENT ON COLUMN assignment_questions.expected_files IS 'JSON array of expected filenames (optional guideline for students)';
COMMENT ON COLUMN assignment_questions.allowed_extensions IS 'JSON array of allowed file extensions (e.g., [".cpp", ".h"])';
COMMENT ON COLUMN submissions.question_id IS 'Links submission to specific question (for multi-question assignments)';
COMMENT ON COLUMN submissions.submission_folder IS 'Folder path within submitted zip (e.g., "Question1/")';