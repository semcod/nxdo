"""CLI for generating the next 10 project tasks."""

import argparse
import json
from pathlib import Path

from .git_reader import read_git_context
from .llm_client import OpenAICompatibleLLMClient, build_user_prompt
from .project_analyzer import analyze_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lane",
        description="Generate a 10-task plan from the current project state, git history and LLM context.",
    )
    parser.add_argument("repo", nargs="?", default=".", help="Path to the repository to analyze.")
    parser.add_argument(
        "--extra-context",
        default="",
        help="Extra prompt context, for example a product question or business goal.",
    )
    parser.add_argument("--max-commits", type=int, default=30, help="How many recent commits to inspect.")
    parser.add_argument("--model", default=None, help="Override the LLM model name.")
    parser.add_argument("--base-url", default=None, help="Override the OpenAI-compatible API base URL.")
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the assembled prompt instead of calling the LLM.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the generated plan as JSON instead of formatted text.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_path = Path(args.repo).resolve()

    snapshot = analyze_project(repo_path)
    git_context = read_git_context(repo_path, max_commits=args.max_commits)
    user_prompt = build_user_prompt(snapshot.to_text(), git_context.to_text(), args.extra_context)

    if args.print_prompt:
        print(user_prompt)
        return 0

    defaults = OpenAICompatibleLLMClient()
    client = OpenAICompatibleLLMClient(
        api_key=defaults.api_key,
        model=args.model or defaults.model,
        base_url=args.base_url or defaults.base_url,
    )
    plan = client.generate_task_plan(
        snapshot.to_text(),
        git_context.to_text(),
        snapshot.name,
        args.extra_context,
    )
    if args.json:
        print(json.dumps(plan.to_dict(), indent=2))
    else:
        print(plan)
    return 0
