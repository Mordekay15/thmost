# THMOST

Tool that helps to maintain or raplace COBOL legacy systems. Fully automated approach with locally working LLM.

## How to Use
0. Make sure that you have [python3](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download).
1. Download and start a deepseek-r1 (can use any model)
```bash
ollama pull deepseek-r1:7b
```
3. Run the program
```bash
python main.py path/to/code -o <output_dir> -m <model> --recursive
```

| Argument            | Description                                              |
| ------------------- | -------------------------------------------------------- |
| `input`             | Path to a `.cbl` file or a folder containing COBOL files |
| `-o`, `--output`    | Output directory for Markdown documentation              |
| `-m`, `--model`     | Ollama model name (default: `deepseek-r1`)               |
| `-r`, `--recursive` | Recursively process all `.cbl` files in subdirectories   |
| `--max-chars`       | Maximum characters per chunk (default: 3000)             |


## License - MIT


