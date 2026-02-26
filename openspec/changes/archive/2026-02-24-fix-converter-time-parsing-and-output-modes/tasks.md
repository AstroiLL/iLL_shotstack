## 1. Fix Time Parsing in convert_script.py

- [x] 1.1 Update `parse_time()` function to support MM:SS:mmm format (3 parts: minutes, seconds, milliseconds)
- [x] 1.2 Update `parse_timing_start()` to correctly extract trim from timing range with milliseconds
- [x] 1.3 Test time parsing with example: "00:01:800" should return 1.8

## 2. Add Output Modes to convert_script.py

- [x] 2.1 Add global VERBOSITY variable at module level
- [x] 2.2 Implement `log_verbose()`, `log_normal()`, `log_quiet()` helper functions
- [x] 2.3 Update `main()` to parse -v/--verbose and -q/--quiet flags
- [x] 2.4 Replace existing print statements in `md_to_shotstack()` with appropriate log functions
- [x] 2.5 Replace existing print statements in `convert_file()` with appropriate log functions
- [x] 2.6 Add verbose logging in `parse_new_table()` to show each row being processed
- [x] 2.7 Add verbose logging in `build_clip_with_text()` to show clip details
- [x] 2.8 Add verbose logging in `build_text_clip()` to show text overlay details
- [x] 2.9 Add verbose logging for merge fields generation

## 3. Add Quiet Mode to check.py

- [x] 3.1 Update `main()` to parse -q/--quiet flag in addition to existing -v flag
- [x] 3.2 Update `ScriptChecker` class to store quiet mode state
- [x] 3.3 Modify `print_report()` to suppress all output when quiet mode is enabled
- [x] 3.4 Ensure exit codes work correctly: 0 for success, 1 for errors (even in quiet mode)

## 4. Update Documentation

- [x] 4.1 Update AGENTS.md section for convert_script.py to document -v and -q flags
- [x] 4.2 Update AGENTS.md section for check.py to document -q flag

## 5. Testing and Verification

- [x] 5.1 Test convert_script.py with script_single.md - verify correct trim values (1.8, not 860)
- [x] 5.2 Test convert_script.py -v (verbose mode) shows detailed output
- [x] 5.3 Test convert_script.py -q (quiet mode) shows no output
- [x] 5.4 Test convert_script.py normal mode shows only essential info
- [x] 5.5 Test check.py -q (quiet mode) shows no output but returns correct exit code
- [x] 5.6 Verify script_single.md table remains unchanged after all operations
