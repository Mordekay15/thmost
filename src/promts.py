ANALYZE_CODE_PROMPT = """
You are an expert in COBOL documentation.
Given a COBOL code chunk, generate concise, clear Markdown documentation for developers and system architects.

Instructions:
- Give a high-level overview of what this code does.
- List main entry points (PROGRAM-ID, sections, paragraphs).
- Summarize key data structures (no full variable lists).
- Outline main procedures/call chains (bullets or diagrams, not code).
- Note any external calls, file I/O, or dependencies.
- Flag dead code, unused variables, or risky constructs (e.g., GOTO).
- Summarize business logic and main data flows.
- If context is missing due to chunking, mention it.

Formatting:
- Use Markdown with clear section headers.
- Use bullet points and tables where relevant.

Do NOT include thoughts, process steps, or internal notes.

Below is the COBOL code chunk:
{code_chunk}
"""


FINALIZE_PROMPT = """
You are a COBOL documentation expert.
Combine the following Markdown docs (each from a COBOL chunk) into a single, clear, professional Markdown document.

Instructions:
- Remove repetition.
- Merge related info into clear sections (Overview, Logic, Data, File I/O, External Calls, Risks).
- Add a summary and table of contents if long.

Do NOT include raw chunk docs or internal notes.

Below are the chunk-level docs:
{raw_markdown}
"""
