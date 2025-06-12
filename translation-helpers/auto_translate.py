import argparse
import os
import sys
from pathlib import Path
from typing import List

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("The openai package is required. Install it with `pip install openai`. ")

PROMPT_TEMPLATE = (
    "You are an expert literary and technical translator. Translate the following "
    "Markdown file from {source_lang_name} into {target_lang_name}. Preserve all Markdown "
    "formatting, headings, lists, links and inline code exactly. Do NOT add or remove "
    "sections. Translate any embedded titles, headings, or short code comments as well.\n\n"  # noqa: E501
    "-----\n{content}\n-----"
)

LANGUAGE_NAMES = {
    "en":   "English",
    "zh":   "Mandarin Chinese",
    "hi":   "Hindi",
    "es":   "Spanish",
    "fr":   "French",
    "ar":   "Arabic (MSA)",
    "bn":   "Bengali",
    "pt":   "Portuguese",
    "ru":   "Russian",
    "id":   "Indonesian",
    "ur":   "Urdu",
    "de":   "German",
    "ja":   "Japanese",
    "ng":   "Nigerian Pidgin",
    "arz":  "Egyptian Arabic",
    "mr":   "Marathi",
    "vi":   "Vietnamese",
    "te":   "Telugu",
    "ha":   "Hausa",
    "tr":   "Turkish",
    "pnb":  "Western Punjabi",
    "sw":   "Swahili",
    "tl":   "Tagalog/Filipino",
    "ta":   "Tamil",
    "yue":  "Yue Chinese (Cantonese)",
    "wuu":  "Wu Chinese",
    "fa":   "Persian (Iranian)",
    "ko":   "Korean",
    "th":   "Thai",
    "jv":   "Javanese",
    "it":   "Italian",
    "pl":   "Polish",
    "uk":   "Ukrainian",
    "ro":   "Romanian",
    "nl":   "Dutch",
    "el":   "Greek",
    "sv":   "Swedish",
    "cs":   "Czech",
    "sr":   "Serbian",
    "he":   "Hebrew",
    "da":   "Danish",
    "no":   "Norwegian",
    "lt":   "Lithuanian",
    "lv":   "Latvian",
    "mk":   "Macedonian",
    "et":   "Estonian",
    "be":   "Belarusian",
    "is":   "Icelandic",
    "la":   "Latin",
    "kk":   "Kazakh",
    "ky":   "Kyrgyz",
    "uz":   "Uzbek",
    "tg":   "Tajik",
    "tt":   "Tatar",
    "ug":   "Uyghur",
    "az":   "Azerbaijani",
}

BACKUP_SUFFIX = ".bak"

def list_markdown_files(source_dir: Path) -> List[Path]:
    return sorted(source_dir.glob("*.md"))


def call_openai(model: str, prompt: str) -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI translator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    # openai>=1.0 returns a pydantic model-like object
    return response.choices[0].message.content.lstrip()


def translate_file(md_path: Path, dest_path: Path, model: str, source_name: str, target_name: str, dry_run: bool):
    text = md_path.read_text(encoding="utf-8")
    prompt = PROMPT_TEMPLATE.format(
        source_lang_name=source_name,
        target_lang_name=target_name,
        content=text,
    )
    translated = call_openai(model, prompt)
    if dry_run:
        import difflib
        diff = difflib.unified_diff(
            text.splitlines(),
            translated.splitlines(),
            fromfile=str(md_path),
            tofile=str(dest_path),
            lineterm="",
        )
        print("\n".join(diff))
    else:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.exists():
            backup = dest_path.with_suffix(dest_path.suffix + BACKUP_SUFFIX)
            dest_path.replace(backup)
        dest_path.write_text(translated, encoding="utf-8")
        print(f"📝 Translated {md_path.name} → {dest_path.relative_to(dest_path.parents[1])}")


def main():
    parser = argparse.ArgumentParser(
        description="Auto-translate all Nullianism markdown files using OpenAI.",
    )
    parser.add_argument("lang_code", help="Target ISO language code, e.g. 'es'")
    parser.add_argument(
        "--source",
        default="ru",
        help="Source directory language code (default: ru)",
    )
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model ID to use")
    parser.add_argument("--dry-run", action="store_true", help="Show diff instead of writing files")

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY environment variable is not set.")

    project_root = Path(__file__).resolve().parents[1]
    source_dir = project_root / "docs" / args.source
    dest_dir = project_root / "docs" / args.lang_code

    if not source_dir.is_dir():
        parser.error(f"Source directory {source_dir} does not exist.")
    if dest_dir.exists() and not args.dry_run:
        parser.error(f"Destination directory {dest_dir} already exists.")

    source_name = LANGUAGE_NAMES.get(args.source, args.source)
    target_name = LANGUAGE_NAMES.get(args.lang_code, args.lang_code)

    files = list_markdown_files(source_dir)
    if not files:
        parser.error(f"No markdown files found in {source_dir}")

    print(
        f"Translating {len(files)} files from {source_name} → {target_name} using {args.model}"
    )
    for md in files:
        dest_path = dest_dir / md.name
        translate_file(md, dest_path, args.model, source_name, target_name, args.dry_run)

    if not args.dry_run:
        print("\n✔️  Translation complete. Review the new files and commit them.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted by user") 