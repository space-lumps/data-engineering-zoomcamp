FROM python:3.13.11-slim
# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin

# no longer needed to install these separately as they are included in the base image
# RUN pip install pandas pyarrow

# first set working directory and then copy files
WORKDIR /code
# since we removed uv run from the entrypoint, we need to add the venv to the PATH -- tells the container where to find the packages installed in the virtual environment
# Add virtual environment to PATH so we can use installed packages
ENV PATH="/code/.venv/bin:$PATH"

# Copy dependency files first (better layer caching)
COPY pyproject.toml .python-version uv.lock ./

# install dependencies from uv.lock file(ensures reproducible builds):
RUN uv sync --locked
# COPY pipeline.py . # we did this first
# now we want to Dockerize this pipeline, so we are changing this to copy ingest_data
COPY ingest_data.py .

# ENTRYPOINT ["uv", "run", "python", "pipeline.py"]
# ENTRYPOINT ["python", "pipeline.py"]
# also need to edit entrypoint from pipeline to ingest_data:
ENTRYPOINT ["python", "ingest_data.py"]