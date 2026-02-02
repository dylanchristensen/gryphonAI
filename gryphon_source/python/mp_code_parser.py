import re
from copy import deepcopy
from collections import defaultdict
from PySide6.QtCore import QRegularExpression
from mp_code_expressions import MP_KEYWORDS, MP_META_SYMBOL_EXPRESSION, \
                  COMMENT_START_EXPRESSION, \
                  COMMENT_END_EXPRESSION, SINGLE_LINE_COMMENT_EXPRESSION, \
                  QUOTED_TEXT_EXPRESSION

# event names are [a-zA-Z_]\w*
# root and composite event definitions are follwed by colon ":" as opposed
# to variable assignment which is followed by colon equals ":=".
_STARTING_SCHEMA_EXPRESSION \
                  = QRegularExpression(r"^\s*SCHEMA\s*([a-zA-Z_]\w*)")
_STARTING_ROOT_EXPRESSION \
                  = QRegularExpression(r"^\s*ROOT\s*([a-zA-Z_]\w*)\s*:(?!=)")
_STARTING_EVENT_COLON_EXPRESSION \
                  = QRegularExpression(r"^\s*([a-zA-Z_]\w*)\s*:(?!=)")
_EVENT_WORD_EXPRESSION \
                  = QRegularExpression(r"(\$\$[a-zA-Z_]\w*|[a-zA-Z_]\w*)")

# SAY keyword
_SAY_KEYWORD_EXPRESSION = QRegularExpression(r"\bSAY\s*\(")

# SAY content
_SAY_CONTENT = QRegularExpression(r"\bSAY\s*\((.*)\)\s*$")

# increment_report_command "=>" (97) or add_tuple_command "<|" (106)
_SAY_EXEMPTION_EXPRESSION = QRegularExpression(r"=\s*>|<\s*\|")

# MP keywords
_STARTING_KEYWORD_EXPRESSION = QRegularExpression(r"^\s*(%s)"%MP_KEYWORDS)

# Define events where key=event type, value=event(s).
# We call schema an event.
_EMPTY_EVENT_DICT = {"schema": "Schema not defined",
                     "root":set(), "atomic":set(), "composite":set()}
# optimization
_mp_code_text_cache = ""
_mp_lines_cache = ""
_event_dict = deepcopy(_EMPTY_EVENT_DICT)

# return non-commented lines
def _non_comment_lines(mp_code_text):
    in_comment = False
    stripped_lines = list()
    lines = mp_code_text.split("\n")
    for line in lines:

        # remove multi-line comments
        text_start_index = 0
        parts = list()
        while text_start_index != -1:
            if in_comment == False:
                # in non-comment
                match = COMMENT_START_EXPRESSION.match(line, text_start_index)
                comment_start_index = match.capturedStart()
                if comment_start_index == -1:
                    # no comment so accept text from text_start_index to end
                    parts.append(line[text_start_index:])
                    text_start_index = -1
                else:
                    # comment so accept text from text_start_index
                    # to comment_start_index
                    parts.append(line[text_start_index:comment_start_index])
                    text_start_index = comment_start_index + 2
                    in_comment = True # begin comment

            elif in_comment == True:
                # in comment
                match = COMMENT_END_EXPRESSION.match(line, text_start_index)
                comment_end_index = match.capturedStart()
                if comment_end_index == -1:
                    # line ends in comment
                    text_start_index = -1
                else:
                    # there is text after the comment
                    text_start_index = comment_end_index + 2
                    in_comment = False

        # compose new line from uncommented parts
        stripped_line = "".join(parts)

        # remove single-line comments
        match = SINGLE_LINE_COMMENT_EXPRESSION.match(stripped_line)
        single_line_comment_index = match.capturedStart()
        if single_line_comment_index != -1:
            stripped_line = stripped_line[0:single_line_comment_index]

        stripped_lines.append(stripped_line)

    # convert list of stripped lines into a list made from semicolon boundaries
    parsable_mp_lines = (" ".join(stripped_lines)).split(";")

    return parsable_mp_lines

def _non_quote_line(non_comment_line):
    # remove quoted text
    while True:
        match = QUOTED_TEXT_EXPRESSION.match(non_comment_line)
        quoted_text_index = match.capturedStart()
        if quoted_text_index == -1:
            # no quoted text
            break
        # remove quoted text including quotation marks
        non_comment_line = non_comment_line[:quoted_text_index] \
                           + non_comment_line[match.capturedEnd():]
    return non_comment_line

def _non_quote_lines(non_comment_lines):
    non_quote_lines = [_non_quote_line(line) for line in non_comment_lines]
    return non_quote_lines

# return tuple schema, remainder
def _parse_schema(mp_line):
    match = _STARTING_SCHEMA_EXPRESSION.match(mp_line)
    return match.captured(1), mp_line[match.capturedEnd():]

# add any events as atomic events, stopping at any BUILD block
def _parse_righthand_events(mp_line, events):
    match_iterator = _EVENT_WORD_EXPRESSION.globalMatch(mp_line)
    while match_iterator.hasNext():
        word = match_iterator.next().captured(1)
        if word == "BUILD":
            # the beginning of a build block means no more event definitions
            break
        if MP_META_SYMBOL_EXPRESSION.match(word).captured(1):
            # do not include words that are MP meta-symbols
            continue
        events["atomic"].add(word)

