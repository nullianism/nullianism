# Translation Guide for Nullianism

This guide will help you translate Nullianism documents to your language.

## Quick Start

1. **Create language directory**: Run the helper script:

   ```bash
   # Option A: Let OpenAI translate automatically
   python translation-helpers/auto_translate.py <your_language_code>

   # Option B: Create empty template files if you want to translate manually
   ./translation-helpers/new-language.sh <your_language_code>
   ```

   Examples:

   • `python translation-helpers/auto_translate.py es` — generate Spanish translation from Russian originals.
   • `python translation-helpers/auto_translate.py de --source en --dry-run` — preview a German translation using English as the source without writing files.
   • `./translation-helpers/new-language.sh it` — create Italian directory with template placeholders for manual work.

   The automatic translator needs an OpenAI API key. See "Generate a Translation with OpenAI" below for details.

2. **Translate the template files** in your new language directory

3. **Update the root README.md** to include your language

4. **Submit a Pull Request**

## Generate a Translation with OpenAI

If you prefer an initial machine translation that you can afterwards tweak manually, use the helper below. It will create a brand-new directory under `docs/<lang_code>` with fully translated Markdown files.

```bash
# 1. Install deps (only once)
pip install -r requirements.txt

# 2. Set your key
export OPENAI_API_KEY=sk-...

# 3. Generate translation (from Russian by default)
python translation-helpers/auto_translate.py es

#   Use --source en to translate from English originals instead
#   Use --dry-run to preview diffs without writing.
```

After the script finishes:

1. Review the generated Markdown to ensure cultural and contextual accuracy.
2. Commit the new `docs/<lang_code>` directory.
3. Continue with the normal contribution steps (update root README, open PR, etc.).

## Understanding the Template System

Template files contain placeholders in the format `{PLACEHOLDER_NAME}`. Here's how to use them:

### README.md Template

| Placeholder          | Description                   |
| -------------------- | ----------------------------- |
| `{PROJECT_NAME}`     | Project name in your language |
| `{TAGLINE}`          | Main tagline                  |
| `{WELCOME_TEXT}`     | Welcome paragraph             |
| `{MAIN_IDEA_TITLE}`  | Section title                 |
| `{SYMBOL_TEXT}`      | Symbol explanation            |
| `{SYMBOL_MEANING_1}` | First symbol meaning          |

### MANIFESTO.md Template

| Placeholder           | Description                                       |
| --------------------- | ------------------------------------------------- |
| `{MANIFESTO_TITLE}`   | "Manifesto of Curiosity" or equivalent            |
| `{OPENING_PARAGRAPH}` | The opening paragraph about dogmas and human fire |
| `{PRINCIPLE_X_TITLE}` | Titles like "Knowledge is a moral duty"           |

### COMMANDMENTS.md Template

| Placeholder                   | Description                           |
| ----------------------------- | ------------------------------------- |
| `{COMMANDMENTS_TITLE}`        | "Commandments"                        |
| `{COMMANDMENT_X_TITLE}`       | Command titles like "DO NOT DIE"      |
| `{COMMANDMENT_X_EXPLANATION}` | Explanation text for each commandment |

## Translation Best Practices

### 1. Maintain Philosophical Integrity

- Keep the core meaning intact
- Adapt cultural references while preserving the message
- Don't add religious concepts that aren't in the original

### 2. Preserve Structure

- Keep the same markdown formatting
- Maintain the same section order
- Keep the same number of bullet points, commandments, etc.

### 3. Cultural Adaptation

- Use appropriate formal/informal language for your culture
- Adapt examples that don't translate well culturally
- Consider how concepts like "anti-prayer" might be received

### 4. Language-Specific Considerations

#### Gendered Languages

- Use inclusive language where possible
- Be consistent with gender choices
- Consider cultural context for religious terminology

#### Right-to-Left Languages

- Maintain logical structure
- Consider if any visual elements need adjustment

#### Tonal Languages

- Choose appropriate tone levels for formal/religious content

## Step-by-Step Translation Process

1. **Read all files first** to understand the complete philosophy
2. **Start with README.md** as it provides the overview
3. **Translate MANIFESTO.md** next as it contains core principles
4. **Continue with COMMANDMENTS.md, PHILOSOPHY.md, RITUALS.md**
5. **Review for consistency** across all files
6. **Have a native speaker review** if possible

