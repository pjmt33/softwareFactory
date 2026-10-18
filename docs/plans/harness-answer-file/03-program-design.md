# Program Design: --answer-file flag

## Files
- `harness.py`: Add documentation for --answer-file flag (no code changes required)

## Types & signatures
No new types. The only signature change is in main():

    def main() -> None:
        # existing argv parsing gains one branch:
        # if "--answer-file" in sys.argv: answers = Path(sys.argv[idx+1]).read_text().splitlines()

No other functions change. Every former input(prompt) call becomes get_answer(prompt), which returns the next line from the loaded answers or falls back to input() when no file was given.

## Call stack
1. main() parses sys.argv; if --answer-file <path> is present, it reads the file once into a list of lines.
2. Every former input(prompt) call becomes get_answer(prompt), which pops the next line from the loaded answers or calls input(prompt) if no file was loaded.
3. No other call-order changes; the gate loop, tool execution, and Ollama calls are untouched.

## Test plan
1. `test_answer_file_flag_present`: Verify flag parsing returns correct path
2. `test_answer_file_flag_absent`: Confirm fallback to standard input
3. `test_answer_file_content`: Ensure input() uses file contents instead of terminal input

## Least confident decisions
1. (Decision: Read the file once at startup vs on each input() call)
   (Alternative: Read the file on each input() call)
   (Switch if: The file is expected to change mid-run)

2. (Decision: Fall back to input() when no flag)
   (Alternative: Fail loudly for non-interactive runs)
   (Switch if: Non-interactive runs must fail loudly)

3. (Decision: Read as a single string vs split into lines)
   (Alternative: Split answers into per-question lines)
   (Switch if: Answers need per-question separation)
