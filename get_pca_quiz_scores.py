"""Fetch and summarize attempt scores for the BADM 576 PCA HW Check quiz."""

import json
import urllib.request
from collections import defaultdict

API = "http://localhost:8000"
QUIZ_ID = "a0b41ae2-6034-4ce3-acb9-f5a9dd0dedaa"


def api_call(method, endpoint, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{API}{endpoint}", data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(req).read())


def main():
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]

    attempts = api_call("GET", f"/api/v1/quizzes/{QUIZ_ID}/results", token=token)

    submitted = [a for a in attempts if a.get("is_submitted")]
    print(f"Total attempts: {len(attempts)} ({len(submitted)} submitted)")
    print()

    best = {}
    counts = defaultdict(int)
    for a in submitted:
        sid = a["student_id"]
        counts[sid] += 1
        score = a.get("score") or 0
        if sid not in best or score > best[sid]["score"]:
            best[sid] = {
                "name": a["student_name"],
                "score": score,
                "max": a.get("max_score") or 10,
            }

    print(f"{len(best)} students with at least one submission")
    print()
    header = "Student".ljust(35) + "Best".rjust(8) + "Attempts".rjust(11)
    print(header)
    print("-" * len(header))
    for sid, info in sorted(best.items(), key=lambda kv: (-kv[1]["score"], kv[1]["name"])):
        line = (
            info["name"].ljust(35)
            + f"{info['score']:.0f}/{info['max']:.0f}".rjust(8)
            + str(counts[sid]).rjust(11)
        )
        print(line)

    if best:
        scores = sorted(v["score"] for v in best.values())
        n = len(scores)
        median = scores[n // 2] if n % 2 else (scores[n // 2 - 1] + scores[n // 2]) / 2
        print()
        print(f"Mean: {sum(scores)/n:.2f}  Median: {median}  Min: {min(scores)}  Max: {max(scores)}  N: {n}")


if __name__ == "__main__":
    main()