def _parse_line(mp_line, events):
    # use if line starts with ROOT <word> :
    match = _STARTING_ROOT_EXPRESSION.match(mp_line)
    word = match.captured(1)
    if word:
        events["root"].add(word)
        _parse_righthand_events(mp_line[match.capturedEnd():], events)

    # discard if line starts with a keyword
    match = _STARTING_KEYWORD_EXPRESSION.match(mp_line)
    if match.captured(1):
        return

    # discard if line does not start with word and colon and is
    # not an := variable assignment
    match = _STARTING_EVENT_COLON_EXPRESSION.match(mp_line)
    word = match.captured(1)
    if word:
        events["composite"].add(word)
        _parse_righthand_events(mp_line[match.capturedEnd():], events)

# Return events classified as dict event_type of sets of event names.
# Optimization: cache result.
def mp_code_event_dict(mp_code_text):
    global _mp_code_text_cache
    global _mp_lines_cache
    global _event_dict

    # optimization
    if mp_code_text == _mp_code_text_cache:
        return deepcopy(_event_dict)
    _mp_code_text_cache = mp_code_text

    # convert text into lines without comments or quoted text
    non_comment_lines = _non_comment_lines(mp_code_text)
    mp_lines = _non_quote_lines(non_comment_lines)

    # optimization
    if mp_lines == _mp_lines_cache:
        return deepcopy(_event_dict)
    _mp_lines_cache = mp_lines

    # recalculate the evnt dict
    _event_dict = deepcopy(_EMPTY_EVENT_DICT)

    if not mp_lines:
        # no text
        return deepcopy(_event_dict)

    # parse the schema
    schema, remainder = _parse_schema(mp_lines[0])
    if schema:
        _event_dict["schema"] = schema
    else:
        # no schema so abort
        return deepcopy(_event_dict)

    # parse the first line's remaining text
    _parse_line(remainder, _event_dict)

    # parse the remaining lines
    for mp_line in mp_lines[1:]:
        _parse_line(mp_line, _event_dict)

    # remove composite events from the atomic event list
    _event_dict["atomic"] -= _event_dict["composite"]

    # convert sets into sorted lists
    _event_dict["root"] = sorted(_event_dict["root"], key=str.casefold)
    _event_dict["atomic"] = sorted(_event_dict["atomic"], key=str.casefold)
    _event_dict["composite"] = sorted(
                                _event_dict["composite"], key=str.casefold)

    return deepcopy(_event_dict)

# get the list of connectable events without schema and say events
def mp_code_event_list(event_dict):
    event_types = ["root", "atomic", "composite"]
    events = list()
    for event_type in event_types:
        events.extend(event_dict[event_type])
    events = sorted(events, key=str.casefold)
    return events

def mp_code_schema(mp_code_text):
    return mp_code_event_dict(mp_code_text)["schema"]

def _say_text_and_number_count(say_line):
    say_content = _SAY_CONTENT.match(say_line).captured(1)

    quoted_text = ""
    between_text = list()
    number_count = 0

    global_match = QUOTED_TEXT_EXPRESSION.globalMatch(say_content)

    # text and count
    start = 0
    while global_match.hasNext():
        match = global_match.next()
        quoted_text += match.captured()[1:-1] # text with quotes stripped
        captured_start = match.capturedStart()
        between_text = say_content[start:match.capturedStart()]
        if between_text.strip():
            number_count += 1
        start = match.capturedEnd()

    # any final count
    final_text = say_content[start:]
    if final_text.strip():
        number_count += 1

    return quoted_text, number_count

# Return header list and warning list
# derive sorted say headers from mp_code_text
# We do not cache these results.  This mp_code_text is from trace generation
# and is called by graph_list_table_model when the graph is loaded.
_number_pattern = re.compile(r"[0-9.]+")
def mp_code_say_headers(mp_code_text):

    # convert text into lines without comments
    non_comment_lines = _non_comment_lines(mp_code_text)

    header_list = list()
    warnings = list()
    for line in non_comment_lines:
        non_quote_line = _non_quote_line(line)

        # SAY keyword is required
        if not _SAY_KEYWORD_EXPRESSION.globalMatch(non_quote_line).hasNext():
            continue

        # SAY directives increment_report_command "=>" (97) and
        # add_tuple_command "<|" (106) do not generate SAY event blocks
        if _SAY_EXEMPTION_EXPRESSION.globalMatch(non_quote_line).hasNext():
            continue

        # parse out say_text and number count
        say_text, number_count = _say_text_and_number_count(line)

        # say_text must not contain numbers else warn and drop
        if number_count >= 1 and _number_pattern.findall(say_text):
            say_content = _SAY_CONTENT.match(line).captured(1)
            warnings.append(say_content)
            continue

        # add to texts and columns
        if number_count == 0:
            header_list.append(say_text)
        else:
            for i in range(number_count):
                header_list.append("%s (%d)"%(say_text, i+1))

    header_list = sorted(header_list, key=str.casefold)
    return header_list, warnings

# Return text for the matching column else X or checkmark
# Say nodes are type="T"."""
def say_info(gry_graph, column_title):
    if not "trace" in gry_graph:
        raise RuntimeError("bad")

    for gry_node in gry_graph["trace"]["nodes"]:
        if gry_node["type"] == "T":

            # try exact column match
            label = gry_node["label"]
            if label == column_title:
                return "\u2713" # checkmark

            # match the label with numbers extracted with the column title
            prefix = _number_pattern.sub("", label)
            numbers = _number_pattern.findall(label)
            for i, number in enumerate(numbers):
                # key is column without numbers and with index appended
                key = "%s (%i)"%(prefix, i+1)
                if key == column_title:
                    # column matches for this index so return its number
                    return float(numbers[i])

    # no column match found
    return "X"

