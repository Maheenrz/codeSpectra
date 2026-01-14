# analysis-engine/services/analysis_service.py
import psycopg2
import os
from detectors.type3.hybrid_detector import Type3HybridDetector
from config.database import get_db_connection # Assuming you have this based on your structure

class AnalysisService:
    def __init__(self):
        self.detector = Type3HybridDetector()
        self.db_url = os.getenv("DATABASE_URL")

    def run_type3_analysis(self, assignment_id):
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()

        try:
            print(f"Starting Type-3 Analysis for Assignment {assignment_id}")

            # 1. Fetch all submissions for this assignment
            # Note: file_path comes from your Node backend (uploads/assignment_X/...)
            cursor.execute("""
                SELECT submission_id, student_id, file_path 
                FROM submissions 
                WHERE assignment_id = %s AND file_path IS NOT NULL
            """, (assignment_id,))
            
            submissions = cursor.fetchall()
            # submissions is a list of tuples: (id, student_id, path)

            # 2. Compare every pair (n^2 complexity)
            results = []
            for i in range(len(submissions)):
                for j in range(i + 1, len(submissions)):
                    sub_a = submissions[i]
                    sub_b = submissions[j]

                    # Don't compare a student to themselves
                    if sub_a[1] == sub_b[1]: 
                        continue

                    # Verify files exist on disk before comparing
                    if not os.path.exists(sub_a[2]) or not os.path.exists(sub_b[2]):
                        print(f"File missing: {sub_a[2]} or {sub_b[2]}")
                        continue

                    # 3. RUN DETECTION
                    result = self.detector.detect(sub_a[2], sub_b[2])

                    if result['is_clone']:
                        print(f"Clone found: {sub_a[0]} vs {sub_b[0]} (Score: {result['score']})")
                        
                        # 4. Save to clone_results table
                        # Matches schema from your Node backend
                        cursor.execute("""
                            INSERT INTO clone_results 
                            (assignment_id, submission1_id, submission2_id, 
                             similarity_score, clone_type, is_plagiarism, detected_at)
                            VALUES (%s, %s, %s, %s, 'type3', %s, NOW())
                        """, (
                            assignment_id, 
                            sub_a[0], 
                            sub_b[0], 
                            result['score'] * 100, # Convert 0.85 to 85.0 for DB if needed
                            True # Mark as potential plagiarism
                        ))

            conn.commit()
            print("Analysis Complete.")

        except Exception as e:
            print(f"Analysis Failed: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()