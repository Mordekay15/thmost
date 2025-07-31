
# cli_codegen.py

import argparse
import subprocess
import json
from pathlib import Path

# ==== LLM-вызов через Ollama ====
def call_llm(prompt: str, model: str = "legacy") -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print("⚠️ Error:", result.stderr.decode())
        return "⚠️ LLM call failed."

    return result.stdout.decode()

# ==== Разделение кода на чанки ====
def chunk_code(source_code: str, lines_per_chunk=20):
    lines = source_code.splitlines()
    return ['\n'.join(lines[i:i+lines_per_chunk]) for i in range(0, len(lines), lines_per_chunk)]

# ==== Генерация документации ====
def generate_doc(input_path: Path, output_path: Path, model: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        code = f.read()

    chunks = chunk_code(code)

    doc_parts = []
    for i, chunk in enumerate(chunks):
        prompt = f"""Explain the following legacy code (COBOL or HLASM) in **Markdown** format. 
                Use headings, bullet points, and summarize its logic and purpose clearly: {chunk}"""

        print(f"🧠 Sending chunk {i+1} to LLM...")
        markdown = call_llm(prompt, model)
        doc_parts.append(f"## Block {i+1}\n{markdown.strip()}\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(doc_parts))

    print(f"\n✅ Documentation saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate markdown documentation from legacy COBOL/HLASM code using Ollama.")
    parser.add_argument("input", type=Path, help="Path to COBOL/HLASM code file.")
    parser.add_argument("-o", "--output", type=Path, default="output.md", help="Path to output .md file.")
    parser.add_argument("-m", "--model", type=str, default="legacy", help="Ollama model name (legacy - promted deepseek-r1).")
    args = parser.parse_args()

    generate_doc(args.input, args.output, args.model)

if __name__ == "__main__":
    main()