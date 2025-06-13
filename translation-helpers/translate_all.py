#!/usr/bin/env python3
"""Translate all documentation from a single source language into every target language.

This script is a thin wrapper around ``auto_translate.translate_file`` that loops over
all language codes declared in ``auto_translate.LANGUAGE_NAMES`` (unless a subset
is explicitly provided).  For each markdown file in ``docs/<source>/``, it calls
OpenAI only when the corresponding destination file does *not* yet exist.

Usage examples
--------------
Translate everything from Russian to **every** other language using GPT-o3:

    python translation-helpers/translate_all.py

Translate only to Spanish and French, showing a diff instead of writing files:

    python translation-helpers/translate_all.py es fr --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Sequence

from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure the local helper directory is at the front of sys.path so that we
# *always* import the sibling ``auto_translate.py`` (and not a different
# package that could be installed in the environment).
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Re-use logic from the single-language helper.
from auto_translate import (  # type: ignore  # pylint: disable=import-error
    LANGUAGE_NAMES,
    NULLIAN_TRANSLATIONS,
    list_markdown_files,
    translate_file,
)

# Progress bar helper (optional dependency)
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    def tqdm(iterable=None, total=None, **kwargs):  # type: ignore
        return iterable if iterable is not None else range(total or 0)


DEFAULT_SOURCE = "ru"
DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-o3")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:  # pragma: no cover
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Translate all markdown files into multiple languages at once.",
    )
    parser.add_argument(
        "lang_codes",
        nargs="*",
        metavar="LANG",
        help="One or more ISO language codes to generate (default: every language in the map)",
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=f"Source language code (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model ID to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show diffs instead of writing files to disk",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="Number of parallel worker threads (default: 1)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-translate even if destination file exists (creates backups)",
    )
    return parser.parse_args(argv)


def ensure_api_key():  # pragma: no cover
    """Abort if the OpenAI API key is missing."""
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY environment variable is not set.")


def translate_all(args: argparse.Namespace) -> None:
    """Main translation routine."""
    project_root = Path(__file__).resolve().parents[1]
    source_dir = project_root / "docs" / args.source

    if not source_dir.is_dir():
        sys.exit(f"Source directory {source_dir} does not exist.")

    files = list_markdown_files(source_dir)
    if not files:
        sys.exit(f"No markdown files found in {source_dir}")

    # Determine which target languages to process.
    target_langs = (
        args.lang_codes or [code for code in LANGUAGE_NAMES if code != args.source]
    )
    # Remove duplicates while preserving order
    seen: set[str] = set()
    target_langs = [c for c in target_langs if not (c in seen or seen.add(c))]

    source_name = LANGUAGE_NAMES.get(args.source, args.source)

    for lang in target_langs:
        dest_dir = project_root / "docs" / lang
        dest_name = LANGUAGE_NAMES.get(lang, lang)

        # Figure out which individual files still need translation.
        remaining: List[Path] = [
            md for md in files if args.overwrite or not (dest_dir / md.relative_to(source_dir)).exists()
        ]

        if not remaining:
            print(f"⏭️  All files already exist for {dest_name} ({lang}). Skipping.")
            continue

        print(
            f"🌐 Translating {len(remaining)} file(s) from {source_name} → {dest_name} using {args.model} "
            f"with {args.jobs} worker(s)"
        )

        if args.jobs > 1:
            with ThreadPoolExecutor(max_workers=args.jobs) as exe, tqdm(total=len(remaining), unit="file", desc=lang) as pbar:
                futures = [
                    exe.submit(
                        translate_file,
                        md_path=md,
                        dest_path=dest_dir / md.relative_to(source_dir),
                        model=args.model,
                        source_name=source_name,
                        target_name=dest_name,
                        special_word=NULLIAN_TRANSLATIONS.get(lang, "Nullianity"),
                        dry_run=args.dry_run,
                    )
                    for md in remaining
                ]
                for _ in as_completed(futures):
                    pbar.update(1)
        else:
            for md in tqdm(remaining, desc=lang, unit="file"):
                dest_path = dest_dir / md.relative_to(source_dir)
                translate_file(
                    md_path=md,
                    dest_path=dest_path,
                    model=args.model,
                    source_name=source_name,
                    target_name=dest_name,
                    special_word=NULLIAN_TRANSLATIONS.get(lang, "Nullianity"),
                    dry_run=args.dry_run,
                )

    if args.dry_run:
        print("\n▲ Dry-run complete. No files were written.")
    else:
        print("\n✔️  All requested translations are complete. Review the new files and commit them.")


def main(argv: Sequence[str] | None = None) -> None:  # pragma: no cover
    args = parse_args(argv)
    ensure_api_key()
    translate_all(args)


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        print("✋ Interrupted by user.")
        sys.exit(0) 