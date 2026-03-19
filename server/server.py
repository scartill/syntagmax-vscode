from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams,
    Diagnostic,
    Position,
    Range,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
)
from lark import Lark
from lark.indenter import Indenter

server = LanguageServer("syntagmax-server", "v0.1")

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

parser = Lark(
    GRAMMAR,
    parser="lalr",
    postlex=SyntagmaxIndenter(),
    propagate_positions=True
)


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls, params: DidOpenTextDocumentParams):
    validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    validate(ls, params.text_document.uri)


def validate(ls, uri):
    doc = ls.workspace.get_document(uri)
    diagnostics = []
    try:
        parser.parse(doc.source)
    except Exception as e:
        # Simple error reporting for now
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=1),
                ),
                message=str(e),
            )
        )
    ls.publish_diagnostics(uri, diagnostics)


@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls, params: CompletionParams):
    items = [
        CompletionItem(label="artifact"),
        CompletionItem(label="attribute"),
        CompletionItem(label="mandatory"),
        CompletionItem(label="optional"),
        CompletionItem(label="string"),
        CompletionItem(label="integer"),
        CompletionItem(label="boolean"),
        CompletionItem(label="enum"),
        CompletionItem(label="trace"),
        CompletionItem(label="from"),
        CompletionItem(label="to"),
        CompletionItem(label="or"),
    ]
    return CompletionList(is_incomplete=False, items=items)


if __name__ == "__main__":
    server.start_io()
