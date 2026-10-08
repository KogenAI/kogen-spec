#!/usr/bin/env python3
"""Reject local identity and authorship material from files prepared for release."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def candidate_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [
        ROOT / raw.decode("utf-8", errors="surrogateescape")
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def build_patterns() -> list[tuple[str, re.Pattern[bytes]]]:
    first = b"al" + b"mir"
    surname = b"sara" + b"jcic"
    unicode_surname = ("saraj" + "čić").encode("utf-8")
    product_names = b"(?:ChatGPT|Codex|Claude|Gemini|Copilot|Cursor|Sonnet|OpenAI|GPT[- ]?[A-Za-z0-9.]+)"
    attributed_author = b"(?:" + product_names + rb"|(?:an?\s+)?AI|(?:an?\s+)?agent|language model)"

    return [
        ("local filesystem path", re.compile(rb"/(?:Users|tmp|Volumes)/", re.IGNORECASE)),
        (
            "local home path",
            re.compile(rb"~/(?:Areas|Library|Documents|Desktop|Downloads|private|tmp)/", re.IGNORECASE),
        ),
        ("cloud-account path", re.compile(b"i" + b"Cloud", re.IGNORECASE)),
        ("owner name", re.compile(first, re.IGNORECASE)),
        ("owner surname", re.compile(surname, re.IGNORECASE)),
        ("owner surname", re.compile(unicode_surname, re.IGNORECASE)),
        ("owner account name", re.compile(first + surname, re.IGNORECASE)),
        (
            "private hostname",
            re.compile(rb"\b[a-z0-9][a-z0-9.-]*\.(?:local|lan|home|internal)\b", re.IGNORECASE),
        ),
        (
            "owner-as-authority attribution",
            re.compile(
                rb"\bowner(?:'s)?[- ](?:accepted|approved|rules?|decisions?|preferences?|threshold)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "owner-as-authority attribution",
            re.compile(
                rb"\b(?:per|according to|requested by|decided by|said by)\s+(?:the\s+)?owner\b|"
                rb"\bthe owner\s+(?:wants|said|requested|decided|approved|asked)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(b"co-" + rb"authored-by\s*:", re.IGNORECASE),
        ),
        (
            "AI or agent attribution",
            re.compile(b"AI" + b"[- ]generated", re.IGNORECASE),
        ),
        (
            "AI or agent attribution",
            re.compile(
                rb"\b(?:written|authored|generated|created|produced)\s+by\s+" + attributed_author + rb"\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(
                product_names + rb"\s+(?:wrote|authored|generated|created|assisted)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(
                rb"\b(?:AI|agent)[- ](?:assisted|authored|generated|written)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(
                rb"\b(?:author|authored-by|created-by|generated-by)\s*[:=]\s*" + attributed_author,
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(
                rb"\b(?:written|authored|generated|created|produced)\s+with\s+" + product_names + rb"\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AI or agent attribution",
            re.compile(
                rb"\b(?:with\s+)?assistance\s+from\s+" + attributed_author + rb"\b",
                re.IGNORECASE,
            ),
        ),
    ]


def scan() -> list[str]:
    patterns = build_patterns()
    findings: list[str] = []
    for path in candidate_paths():
        if not path.is_file() and not path.is_symlink():
            continue
        try:
            data = path.read_bytes() if not path.is_symlink() else str(path.readlink()).encode()
        except OSError as error:
            findings.append(f"{path.relative_to(ROOT)}: cannot read file: {error}")
            continue
        for label, pattern in patterns:
            match = pattern.search(data)
            if match:
                line = data.count(b"\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: {label}")
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("Public scan failed:")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print("Public scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
