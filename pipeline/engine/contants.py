PICKLE_SAFE_ALLOWLIST = {
    "builtins": {
        "set",
        "frozenset",
        "list",
        "tuple",
        "dict",
        "str",
        "bytes",
        "bytearray",
        "int",
        "float",
        "complex",
        "bool",
        "type",
        "range",
        "slice",
    },
    "datetime": {
        "datetime",
        "date",
        "time",
        "timedelta",
        "timezone",
    },
    "decimal": {
        "Decimal",
    },
    "collections": {
        "OrderedDict",
        "defaultdict",
        "deque",
    },
    "uuid": {
        "UUID",
    },
    "pipeline.utils.collections": {
        "FancyDict",
    },
}
