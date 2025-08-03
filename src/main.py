import argparse
import subprocess
import json
import re

from pathlib import Path
from promts import ANALYZE_CODE_PROMPT, FINALIZE_PROMPT

# ==== LLM-call ====
def call_llm(prompt: str, model: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("=== STDERR ===")
    print(result.stderr.decode())
    print("=== STDOUT ===")
    print(result.stdout.decode())

    if result.returncode != 0:
        print("Error:", result.stderr.decode())
        return "LLM call failed."

    # Clean Ollama progress bars (lines made only of '@') if any slipped through
    output = result.stdout.decode()
    # remove lines that are ONLY made of '@' characters (progress bar)
    cleaned_lines = [ln for ln in output.splitlines() if set(ln.strip()) != {'@'}]
    output = "\n".join(cleaned_lines)
    return output

# ==== go through code files ====
def collect_code_files(path: Path, recursive: bool = False):
    extensions = [".cbl"]
    if path.is_file():
        return [path] if path.suffix.lower() in extensions else []
    
    pattern = "**/*" if recursive else "*"
    return [p for p in path.glob(pattern) if p.suffix.lower() in extensions]

# ==== Code-chunking ====
def chunk_code(source_code: str, max_chars=3000):
    # First, split by divisions
    division_pattern = re.compile(r'^\s*\w+\s+DIVISION\.', re.IGNORECASE | re.MULTILINE)
    split_points = [m.start() for m in division_pattern.finditer(source_code)]
    split_points.append(len(source_code))
    
    chunks = []
    for i in range(len(split_points) - 1):
        chunk = source_code[split_points[i]:split_points[i+1]]
        # If chunk is too big, you can further split here by SECTION or PARAGRAPH
        if len(chunk) > max_chars:
            # Fallback: split by SECTION
            section_pattern = re.compile(r'^\s*\w+\s+SECTION\.', re.IGNORECASE | re.MULTILINE)
            sect_splits = [m.start() for m in section_pattern.finditer(chunk)]
            sect_splits.append(len(chunk))
            for j in range(len(sect_splits) - 1):
                section_chunk = chunk[sect_splits[j]:sect_splits[j+1]]
                if len(section_chunk) > max_chars:
                    # Final fallback: split by size
                    lines = section_chunk.splitlines()
                    buf, size = [], 0
                    for line in lines:
                        buf.append(line)
                        size += len(line)
                        if size >= max_chars:
                            chunks.append('\n'.join(buf))
                            buf, size = [], 0
                    if buf:
                        chunks.append('\n'.join(buf))
                else:
                    chunks.append(section_chunk)
        else:
            chunks.append(chunk)
    return [c for c in chunks if c.strip()]


# ==== strip thinking part ====
def strip_pre_markdown(text: str) -> str:
    marker = "...done thinking."
    idx = text.find(marker)
    return text[idx:] if idx != -1 else text

# ==== finalizing docs ====
def finalizing_doc(doc_parts: list[str]) -> list[str]:

    final_doc = call_llm(FINALIZE_PROMPT.format(raw_markdown=doc_parts), model="deepseek-r1")
    return strip_pre_markdown(final_doc)

# ==== Documentation generation ====
def generate_docs(path: Path, output_path: Path, model: str, recursive: bool, max_chars: int):
    files = collect_code_files(path, recursive)

    if not files:
        print("No suitable code files found.")
        return

    for file in files:
        print(f"\nProcessing: {file}")
        with open(file, 'r', encoding='utf-8') as f:
            code = f.read()

        chunks = chunk_code(code, max_chars=max_chars)
        doc_parts = []

        for i, chunk in enumerate(chunks):

            print(f"Sending chunk {i+1} to LLM...")
            markdown = call_llm(ANALYZE_CODE_PROMPT.format(code_chunk=chunk), model)
            #markdown = strip_pre_markdown(markdown)
            doc_parts.append(f"## Block {i+1} in {file}\n{markdown.strip()}\n")

        #final_doc = finalizing_doc(doc_parts)

        out_file = output_path / f"{file.stem}.md"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(doc_parts))

        print(f"\nDocumentation saved to {out_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate markdown documentation from legacy COBOL code")
    parser.add_argument("input", type=Path, help="Path to COBOL code file.")
    parser.add_argument("-o", "--output", type=Path, default=".\docs", help="Path to output .md files.")
    parser.add_argument("-m", "--model", type=str, default="deepseek-r1", help="Ollama model name (legacy - promted deepseek-r1).")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process files recursively.")
    parser.add_argument("-c", "--max-chars", type=int, default=3000, help="Maximum number of characters per chunk.")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    generate_docs(args.input, args.output, args.model, args.recursive, args.max_chars)

if __name__ == "__main__":
    main()