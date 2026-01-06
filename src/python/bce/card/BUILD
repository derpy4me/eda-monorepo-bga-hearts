python_sources(name="logic", sources=["logic/**/*.py"], dependencies=["3rd-party/python:pydantic"])

python_sources(name="ports", sources=["ports/**/*.py"], dependencies=[":logic"])

python_sources(
    name="adapters",
    sources=["adapters/**/*.py"],
    dependencies=[
        ":logic",
        ":ports",
        "src/python/bce/common",
        "3rd-party/python:fastapi",
    ],
)

__dependents_rules__(
    (
        {"type": "*"},
        "src/python/bce/card/**",
        "!*",
    )
)
