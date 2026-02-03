from PySide6.QtCore import QRegularExpression
# root names
ROOT_NAME_EXPRESSION = QRegularExpression(r"^\s*ROOT\s*(\w*)\s*:")

# composite names
COMPOSITE_NAME_EXPRESSION = QRegularExpression(r"^\s*(\w*)\s*:")

# schema names
SCHEMA_NAME_EXPRESSION = QRegularExpression(r"^\s*SCHEMA\s*(\w*)")


# atomic names are all words
ATOMIC_NAME_EXPRESSION = QRegularExpression(r"\b\w*\b")

# multiline comment expressions
COMMENT_START_EXPRESSION = QRegularExpression("/\\*")
COMMENT_END_EXPRESSION = QRegularExpression("\\*/")

# single line comments
SINGLE_LINE_COMMENT_EXPRESSION = QRegularExpression(r"--.*$")

# keywords, ref. MP documentation
_KEYWORDS = "ACTIVITY|ADD|AFTER|ALL|AND|APPLY|ARROW|AS|AT|ATTRIBUTES|AVG|BAR|BEFORE|BUILD|CHAIN|CHART|CHECK|CLEAR|CONTAINS|COORDINATE|CUT_END|CUT_FRONT|DIAGRAM|DISJ|DO|ELSE|ENCLOSING|ENSURE|EXISTS|FI|FIRST|FOLLOWS|FOR|FOREACH|FROM|GLOBAL|GRAPH|HAS|IF|IN|IS|LAST|LEAST|LINE|MAP|MARK|MAX|MAY_OVERLAP|MIN|NEW|NOT|OD|ON|ONFAIL|OR|PRECEDES|REJECT|REPORT|REVERSE|ROOT|ROTATE|SAY|SCHEMA|SET|SHARE|SHIFT_LEFT|SHIFT_RIGHT|SHOW|SORT|STEP|SUCH|SUM|TABLE|TABS|THAT|THEN|THIS|TIMES|TITLE|WHEN|WITHIN|X_AXIS|"
KEYWORD_SET = set(_KEYWORDS.split('|'))
KEYWORD_EXPRESSION = QRegularExpression(r'\b(%s)\b'%_KEYWORDS)

# words
WORD_EXPRESSION = QRegularExpression("\\b\\w*")

# meta-symbols
META_SYMBOL_EXPRESSION = QRegularExpression(r'\$\$(EVENT|ROOT|COMPOSITE|ATOM|scope)')

# operators, any of: -+*=<>!(){}|
OPERATOR_EXPRESSION = QRegularExpression("[-+\/*=<>!\(\)\{\}\|]+")

# numbers
NUMBER_EXPRESSION = QRegularExpression(r'[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')

# variables
VARIABLE_EXPRESSION = QRegularExpression("(<.*>)?\$[a-z][a-z0-9_]*")

# Double-quoted string, possibly containing escape sequences
QUOTED_TEXT_EXPRESSION = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')

# brace, bracket IF, DO
PAREN_EXPRESSION = QRegularExpression("[\(\)]")   # "(" or ")"
BRACE_EXPRESSION = QRegularExpression("[\{\}]")   # "{" or "}"
BRACKET_EXPRESSION = QRegularExpression("[\[\]]")   # "[" or "]"
IF_EXPRESSION = QRegularExpression("\\b(IF|FI)\\b") # IF or FI
DO_EXPRESSION = QRegularExpression("\\b(DO|OD)\\b") # DO or OD

# leading whitespace used for auto-indent
LEADING_WHITESPACE_EXPRESSION = QRegularExpression("^\s*")

