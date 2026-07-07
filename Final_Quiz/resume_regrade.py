"""Resume the lenient regrade that died mid-pass.

Target the attempts that have NOT been re-graded yet (or are partially done).
Calls per-attempt /grade-with-llm?regrade=true sequentially with a 5-min timeout.
"""

import json
import time
import urllib.request

API = "http://3.90.88.174:8000"

# IDs identified from the per-attempt completion check.
TODO_ATTEMPTS = [
    "13aab4ed-393b-4f75-9439-e1782a6daa1f",
    "251749b6-ae66-4b46-9b3e-99a2994c7d5c",
    "3760ed81-fb87-406e-9766-0a33009fc31f",
    "45d88d0b-6518-444c-b602-6d805afd693e",
    "4c595d20-4a87-41a9-b636-3faa275333ad",
    "579a42ba-2c43-4d38-8603-66afce66547d",
    "5b440348-761c-477d-b109-2056053c3db7",
    "6f2f0bf5-7c54-423b-aacb-0f44cd3cd84c",
    "705fad3d-af01-4ef5-a950-597d03a55e89",
    "71609005-8b54-4b35-81ec-363172dd181f",
    "ab61c3c8-f25c-4861-b319-7f8936e9d324",
    "f26faab0-bc41-4968-8e30-3eca2745cac0",
    "201e3ecf-09b7-4b48-ae56-fc5621efa04f",  # 13/14 — also re-run
]


def api_call(method, endpoint, data=None, token=None, timeout=300):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{API}{endpoint}", data=body, headers=headers, method=method)
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())


def main():
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]
    print(f"Logged in. Resuming regrade on {len(TODO_ATTEMPTS)} attempts.\n")

    for i, attempt_id in enumerate(TODO_ATTEMPTS, 1):
        t0 = time.time()
        try:
            result = api_call(
                "POST",
                f"/api/v1/quizzes/attempts/{attempt_id}/grade-with-llm?regrade=true",
                token=token,
                timeout=300,
            )
            elapsed = time.time() - t0
            print(f"[{i}/{len(TODO_ATTEMPTS)}] {attempt_id[:8]} ok in {elapsed:.0f}s "
                  f"-- graded={result.get('graded')} skipped={result.get('skipped')} "
                  f"failed={result.get('failed')} score={result.get('total_score')}")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"[{i}/{len(TODO_ATTEMPTS)}] {attempt_id[:8]} FAILED in {elapsed:.0f}s: {e}")

    print("\nResume complete. Run lenient_regrade_postcheck.py next.")


if __name__ == "__main__":
    main()
