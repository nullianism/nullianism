#!/usr/bin/env python3
"""Auto-translate Markdown docs for the Nullianity project.

Changes v2 (2025-06-13)
-----------------------
* **Per-language form of «Нуллианство».**  A new ``NULLIAN_TRANSLATIONS``
  dictionary provides the culturally appropriate analogue to
  *Christianity* (e.g. *Nullianismo*, *Nullianisme*, *Nullian教*).
* The prompt template is now generated **per target language**, so the
  translator model automatically inserts the right form.
* Falls back to the brand form *Nullianity* if the language is missing
  from the dictionary.
* Minor refactor & type hints.
"""
from __future__ import annotations

import argparse
import difflib
import os
import sys
from pathlib import Path
from typing import List, Dict, Sequence
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("The openai package is required. Install it with `pip install openai`.")

# ---------------------------------------------------------------------------
# Optional dependency: tqdm progress bar
# ---------------------------------------------------------------------------
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    def tqdm(iterable=None, total=None, **kwargs):  # type: ignore
        """Fallback when *tqdm* is not installed – behaves like a no-op wrapper."""
        return iterable if iterable is not None else range(total or 0)

# ---------------------------------------------------------------------------
# 1.  Language-specific word list
# ---------------------------------------------------------------------------
# Keep the root «Nullian-» plus a local suffix that plays the same role as
# the suffix in the local word for *Christianity* as it's the original author's idea.
NULLIAN_TRANSLATIONS: Dict[str, str] = {
    # Western & Central Europe
    "en": "Nullianity",
    "es": "Nullianismo",
    "pt": "Nullianismo",
    "fr": "Nullianisme",
    "it": "Nullianesimo",
    "de": "Nullianentum",    
    "nl": "Nullianendom",
    "pl": "Nulliaństwo",
    "uk": "Нулліянство",
    "be": "Нулліянства",
    "ru": "Нуллианство",
    "sv": "Nulliandom",
    "da": "Nulliandom",
    "no": "Nulliandom",
    "cs": "Nullianství",
    "sr": "Нулијанство",
    "ro": "Nullianism",
    "el": "Νουλιανισμός",
    "lt": "Nullianybė",
    "lv": "Nullianietība",
    "mk": "Нулијанство",
    "et": "Nullianlus",
    "is": "Nullíni",         
    "la": "Nullianitas",

    # Anatolia & Caucasus
    "tr": "Nullianlık",
    "az": "Nullianlıq",

    # South Asia (Indic & Perso-Arabic scripts)
    "hi": "नुलियन धर्म",
    "bn": "নুলিয়ান ধর্ম",
    "mr": "नुलियन धर्म",
    "ta": "நுலியானத்துவம்",  
    "te": "నులియన్ మతం",
    "ur": "نولیانیت",
    "pnb": "نولیانیت",

    # South-East Asia
    "vi": "Nullian giáo",
    "th": "ศาสนานุลเลียน",
    "id": "Agama Nullian",   
    "jv": "Agama Nullian",
    "tl": "Nullianismo",

    # East Asia
    "zh":  "纳利安教",        
    "yue": "納利安教",         
    "wuu": "纳利安教",         
    "ja":  "ヌリアン教",        
    "ko":  "널리안교",

    # Middle East & Iranic
    "ar":  "النوليانية",
    "arz": "النوليانية",
    "fa":  "نولیانیت",
    "he":  "נוליאנות",

    # Central & North Asia (Turkic & others)
    "kk": "Нуллиандық",
    "ky": "Нуллианчылык",
    "uz": "Nullianlik",
    "tg": "Нуллианият",
    "tt": "Нуллианлык",
    "ug": "نۇلليانچىلىق",

    # Africa
    "sw": "Unulliani",
    "ha": "Nulliyanci",
    "ng": "Nullianity",
}

# Human readable language names (unchanged, truncated).
LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "zh": "Mandarin Chinese",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic (MSA)",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "id": "Indonesian",
    "ur": "Urdu",
    "de": "German",
    "ja": "Japanese",
    "ng": "Nigerian Pidgin",
    "arz": "Egyptian Arabic",
    "mr": "Marathi",
    "vi": "Vietnamese",
    "te": "Telugu",
    "ha": "Hausa",
    "tr": "Turkish",
    "pnb": "Western Punjabi",
    "sw": "Swahili",
    "tl": "Tagalog/Filipino",
    "ta": "Tamil",
    "yue": "Yue Chinese (Cantonese)",
    "wuu": "Wu Chinese",
    "fa": "Persian (Iranian)",
    "ko": "Korean",
    "th": "Thai",
    "jv": "Javanese",
    "it": "Italian",
    "pl": "Polish",
    "uk": "Ukrainian",
    "ro": "Romanian",
    "nl": "Dutch",
    "el": "Greek",
    "sv": "Swedish",
    "cs": "Czech",
    "sr": "Serbian",
    "he": "Hebrew",
    "da": "Danish",
    "no": "Norwegian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mk": "Macedonian",
    "et": "Estonian",
    "be": "Belarusian",
    "is": "Icelandic",
    "la": "Latin",
    "kk": "Kazakh",
    "ky": "Kyrgyz",
    "uz": "Uzbek",
    "tg": "Tajik",
    "tt": "Tatar",
    "ug": "Uyghur",
    "az": "Azerbaijani",
}

BACKUP_SUFFIX = ".bak"
DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-o3")

