# Design Spec: Syntagmax DSL Extension Update

## 1. Overview
The Syntagmax Domain Specific Language (DSL) has been enhanced with new syntax for traceability and improved flexibility (allowing blank lines). This update ensures the VS Code extension correctly highlights the new keywords, provides accurate diagnostics via the LSP server, and offers relevant completions.

## 2. Goals
- Update the TextMate grammar for syntax highlighting.
- Update the Lark-based LSP server to support the new grammar rules.
- Add new keywords to the LSP completion list.
- Verify the extension using the provided sample DSL.

## 3. Architecture
The extension follows the standard VS Code architecture:
- **Client:** TypeScript-based VS Code extension that launches the server and provides syntax highlighting.
- **Server:** Python-based Language Server (LSP) using `pygls` for the protocol and `Lark` for parsing.

## 4. Proposed Changes

### 4.1. Language Server (`server/server.py`)
The `GRAMMAR` string in `server/server.py` will be updated to:

```lark
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
```

The `completions` function will be updated to include:
- `trace`, `from`, `to`, `or`.

### 4.2. Syntax Highlighting (`syntagmax.tmLanguage.json`)
The `keywords` repository will be updated to include the new keywords:
- `trace`, `from`, `to`, `or` as `keyword.control.syntagmax`.

### 4.3. Language Configuration (`language-configuration.json`)
No changes are required for indentation as the new `trace` rule is a single-line statement.

## 5. Verification Plan

### 5.1. Sample File
Create `test.stmx` with:
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

### 5.2. Test Cases
1.  **Syntax Highlighting:** Open `test.stmx` and verify all keywords are colored correctly.
2.  **Diagnostics:** Ensure no errors are reported for the sample file.
3.  **Error Reporting:** Intentionally introduce an error (e.g., misspelling `trace`) and verify the LSP server reports a diagnostic.
4.  **Completions:** Trigger completion (Ctrl+Space) and verify `trace`, `from`, `to`, and `or` are listed.

## 6. Deployment
The changes will be committed to the repository and can be tested locally by launching the extension in the Extension Development Host.
