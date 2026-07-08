from fastmcp import FastMCP

mcp = FastMCP("my-new-mcp-server2")


@mcp.tool()
def hello(name: str = "world") -> str:
    """Say hello."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()
