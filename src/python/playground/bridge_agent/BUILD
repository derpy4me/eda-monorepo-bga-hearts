python_sources(
    name="bridge_agent",
    sources=["*.py"],
    dependencies=[
        "3rd-party/python:reqs",
        "src/python/playground/bridge_agent/adapters:adapters",
        "src/python/playground/bridge_agent/domain:domain",
        "src/python/playground/bridge_agent/ports:ports",
        "src/python/playground/bridge_agent/services:services",
    ],
)

pex_binary(
    name="bridge_agent_pex",
    entry_point="main.py",
    dependencies=[":bridge_agent"],
    output_path="bridge_agent.pex",
)

docker_image(
    name="bridge_agent_docker_image",
    repository="bridge-agent",
    image_tags=["latest", "0.0.1"],
    dependencies=[":bridge_agent_pex"],
    instructions=[
        "FROM python:3.12-slim",
        "ARG PEX_BIN=bridge_agent.pex",
        "COPY $PEX_BIN /app/bridge_agent.pex",
        "RUN chmod +x /app/bridge_agent.pex",
        'ENTRYPOINT ["/app/bridge_agent.pex"]',
    ],
)

__dependents_rules__(
    (
        {"type": "*"},
        "3rd-party/**",
        "playground/bridge_agent/**",
        "!*",
    )
)
