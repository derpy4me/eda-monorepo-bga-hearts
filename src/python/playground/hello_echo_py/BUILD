python_sources(tags=["playground", "python"])

pex_binary(
    name="hello_echo_pex",
    entry_point="main.py:main"
)

__dependents_rules__(
    (
        {"type": "*"},
        "src/python/playground/hello_echo_py/**",
        "!*",
    )
)
