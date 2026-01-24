# strip underscore
def strip_underscore(text_item):
    return text_item.replace('_'," ")

# strip underscores in list
def strip_underscores(text_items):
    return [item.replace('_'," ") for item in text_items]

# strip underscores in list with allowance for numeric types
def maybe_strip_underscores(items):
    result = list()
    for item in items:
        if type(item) == str:
            result.append(item.replace("_", " "))
        else:
            result.append(item)
    return result