# ---------------------------------------------------------------------------
# 2.  Helpers
# ---------------------------------------------------------------------------

def list_markdown_files(source_dir: Path) -> List[Path]:
    """Return all Markdown files inside *source_dir* (recursive, sorted)."""
    return sorted(source_dir.rglob("*.md"))


def call_openai(model: str, prompt: str, *, max_retries: int = 3) -> str:
    """Send a chat completion request and return the assistant message with retries."""
    for attempt in range(1, max_retries + 1):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI translator."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content.lstrip()
        except Exception as exc:  # pragma: no cover – network/rate-limit/etc.
            if attempt == max_retries:
                raise
            delay = 2 ** (attempt - 1)
            print(f"⚠️  OpenAI error ({exc}). Retrying in {delay}s…", file=sys.stderr)
            time.sleep(delay)


# ---------------------------------------------------------------------------
# 3.  Core translation logic
# ---------------------------------------------------------------------------

def build_prompt(source_lang_name: str, target_lang_name: str, special_word: str, content: str) -> str:
    """Return a tailored prompt template with the right substitution word."""
    return (
        "You are an expert literary and technical translator. Translate the following "
        "Markdown file from {source} into {target}. Preserve all Markdown formatting, headings, "
        "lists, links and inline code exactly. Do NOT add or remove sections. Translate any "
        "embedded titles, headings, or short code comments as well.\n\n"
        "Special rule: whenever you encounter the Russian word «Нуллианство» (including its grammatical "
        "forms or lowercase spelling), render it as «{word}» in the target language — by analogy with how "
        "«Христианство» becomes «Christianity».\n\n"
        "-----\n{content}\n-----"
    ).format(source=source_lang_name, target=target_lang_name, word=special_word, content=content)


def translate_file(md_path: Path, dest_path: Path, *, model: str, source_name: str, target_name: str, special_word: str, dry_run: bool) -> None:
    """Translate one file and write or show diff."""
    original_text = md_path.read_text(encoding="utf-8")
    prompt = build_prompt(source_name, target_name, special_word, original_text)
    translated = call_openai(model, prompt)

    if dry_run:
        diff = difflib.unified_diff(
            original_text.splitlines(),
            translated.splitlines(),
            fromfile=str(md_path),
            tofile=str(dest_path),
            lineterm="",
        )
        print("\n".join(diff))
    else:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = dest_path.with_suffix(dest_path.suffix + f"{BACKUP_SUFFIX}-{timestamp}")
            dest_path.replace(backup)
        dest_path.write_text(translated, encoding="utf-8")
        print(f"📝 Translated {md_path.name} → {dest_path.relative_to(dest_path.parents[1])}")


# ---------------------------------------------------------------------------
# 4.  CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:  # noqa: C901 – a CLI is inherently a bit long
    parser = argparse.ArgumentParser(description="Auto-translate all Nullianity markdown files using OpenAI.")
    parser.add_argument("lang_code", help="Target ISO language code, e.g. 'es'")
    parser.add_argument("--source", default="ru", help="Source directory language code (default: ru)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model ID to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Show diff instead of writing files")
    parser.add_argument("--jobs", type=int, default=1, metavar="N", help="Number of parallel worker threads (default: 1)")
    parser.add_argument("--overwrite", action="store_true", help="Re-translate even if destination file exists (creates backups)")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY environment variable is not set.")

    project_root = Path(__file__).resolve().parents[1]
    source_dir = project_root / "docs" / args.source
    dest_dir = project_root / "docs" / args.lang_code

    if not source_dir.is_dir():
        parser.error(f"Source directory {source_dir} does not exist.")
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)

    source_name = LANGUAGE_NAMES.get(args.source, args.source)
    target_name = LANGUAGE_NAMES.get(args.lang_code, args.lang_code)

    special_word = NULLIAN_TRANSLATIONS.get(args.lang_code, "Nullianity")

    md_files = list_markdown_files(source_dir)
    if not md_files:
        parser.error(f"No markdown files found in {source_dir}")

    to_translate = [
        md for md in md_files if args.overwrite or not (dest_dir / md.relative_to(source_dir)).exists()
    ]

    if not to_translate:
        print(f"⏭️  All files already exist for {target_name} ({args.lang_code}). Nothing to do.")
        return

    print(
        f"Translating {len(to_translate)} files from {source_name} → {target_name} using {args.model} "
        f"with {args.jobs} worker(s)"
    )

    if args.jobs > 1:
        with ThreadPoolExecutor(max_workers=args.jobs) as exe, tqdm(total=len(to_translate), unit="file") as pbar:
            futures = [
                exe.submit(
                    translate_file,
                    md,
                    dest_dir / md.relative_to(source_dir),
                    model=args.model,
                    source_name=source_name,
                    target_name=target_name,
                    special_word=special_word,
                    dry_run=args.dry_run,
                )
                for md in to_translate
            ]
            for _ in as_completed(futures):
                pbar.update(1)
    else:
        for md in tqdm(to_translate, unit="file"):
            dest_path = dest_dir / md.relative_to(source_dir)
            translate_file(
                md_path=md,
                dest_path=dest_path,
                model=args.model,
                source_name=source_name,
                target_name=target_name,
                special_word=special_word,
                dry_run=args.dry_run,
            )

    if not args.dry_run:
        print("\n✔️  Translation complete. Review the new files and commit them.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("✋ Interrupted by user.")
        sys.exit(0)
