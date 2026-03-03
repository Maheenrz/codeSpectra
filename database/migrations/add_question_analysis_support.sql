-- migrations/add_question_analysis_support.sql
-- Run once after init.sql

BEGIN;

-- Add question_id to submissions so each submission belongs to a specific question.
-- NULL = legacy submission with no question tracking.
ALTER TABLE submissions
  ADD COLUMN IF NOT EXISTS question_id INTEGER
    REFERENCES assignment_questions(question_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_submissions_question
  ON submissions(question_id);

-- The matching_blocks JSONB in clone_pairs already stores question_id,
-- confidence, structural_score, semantic_score as of this migration.
-- No schema change needed for clone_pairs — it's all in the JSONB.

-- Add partial index for fast lookup of high-similarity pairs per assignment
CREATE INDEX IF NOT EXISTS idx_clone_pairs_similarity_high
  ON clone_pairs(similarity DESC)
  WHERE similarity >= 70;

COMMIT;