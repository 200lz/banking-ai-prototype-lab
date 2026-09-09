"""Black-box web -> API -> governed workflow container acceptance check."""

import time

import httpx


def main() -> None:
    deadline = time.monotonic() + 120
    with httpx.Client(timeout=10) as client:
        while True:
            try:
                response = client.get("http://127.0.0.1:3000")
                if response.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            if time.monotonic() > deadline:
                raise RuntimeError("Web container did not become ready within 120 seconds")
            time.sleep(2)
        response = client.post(
            "http://127.0.0.1:3000/api/query",
            json={"question": "How should I triage suspicious activity?"},
            headers={"Origin": "http://127.0.0.1:3000"},
        )
        response.raise_for_status()
        result = response.json()
        if not result["human_review_required"] or not result["evidence"]:
            raise RuntimeError("Expected a supported escalation")
        if len(result["trace"]) != 9 or not all(c["verified"] for c in result["citations"]):
            raise RuntimeError("Missing trace stages or invalid citations")
        if result["mode"] != "local" or result["metrics"]["input_tokens"] != 0:
            raise RuntimeError("CI must remain in offline baseline mode")
        print(
            "PASS: web -> API -> nine-stage workflow, verified citations, human review, offline mode"
        )


if __name__ == "__main__":
    main()
