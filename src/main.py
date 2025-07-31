import argparse
import subprocess
import json
from pathlib import Path
from weakref import finalize

# ==== LLM-call ====
def call_llm(prompt: str, model: str = "legacy") -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print("Error:", result.stderr.decode())
        return "LLM call failed."

    return result.stdout.decode()

# ==== go through code files ====
def collect_code_files(path: Path, recursive: bool = False):
    extensions = [".cbl", ".cob", ".asm"]
    if path.is_file():
        return [path] if path.suffix.lower() in extensions else []
    
    pattern = "**/*" if recursive else "*"
    return [p for p in path.glob(pattern) if p.suffix.lower() in extensions]

# ==== Code-chunking ====
def chunk_code(source_code: str, max_chars=3000):
    lines = source_code.splitlines()
    chunks, current, total_len = [], [], 0
    for line in lines:
        total_len += len(line)
        current.append(line)
        if total_len >= max_chars:
            chunks.append('\n'.join(current))
            current, total_len = [], 0
    if current:
        chunks.append('\n'.join(current))
    return chunks

# ==== strip thinking part ====
def strip_pre_markdown(text: str) -> str:
    marker = "```markdown"
    idx = text.find(marker)
    return text[idx:] if idx != -1 else text

# ==== finalizing docs ====
def finalizing_doc(doc_parts: list[str]) -> list[str]:
    prompt = f""" You are a COBOL documentation expert.
    Below is raw generated documentation from multiple code chunks. Please rewrite it as a clean, structured, readable Markdown document.
    Remove any repetitive or low-value parts, and organize it clearly:
    - Add an introduction
    - Group related logic together
    - Use sections and bullet points
    - Keep it concise but informative
    - Make to be read by a senior COBOL developer and easy to understand by LLM

    Documentation: {raw_markdown} """

    final_doc = call_llm(prompt, model="deepseek-r1")
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
            prompt = f"""Explain the following COBOL or HLASM code in Markdown format.
                        Use headings, bullet points, and explain the logic clearly:

                        ```cobol    
                        {chunk}
                        ```"""

            print(f"Sending chunk {i+1} to LLM...")
            markdown = call_llm(prompt, model)
            markdown = strip_pre_markdown(markdown)
            doc_parts.append(f"## Block {i+1} in {file}\n{markdown.strip()}\n")

        final_doc = finalizing_doc(doc_parts)

        out_file = output_path / f"{file.stem}.md"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(final_doc)

        print(f"\nDocumentation saved to {out_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate markdown documentation from legacy COBOL code")
    parser.add_argument("input", type=Path, help="Path to COBOL code file.")
    parser.add_argument("-o", "--output", type=Path, default="output.md", help="Path to output .md file.")
    parser.add_argument("-m", "--model", type=str, default="legacy", help="Ollama model name (legacy - promted deepseek-r1).")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process files recursively.")
    parser.add_argument("-c", "--max-chars", type=int, default=3000, help="Maximum number of characters per chunk.")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    generate_docs(args.input, args.output, args.model, args.recursive, args.max_chars)

if __name__ == "__main__":
    main()