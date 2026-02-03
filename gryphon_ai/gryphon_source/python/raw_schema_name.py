from PySide6.QtGui import QTextDocument
from mp_code_dynamic_tokens import dynamic_token_tuples


def raw_schema_name(mp_code_text):
    # get schema_name
    schema_name = "Schema name not defined"
    document = QTextDocument(mp_code_text)
    tokens = dynamic_token_tuples(document)
    schema_name = None
    for token_type, name in tokens:
        if token_type == "schema":
            schema_name = name
    return schema_name

