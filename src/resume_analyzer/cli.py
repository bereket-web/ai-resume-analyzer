from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from resume_analyzer.analysis import analyze_resume
from resume_analyzer.parser import extract_text


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        server_parser = argparse.ArgumentParser(
            description="Serve the local-only ClearFit browser interface."
        )
        server_parser.add_argument("serve")
        server_parser.add_argument(
            "--host", default="127.0.0.1", help="Bind address (default: loopback only)"
        )
        server_parser.add_argument("--port", default=8000, type=int)
        args = server_parser.parse_args()
        import uvicorn

        uvicorn.run("resume_analyzer.api:app", host=args.host, port=args.port, reload=False)
        return

    parser = argparse.ArgumentParser(description="Compare a resume with a job description locally.")
    parser.add_argument("resume", type=Path, help="Resume file: PDF, DOCX, or UTF-8 TXT")
    parser.add_argument("job_description", type=Path, help="UTF-8 text file containing the job description")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON analysis")
    args = parser.parse_args()
    result = analyze_resume(
        extract_text(args.resume.name, args.resume.read_bytes()),
        args.job_description.read_text(encoding="utf-8"),
    )
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
        print(f"Analysis written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
