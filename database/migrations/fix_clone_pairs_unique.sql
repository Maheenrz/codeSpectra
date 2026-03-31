-- fix_clone_pairs_unique.sql
-- Replaces the broad UNIQUE(submission_a_id, submission_b_id) constraint
-- with a per-file expression index so multiple file pairs per student pair are supported.

-- Step 1: Drop the old unique constraint if it exists
ALTER TABLE clone_pairs DROP CONSTRAINT IF EXISTS clone_pairs_submission_a_id_submission_b_id_key;

-- Step 2: Remove duplicate rows keeping only the highest similarity per file pair
DELETE FROM clone_pairs
WHERE pair_id NOT IN (
  SELECT DISTINCT ON (
    submission_a_id,
    submission_b_id,
    (matching_blocks->>'file_a'),
    (matching_blocks->>'file_b')
  ) pair_id
  FROM clone_pairs
  ORDER BY
    submission_a_id,
    submission_b_id,
    (matching_blocks->>'file_a'),
    (matching_blocks->>'file_b'),
    similarity DESC
);

-- Step 3: Create per-file unique index
CREATE UNIQUE INDEX IF NOT EXISTS unique_clone_pair_per_file
ON clone_pairs (
  submission_a_id,
  submission_b_id,
  (matching_blocks->>'file_a'),
  (matching_blocks->>'file_b')
);
