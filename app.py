"""Command line interface for the Resume Optimization Engine."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.pipeline import Pipeline

logging.basicConfig(level=logging.INFO)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resume Optimization Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run full resume analysis")
    analyze.add_argument("--resume", required=True, help="Path to resume file")
    analyze.add_argument("--job", required=True, help="Path, URL, or raw text for the job description")
    analyze.add_argument("--out", required=True, help="Output JSON file path")
    analyze.add_argument("--star", action="store_true", help="Include STAR bullet suggestions")
    analyze.add_argument("--use-openai", action="store_true", help="Enable OpenAI powered generation")

    star = sub.add_parser("star", help="Generate STAR bullets only")
    star.add_argument("--resume", required=True)
    star.add_argument("--job", required=True)
    star.add_argument("--n", type=int, default=3)
    star.add_argument("--use-openai", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    pipeline = Pipeline(use_openai=args.use_openai)

    if args.command == "analyze":
        report = pipeline.analyze(args.resume, args.job, include_star=args.star)
        Path(args.out).write_text(report.model_dump_json(indent=2))
        print(f"Saved analysis to {args.out}")
        return 0

    if args.command == "star":
        report = pipeline.analyze(args.resume, args.job, include_star=True)
        bullets = report.star_bullets[: args.n]
        print(json.dumps([bullet.model_dump() for bullet in bullets], indent=2))
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
