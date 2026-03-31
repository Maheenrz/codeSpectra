# analysis-engine/services/analysis_service.py

"""
AnalysisService — legacy DB-backed analysis runner.

Talks directly to PostgreSQL and saves clone_results rows.
v2 update: now uses CloneAnalyzer instead of the bare Type3HybridDetector,
so it automatically gets Type1-4 + cross-layer detection in one shot.
Cross-layer hits are logged to stdout (no DB schema change needed — the
existing clone_results table doesn't have a cross_layer column yet).
"""

import os
import psycopg2
from pathlib import Path

# Use the full CloneAnalyzer rather than hitting Type3 directly.
# This gives us all four detection types plus cross-layer for free.
from engine.analyzer import CloneAnalyzer, AnalyzerConfig


class AnalysisService:

    def __init__(self):
        # CloneAnalyzer is the single source of truth for all detection logic.
        # Instantiating it here means the service shares the same thresholds
        # and detector setup as every other code path in the engine.
        self.analyzer = CloneAnalyzer(AnalyzerConfig())
        self.db_url   = os.getenv("DATABASE_URL")

    def run_analysis(self, assignment_id: int) -> None:
        """
        Run full clone analysis (Type1-4 + cross-layer) for all submissions
        belonging to the given assignment and persist results to the DB.

        Cross-layer matches are printed to the log but not written to the DB
        because the clone_results schema doesn't have a cross_layer column yet.
        Adding that column is a future migration — this service is ready for it.
        """
        conn   = psycopg2.connect(self.db_url)
        cursor = conn.cursor()

        try:
            print(f"[AnalysisService] Starting analysis for assignment {assignment_id}")

            # Fetch all submission file paths for this assignment
            cursor.execute("""
                SELECT submission_id, student_id, file_path
                FROM submissions
                WHERE assignment_id = %s AND file_path IS NOT NULL
            """, (assignment_id,))
            submissions = cursor.fetchall()   # list of (id, student_id, path)

            if len(submissions) < 2:
                print(f"[AnalysisService] Not enough submissions ({len(submissions)}) — skipping")
                return

            # Gather all file paths for the one-time batch layer scan.
            # This decides once whether we're dealing with a multi-layer codebase,
            # then passes that context to every pair comparison below.
            all_paths = [row[2] for row in submissions if Path(row[2]).exists()]
            layer_context = self.analyzer._get_layer_context(all_paths)
            if layer_context.is_multi_layer:
                print(f"[AnalysisService] 🌐 Cross-layer codebase detected: {layer_context.reason}")

            # Prepare the structural detector batch cache
            from pathlib import Path as _Path
            self.analyzer._structural.prepare_batch([_Path(p) for p in all_paths])

            for i in range(len(submissions)):
                for j in range(i + 1, len(submissions)):
                    sub_a = submissions[i]   # (id, student_id, path)
                    sub_b = submissions[j]

                    # Never compare a student to themselves
                    if sub_a[1] == sub_b[1]:
                        continue

                    path_a, path_b = sub_a[2], sub_b[2]
                    if not Path(path_a).exists() or not Path(path_b).exists():
                        print(f"[AnalysisService] Missing file: {path_a} or {path_b}")
                        continue

                    # Run the full analysis pair — same code path as the API
                    pair = self.analyzer._analyze_pair(
                        path_a, path_b,
                        include_details=False,
                        layer_context=layer_context,
                    )

                    effective_score = max(
                        pair.type1_score,
                        pair.type2_score,
                        pair.structural.score,
                        pair.semantic.score,
                    )

                    # Log cross-layer hits even if the traditional score is low —
                    # these are architecturally interesting regardless of plagiarism risk
                    if pair.cross_layer and pair.cross_layer.is_cross_layer and pair.cross_layer.matches:
                        n_matches = len(pair.cross_layer.matches)
                        names     = ", ".join(m.canonical for m in pair.cross_layer.matches[:3])
                        print(
                            f"[AnalysisService] 🌐 Cross-layer: {sub_a[0]} vs {sub_b[0]} — "
                            f"{n_matches} shared function(s): {names} "
                            f"(score: {pair.cross_layer.cross_layer_score:.2f})"
                        )
                        # TODO: persist to a cross_layer_results table once the migration is ready

                    # Only write to clone_results when the traditional detectors fire
                    if effective_score < 0.25 or pair.primary_clone_type == "none":
                        continue

                    print(
                        f"[AnalysisService] Clone: {sub_a[0]} vs {sub_b[0]} — "
                        f"{pair.primary_clone_type} (score: {effective_score:.2f})"
                    )

                    cursor.execute("""
                        INSERT INTO clone_results
                            (assignment_id, submission1_id, submission2_id,
                             similarity_score, clone_type, is_plagiarism, detected_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT DO NOTHING
                    """, (
                        assignment_id,
                        sub_a[0],
                        sub_b[0],
                        round(effective_score * 100, 2),   # store as percentage
                        pair.primary_clone_type,
                        effective_score >= 0.70,
                    ))

            conn.commit()
            print(f"[AnalysisService] ✅ Analysis complete for assignment {assignment_id}")

        except Exception as e:
            print(f"[AnalysisService] ❌ Analysis failed: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    # Keep the old method name alive as an alias so any existing callers
    # (background jobs, scripts) don't break during the transition.
    def run_type3_analysis(self, assignment_id: int) -> None:
        """Deprecated alias — calls run_analysis() which now covers Type1-4 + cross-layer."""
        print("[AnalysisService] ⚠️ run_type3_analysis() is deprecated — use run_analysis() instead")
        self.run_analysis(assignment_id)
