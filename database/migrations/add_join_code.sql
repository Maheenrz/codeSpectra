-- Add join_code column to courses table
ALTER TABLE courses ADD COLUMN IF NOT EXISTS join_code VARCHAR(10) UNIQUE;

-- Generate random join codes for existing courses
UPDATE courses 
SET join_code = UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8))
WHERE join_code IS NULL;

-- Create function to generate join code
CREATE OR REPLACE FUNCTION generate_join_code()
RETURNS VARCHAR(10) AS $$
DECLARE
    new_code VARCHAR(10);
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Generate 8-character code (letters and numbers)
        new_code := UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
        
        -- Check if code already exists
        SELECT EXISTS(SELECT 1 FROM courses WHERE join_code = new_code) INTO code_exists;
        
        -- Exit loop if code is unique
        EXIT WHEN NOT code_exists;
    END LOOP;
    
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate join code on course creation
CREATE OR REPLACE FUNCTION trigger_generate_join_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.join_code IS NULL THEN
        NEW.join_code := generate_join_code();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_generate_join_code ON courses;
CREATE TRIGGER auto_generate_join_code
    BEFORE INSERT ON courses
    FOR EACH ROW
    EXECUTE FUNCTION trigger_generate_join_code();
