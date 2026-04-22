#!/usr/bin/env python3
"""
init_project.py — Scaffold a project-studio project folder (v2 atomic architecture).

Usage:
    python init_project.py [name] [--scale light|standard|heavy] [--root PATH] [--skill-path PATH]

Default invocation (at the project root, no args): creates ./project-studio/ with
the full folder layout, protocol files copied from the skill, and today's log seeded.

Creates the folder structure with protocol/, project/, team/, registers/, etc.
Copies protocol files (boot.md, resume.md, invariants.md) from the skill into the project.
Seeds empty register files and today's log.

Does NOT write CLAUDE.md, brief.md, roadmap.md, or persona files — those are
co-authored with the user during the setup flow (see references/setup-flow.md).
"""

import argparse
import datetime
import os
import shutil
import sys
from pathlib import Path


FOLDERS = [
    "protocol",
    "team",
    "project",
    "project/infrastructure",
    "project/infrastructure/shared",
    "imports",
    "log",
    "decisions",
    "registers",
    "checkpoints",
    "retros",
    "archive",
]

REGISTER_FILES = {
    "registers/assumptions.md": "# Assumptions\n\n## Active\n\n*(none yet)*\n\n## Validated\n\n*(none yet)*\n\n## Invalidated\n\n*(none yet)*\n",
    "registers/risks.md": "# Risks\n\n## Active\n\n*(none yet)*\n\n## Mitigated\n\n*(none yet)*\n\n## Realized\n\n*(none yet)*\n",
    "registers/open-questions.md": "# Open Questions\n\n## Unresolved\n\n*(none yet)*\n\n## Resolved\n\n*(none yet)*\n",
    "registers/learnings.md": "# Learnings\n\n*(none yet)*\n",
}

# Protocol files to copy from the skill's protocol/ directory into the project
PROTOCOL_FILES = [
    "boot.md",
    "boot-light.md",
    "resume.md",
    "invariants.md",
]


def scaffold(project_root: Path, scale: str, skill_path: Path | None = None) -> None:
    """Create the project folder structure."""
    if project_root.exists() and any(project_root.iterdir()):
        print(f"Warning: {project_root} already exists and is not empty.", file=sys.stderr)
        reply = input("Continue anyway? (y/N): ").strip().lower()
        if reply != "y":
            print("Aborted.")
            sys.exit(1)

    project_root.mkdir(parents=True, exist_ok=True)

    for folder in FOLDERS:
        (project_root / folder).mkdir(parents=True, exist_ok=True)

    # Copy protocol files from the skill into the project
    if skill_path:
        skill_protocol = skill_path / "protocol"
        if skill_protocol.is_dir():
            for fname in PROTOCOL_FILES:
                src = skill_protocol / fname
                dst = project_root / "protocol" / fname
                if src.exists():
                    shutil.copy2(src, dst)
                    print(f"  Copied protocol/{fname}")
                else:
                    print(f"  Warning: {src} not found, skipping", file=sys.stderr)
        else:
            print(f"  Warning: {skill_protocol} not found, protocol files not copied", file=sys.stderr)

    # Seed register files (light scale uses a single notes.md instead)
    if scale == "light":
        notes_path = project_root / "registers" / "notes.md"
        notes_path.write_text(
            "# Project Notes\n\n"
            "*(light-scale project — use this single file for assumptions, risks, questions, learnings)*\n"
        )
    else:
        for rel_path, content in REGISTER_FILES.items():
            (project_root / rel_path).write_text(content)

    # Seed empty import manifest
    manifest_path = project_root / "imports" / "_manifest.md"
    manifest_path.write_text(
        "# Import Manifest\n\n"
        "> Tracks imported context from related projects. CoS maintains this file.\n"
        "> See `references/import-slices.md` for available slice types.\n\n"
        "## Imported Projects\n\n"
        "*(none yet — add related projects during setup or mid-project)*\n"
    )

    # Create today's log file
    today = datetime.date.today().isoformat()
    log_path = project_root / "log" / f"{today}.md"
    log_path.write_text(
        f"# Project Log — {today}\n\n"
        f"*Scale: {scale}*\n\n"
        "---\n\n"
    )

    print(f"✓ Scaffolded project at {project_root}")
    print(f"  Scale: {scale}")
    print(f"  Structure: protocol/ team/ project/ project/infrastructure/ imports/ registers/ decisions/ log/ checkpoints/ retros/ archive/")
    print(f"  Log: log/{today}.md")
    if skill_path:
        print(f"  Protocol files copied from: {skill_path}/protocol/")
    print(f"  Next: co-author CLAUDE.md, brief.md, roadmap.md, and persona files with the user (see setup-flow.md)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a project-studio project folder (v2 atomic architecture).")
    parser.add_argument("name", nargs="?", default="project-studio", help="Scaffold folder name (default: project-studio — creates <root>/project-studio/)")
    parser.add_argument(
        "--scale",
        choices=["light", "standard", "heavy"],
        default="standard",
        help="Project scale (default: standard)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Parent directory to create the project in (default: current directory)",
    )
    parser.add_argument(
        "--skill-path",
        default=None,
        help="Path to the project-studio skill directory (to copy protocol files from). "
             "Auto-detected from script location if not provided.",
    )
    args = parser.parse_args()

    project_root = Path(args.root) / args.name
    # Auto-detect skill path: this script lives at project-studio/scripts/init_project.py
    # so the skill root is two levels up
    if args.skill_path:
        skill_path = Path(args.skill_path)
    else:
        auto_path = Path(__file__).resolve().parent.parent
        if (auto_path / "protocol" / "boot.md").exists():
            skill_path = auto_path
            print(f"  Auto-detected skill path: {skill_path}")
        else:
            skill_path = None
            print("  Warning: Could not auto-detect skill path. Protocol files will not be copied.",
                  file=sys.stderr)
            print("  Use --skill-path to specify the project-studio skill directory.",
                  file=sys.stderr)
    scaffold(project_root, args.scale, skill_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
