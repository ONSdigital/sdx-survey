# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-alpine

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project config and lockfile first (for better caching)
COPY pyproject.toml uv.lock ./

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app

# Install dependencies
RUN uv sync --frozen --no-dev

# Expose the port the app runs on
EXPOSE 5000

# Reset the entrypoint to avoid potentially prefixing the command from other based images.
# i.e ENTRYPOINT ["python"] + CMD ["python", "run.py"] will result in ENTRYPOINT ["python", "python", "run.py"]
ENTRYPOINT []

CMD ["uv", "run", "--no-dev", "run.py"]
