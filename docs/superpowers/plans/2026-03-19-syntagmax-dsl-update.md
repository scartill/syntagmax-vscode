# Syntagmax DSL Extension Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the Syntagmax VS Code extension (grammar, LSP server, and completions) to support the new `trace` syntax and blank lines.

**Architecture:** The update involves modifying the TextMate grammar for syntax highlighting and the Lark-based Python LSP server for parsing, diagnostics, and completions. A Lark Indenter is required to handle the `_INDENT` and `_DEDENT` tokens.

**Tech Stack:** TypeScript (VS Code Extension), Python (pygls, Lark), TextMate Grammar (JSON).

---

### Task 1: Create Verification Sample

**Files:**
- Create: `test.stmx`

- [ ] **Step 1: Create the sample file**
Create `test.stmx` with the following content:
```syntagmax
artifact REQ:
    attribute id is mandatory string
    attribute contents is mandatory string
    attribute desc is optional string
    attribute pid is optional string
    attribute input is optional string
    attribute output is optional string

trace from SRC to REQ is mandatory
trace from TEST to REQ or SRC is mandatory
```

- [ ] **Step 2: Commit**
```bash
git add test.stmx
git commit -m "test: add verification sample for new Syntagmax syntax"
```

### Task 2: Update LSP Server Grammar and Indenter

**Files:**
- Modify: `server/server.py`

- [ ] **Step 1: Add Indenter class and update GRAMMAR**
Update `server/server.py` to include the `Indenter` class and the new `GRAMMAR`:

```python
from lark.indenter import Indenter

class SyntagmaxIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

GRAMMAR = r"""
start: (artifact | trace | _NL)+

artifact: ARTIFACT name ":" _NL _INDENT (rule | _NL)* _DEDENT
rule: "attribute" name "is" PRESENCE type _NL

trace: "trace" "from" name "to" target_list "is" PRESENCE _NL
target_list: name ("or" name)*

?type: "string" -> type_string
     | "integer" -> type_integer
     | "boolean" -> type_boolean
     | "enum" "[" value ("," value)* "]" -> type_enum

ARTIFACT: "artifact"
?name: WORD
PRESENCE: "mandatory" | "optional"
?value: ESCAPED_STRING | WORD

%import common.WORD
%import common.ESCAPED_STRING
%import common.WS_INLINE
%import common.SH_COMMENT
%ignore WS_INLINE
%ignore SH_COMMENT

%declare _INDENT _DEDENT
_NL: /(\r?\n[\t ]*)+/
"""
```

- [ ] **Step 2: Update parser initialization**
Update the `parser` initialization in `server/server.py`:
```python
parser = Lark(
    GRAMMAR,
    parser="lalr",
    postlex=SyntagmaxIndenter(),
    propagate_positions=True
)
```

- [ ] **Step 3: Verify grammar and indenter with a test script**
Create `verify_grammar.py`:
```python
from lark import Lark
from lark.indenter import Indenter
import sys

class SyntagmaxIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

GRAMMAR = r'''
start: (artifact | trace | _NL)+

artifact: ARTIFACT name ":" _NL _INDENT (rule | _NL)* _DEDENT
rule: "attribute" name "is" PRESENCE type _NL

trace: "trace" "from" name "to" target_list "is" PRESENCE _NL
target_list: name ("or" name)*

?type: "string" -> type_string
     | "integer" -> type_integer
     | "boolean" -> type_boolean
     | "enum" "[" value ("," value)* "]" -> type_enum

ARTIFACT: "artifact"
?name: WORD
PRESENCE: "mandatory" | "optional"
?value: ESCAPED_STRING | WORD

%import common.WORD
%import common.ESCAPED_STRING
%import common.WS_INLINE
%import common.SH_COMMENT
%ignore WS_INLINE
%ignore SH_COMMENT

%declare _INDENT _DEDENT
_NL: /(\r?\n[\t ]*)+/
'''

parser = Lark(
    GRAMMAR,
    parser="lalr",
    postlex=SyntagmaxIndenter(),
    propagate_positions=True
)

sample = """artifact REQ:
    attribute id is mandatory string
    attribute contents is mandatory string
    attribute desc is optional string
    attribute pid is optional string
    attribute input is optional string
    attribute output is optional string

trace from SRC to REQ is mandatory
trace from TEST to REQ or SRC is mandatory
"""

try:
    parser.parse(sample)
    print("SUCCESS: Grammar and Indenter are valid and parsed the sample.")
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
```
Run: `python verify_grammar.py`
Expected: SUCCESS

- [ ] **Step 4: Commit**
```bash
git add server/server.py
git commit -m "feat: update LSP server grammar and add Indenter for trace syntax"
```

### Task 3: Update LSP Server Completions

**Files:**
- Modify: `server/server.py`

- [ ] **Step 1: Update `completions` function**
Add `trace`, `from`, `to`, `or` to the `items` list in `completions` function in `server/server.py`.

- [ ] **Step 2: Commit**
```bash
git add server/server.py
git commit -m "feat: add trace-related keywords to LSP completions"
```

### Task 4: Update TextMate Grammar

**Files:**
- Modify: `syntagmax.tmLanguage.json`

- [ ] **Step 1: Add new keywords**
Add `trace`, `from`, `to`, `or` to the `keywords` pattern in `syntagmax.tmLanguage.json`.
```json
{
    "name": "keyword.control.syntagmax",
    "match": "\\b(artifact|attribute|is|trace|from|to|or)\\b"
}
```

- [ ] **Step 2: Commit**
```bash
git add syntagmax.tmLanguage.json
git commit -m "feat: update syntax highlighting for new trace keywords"
```

### Task 5: Final Verification and Cleanup

- [ ] **Step 1: Build the extension**
Run: `npm run compile`

- [ ] **Step 2: Functional Verification (Manual)**
Launch the extension in the Extension Development Host and open `test.stmx`.
- **Syntax Highlighting:** Verify `trace`, `from`, `to`, `or` are highlighted as keywords.
- **Diagnostics:** Verify no errors are reported for `test.stmx`.
- **Error Reporting:** Change `trace` to `tracex` and verify a diagnostic error is reported.
- **Completions:** Trigger Ctrl+Space and verify new keywords are listed.

- [ ] **Step 3: Cleanup verification script**
Run: `rm verify_grammar.py`

- [ ] **Step 4: Commit final state**
```bash
git add .
git commit -m "chore: final verification and cleanup"
```