## Testing Your Translation

Before submitting:

1. Check that all placeholders are replaced
2. Verify links work correctly
3. Ensure consistent terminology across files
4. Read the complete set as a user would

## Submitting Your Translation

1. Update the root `README.md` to include your language:

   ```markdown
   <a href="docs/es/README.md">Español</a> ·
   ```

2. Create a Pull Request with:
   - Clear title: "Add [Language] translation"
   - Description of what you translated
   - Any cultural adaptations you made

## Need Help?

- Check existing translations (English) for examples
- Create an Issue if you need clarification
- Refer to the original Russian text for context
- Ask questions in your Pull Request

## Language Codes Reference

| Rank | ISO | Language (English)      | Native name      | Total speakers (M) |
| ---- | --- | ----------------------- | ---------------- | ------------------ |
| 1    | en  | English                 | English          | 1 548              |
| 2    | zh  | Mandarin Chinese        | 中文             | 1 184              |
| 3    | hi  | Hindi                   | हिन्दी           | 610                |
| 4    | es  | Spanish                 | Español          | 559                |
| 5    | fr  | French                  | Français         | 309                |
| 6    | ar  | Arabic (MSA)            | العربية          | 335                |
| 7    | bn  | Bengali                 | বাংলা            | 284                |
| 8    | pt  | Portuguese              | Português        | 267                |
| 9    | ru  | Russian                 | Русский          | 253                |
| 10   | id  | Indonesian              | Bahasa Indonesia | 252                |
| 11   | ur  | Urdu                    | اُردُو‎          | 246                |
| 12   | de  | German                  | Deutsch          | 134                |
| 13   | ja  | Japanese                | 日本語           | 126                |
| 14   | ng  | Nigerian Pidgin         | Nigerian Pidgin  | 121                |
| 15   | arz | Egyptian Arabic         | العربية المصرية  | 119                |
| 16   | mr  | Marathi                 | मराठी            | 99                 |
| 17   | vi  | Vietnamese              | Tiếng Việt       | 97                 |
| 18   | te  | Telugu                  | తెలుగు           | 96                 |
| 19   | ha  | Hausa                   | Hausa            | 94                 |
| 20   | tr  | Turkish                 | Türkçe           | 91                 |
| 21   | pnb | Western Punjabi         | پنجابی           | 90                 |
| 22   | sw  | Swahili                 | Kiswahili        | 87                 |
| 23   | tl  | Tagalog/Filipino        | Tagalog          | 87                 |
| 24   | ta  | Tamil                   | தமிழ்            | 86                 |
| 25   | yue | Yue Chinese (Cantonese) | 粤语             | 86                 |
| 26   | wuu | Wu Chinese              | 吴语             | 83                 |
| 27   | fa  | Persian (Iranian)       | فارسی            | 83                 |
| 28   | ko  | Korean                  | 한국어           | 82                 |
| 29   | th  | Thai                    | ไทย              | 71                 |
| 30   | jv  | Javanese                | ꦧꦱꦗꦮ             | 69                 |
| 31   | it  | Italian                 | Italiano         | 68                 |
| 32   | pl  | Polish                  | Polski           | 50                 |
| 33   | uk  | Ukrainian               | Українська       | 45                 |
| 34   | ro  | Romanian                | Română           | 34                 |
| 35   | nl  | Dutch                   | Nederlands       | 30                 |
| 36   | el  | Greek                   | Ελληνικά         | 25                 |
| 37   | sv  | Swedish                 | Svenska          | 20                 |
| 38   | cs  | Czech                   | Čeština          | 17                 |
| 39   | sr  | Serbian                 | Српски           | 12                 |
| 40   | he  | Hebrew                  | עברית            | 10                 |
| 41   | da  | Danish                  | Dansk            | 6                  |
| 42   | no  | Norwegian               | Norsk            | 5                  |
| 43   | lt  | Lithuanian              | Lietuvių         | 3                  |
| 44   | lv  | Latvian                 | Latviešu         | 2                  |
| 45   | mk  | Macedonian              | Македонски       | 2                  |
| 46   | et  | Estonian                | Eesti            | 1                  |
| 47   | be  | Belarusian              | Беларуская       | 1                  |
