from PySide6.QtCore import QRegularExpression
# root names
ROOT_NAME_EXPRESSION = QRegularExpression(r"^\s*ROOT\s*(\w+)\s*:")

# composite names
COMPOSITE_NAME_EXPRESSION = QRegularExpression(r"^\s*(\w+)\s*:")

# schema names
SCHEMA_NAME_EXPRESSION = QRegularExpression(r"^\s*SCHEMA\s*(\w+)")

# atomic names are all words
ATOMIC_NAME_EXPRESSION = QRegularExpression(r"\b\w+\b")

# multiline comment expressions
COMMENT_START_EXPRESSION = QRegularExpression("/\\*")
COMMENT_END_EXPRESSION = QRegularExpression("\\*/")

# multiline custom view expressions all end in "}" see custom view syntax (83)
_CUSTOM_VIEW_KEYWORDS = r"REPORT|GRAPH|TABLE|BAR\s+CHART"
CUSTOM_VIEW_START_EXPRESSION = QRegularExpression(r"^\s*(%s)\s+(\w+)"
                                                  %_CUSTOM_VIEW_KEYWORDS)
CUSTOM_VIEW_END_EXPRESSION = QRegularExpression(r"}")

# single line comments
SINGLE_LINE_COMMENT_EXPRESSION = QRegularExpression(r"--.*$")

# MP keywords, ref. MP documentation
# note: string and number are table typecast declarations for table column
#       names
# note: largest, smallest, len are interval attribute types
# note: start, end, duration are timing attributes
MP_KEYWORDS = "ACTIVITY|ADD|AFTER|ALL|AND|APPLY|ARROW|AS|AT|ATTRIBUTES|AVG|BAR|BEFORE|BUILD|CHAIN|CHART|CHECK|CLEAR|CONTAINS|COORDINATE|CUT_END|CUT_FRONT|DIAGRAM|DISJ|DO|ELSE|ENCLOSING|ENSURE|EXISTS|FI|FIRST|FOLLOWS|FOR|FOREACH|FROM|GLOBAL|GRAPH|HAS|IF|IN|IS|LAST|LEAST|LINE|MAP|MARK|MAX|MAY_OVERLAP|MIN|NEW|NOT|OD|ON|ONFAIL|OR|PRECEDES|REJECT|REPORT|REVERSE|ROOT|ROTATE|SAY|SCHEMA|SET|SHARE|SHIFT_LEFT|SHIFT_RIGHT|SHOW|SORT|STEP|SUCH|SUM|TABLE|TABS|THAT|THEN|THIS|TIMES|TITLE|WHEN|WITHIN|X_AXIS|string|number|smallest|largest|len|start|end|duration"
MP_KEYWORD_SET = set(MP_KEYWORDS.split('|'))
MP_KEYWORD_EXPRESSION = QRegularExpression(r'\b(%s)\b'%MP_KEYWORDS)

# words
WORD_EXPRESSION = QRegularExpression(r"[a-zA-Z0-9_]+")

# MP meta-symbols
MP_META_SYMBOLS = "TRACE|EVENT|ROOT|COMPOSITE|ATOM|scope"
MP_META_SYMBOL_SET = set(MP_META_SYMBOLS.split('|')) # match excludes $$ prefix
MP_META_SYMBOL_EXPRESSION = QRegularExpression(r'\$\$(%s)'%MP_META_SYMBOLS)

# operators, any of: -+*=<>!(){}|
OPERATOR_EXPRESSION = QRegularExpression(r"[-+*=<>!(){}|]")

# numbers
NUMBER_EXPRESSION = QRegularExpression(r'[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')

# variables
VARIABLE_EXPRESSION = QRegularExpression(r"(<.*>)?\$([a-z][a-z0-9_]*)")

# Double-quoted string, possibly containing escape sequences
QUOTED_TEXT_EXPRESSION = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')

# brace, bracket IF, DO
PAREN_EXPRESSION = QRegularExpression(r"[()]")   # "(" or ")"
BRACE_EXPRESSION = QRegularExpression(r"[{}]")   # "{" or "}"
BRACKET_EXPRESSION = QRegularExpression(r"[][]")   # "[" or "]"
IF_EXPRESSION = QRegularExpression(r"\b(IF|FI)\b") # IF or FI
DO_EXPRESSION = QRegularExpression(r"\b(DO|OD)\b") # DO or OD

# leading whitespace used for auto-indent
LEADING_WHITESPACE_EXPRESSION = QRegularExpression(r"^\s*")

