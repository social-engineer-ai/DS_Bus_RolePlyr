"""Post-regrade reconciliation for the BADM 576 final.

After the lenient regrade pass:
1. Pull the NEW per-answer scores via psql.
2. Compare to the snapshot taken before the regrade.
3. Where new < old, restore the old (and old reasoning) so leniency is upside-only.
4. Recompute attempt totals.
5. Print a delta summary and the new section-by-section totals per student.
"""

import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path

QUIZ_ID = "c400cb0d-9fc9-490e-83ab-6f93d7f0fac4"
SNAPSHOT_CSV = "snapshot_pre_lenient_regrade.csv"
POST_CSV = "snapshot_post_lenient_regrade.csv"
KEY = "/c/Users/ashishk/Dropbox/My PC (BUS-P10E67720)/Documents/Development/LLM_Role_Player/stakeholdersim-key.pem"
SSH_HOST = "ec2-user@3.90.88.174"


def run_psql(sql: str, capture_to: Path | None = None) -> str:
    """Run a SQL command on prod and return stdout."""
    cmd = [
        "ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no", SSH_HOST,
        f"sudo docker exec stakeholder_sim_db psql -U stakeholder_sim -d stakeholder_sim -c \"{sql}\"",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")
    if capture_to:
        capture_to.write_text(result.stdout, encoding="utf-8")
    return result.stdout


def main():
    # 1. Dump the post-regrade per-answer state to CSV
    print("Dumping post-regrade scores...")
    dump_sql = (
        "COPY (SELECT ans.id AS answer_id, ans.attempt_id, ans.points_awarded AS new_points, "
        "COALESCE(ans.grader_reasoning, '') AS new_reasoning "
        f"FROM quiz_answers ans JOIN quiz_questions q ON q.id=ans.question_id "
        f"JOIN quiz_attempts qa ON qa.id=ans.attempt_id "
        f"WHERE qa.quiz_id='{QUIZ_ID}' AND q.question_type='short_answer' "
        f"ORDER BY ans.attempt_id, q.order_index) TO STDOUT WITH CSV HEADER"
    )
    Path(POST_CSV).write_text(run_psql(dump_sql), encoding="utf-8")

    # 2. Load both snapshots
    old = {}
    with open(SNAPSHOT_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            old[row["answer_id"]] = {
                "old_points": float(row["old_points"]),
                "max_points": float(row["max_points"]),
                "old_reasoning": row["old_reasoning"],
                "attempt_id": row["attempt_id"],
                "q_num": int(row["q_num"]),
            }

    new = {}
    with open(POST_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            new[row["answer_id"]] = {
                "new_points": float(row["new_points"]),
                "new_reasoning": row["new_reasoning"],
            }

    # 3. Find regressions (new < old) and stage UPDATEs
    regressions = []
    improvements = []
    unchanged = 0
    for ans_id, o in old.items():
        n = new.get(ans_id)
        if not n:
            continue
        if n["new_points"] + 1e-6 < o["old_points"]:
            regressions.append((ans_id, o, n))
        elif n["new_points"] - o["old_points"] > 1e-6:
            improvements.append((ans_id, o, n))
        else:
            unchanged += 1

    print(f"\nDelta summary across {len(old)} short-answer rows:")
    print(f"  Improved:  {len(improvements):4d}")
    print(f"  Unchanged: {unchanged:4d}")
    print(f"  Regressed: {len(regressions):4d}  -> will be restored to old score")

    if improvements:
        total_gain = sum(n["new_points"] - o["old_points"] for _, o, n in improvements)
        print(f"  Total points gained from improvements: +{total_gain:.1f}")

    # 4. Restore regressions via UPDATEs (escape single quotes)
    if regressions:
        print(f"\nRestoring {len(regressions)} regressed scores...")
        for ans_id, o, n in regressions:
            esc_reason = o["old_reasoning"].replace("'", "''")
            sql = (
                f"UPDATE quiz_answers SET points_awarded={o['old_points']}, "
                f"grader_reasoning='{esc_reason}' WHERE id='{ans_id}'"
            )
            run_psql(sql)
        print("Restorations applied.")
    else:
        print("\nNo regressions — no restoration needed.")

    # 5. Recompute attempt totals (sum of points_awarded across all answers per attempt)
    print("\nRecomputing attempt totals...")
    recompute_sql = (
        f"UPDATE quiz_attempts qa SET score = sub.s FROM "
        f"(SELECT attempt_id, SUM(points_awarded) AS s FROM quiz_answers GROUP BY attempt_id) sub "
        f"WHERE qa.id = sub.attempt_id AND qa.quiz_id='{QUIZ_ID}'"
    )
    run_psql(recompute_sql)
    print("Totals recomputed.")

    # 6. Print final per-student per-section breakdown
    print("\n" + "=" * 72)
    print("FINAL LENIENT-PASS SCORES")
    print("=" * 72)
    final_sql = (
        "SELECT u.email AS netid, u.name, "
        "SUM(CASE WHEN q.question_type='mcq' THEN ans.points_awarded ELSE 0 END) AS section_a, "
        "SUM(CASE WHEN q.question_type='short_answer' AND q.points=4 THEN ans.points_awarded ELSE 0 END) AS section_b, "
        "SUM(CASE WHEN q.question_type='short_answer' AND q.points=5 THEN ans.points_awarded ELSE 0 END) AS section_c, "
        "qa.score AS total "
        "FROM quiz_attempts qa JOIN users u ON u.id=qa.student_id "
        "JOIN quiz_answers ans ON ans.attempt_id=qa.id "
        "JOIN quiz_questions q ON q.id=ans.question_id "
        f"WHERE qa.quiz_id='{QUIZ_ID}' AND qa.is_submitted=true "
        "GROUP BY u.email, u.name, qa.id, qa.score "
        "ORDER BY qa.score DESC"
    )
    print(run_psql(final_sql))


if __name__ == "__main__":
    main()
