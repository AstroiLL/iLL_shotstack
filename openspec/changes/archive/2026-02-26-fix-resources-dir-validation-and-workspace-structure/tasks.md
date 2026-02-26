## 1. Fix Resource Validation in check.py

- [x] 1.1 Update `ScriptChecker.__init__()` to store script directory path
- [x] 1.2 Update `check_resources()` to use script directory as base path for resources
- [x] 1.3 Update `check_resources()` to resolve resourcesDir relative to script directory
- [x] 1.4 Update `check_json.py` to pass correct base path to ScriptChecker
- [x] 1.5 Test validation from different working directories

## 2. Add Output Management to assemble.py

- [x] 2.1 Add `-o, --output` argument parsing in assemble.py main()
- [x] 2.2 Implement default output directory logic (`output/` in script directory)
- [x] 2.3 Implement output filename from JSON `name` field or script filename
- [x] 2.4 Implement automatic file indexing (script.mp4 → script_1.mp4 → script_2.mp4)
- [x] 2.5 Create output directory if it doesn't exist
- [x] 2.6 Update `fast_clip/assembler.py` to accept custom output path

## 3. Update Documentation

- [x] 3.1 Update AGENTS.md with new `-o, --output` flag for assemble.py
- [x] 3.2 Update AGENTS.md with corrected check.py behavior
- [x] 3.3 Update README.md with workspace structure documentation
- [x] 3.4 Update README.md with output management examples
- [x] 3.5 Add examples of running from different directories

## 4. Testing and Verification

- [x] 4.1 Test check.py validation from project directory
- [x] 4.2 Test check.py validation from parent directory
- [x] 4.3 Test assemble.py with default output
- [x] 4.4 Test assemble.py with custom output directory
- [x] 4.5 Test assemble.py with custom output filename
- [x] 4.6 Test automatic indexing (multiple builds)
- [x] 4.7 Test workspace structure with multiple projects
- [x] 4.8 Verify files are not overwritten
