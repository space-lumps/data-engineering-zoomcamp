# Data Engineering Projects
This repository serves as a parent workspace for a collection of data engineering projects focused on building practical, end-to-end pipelines. Each project is implemented as a self-contained, reproducible system and emphasizes production-oriented concerns such as schema management, parameterization, containerization, and operational tooling.

The first project establishes the foundation: a Dockerized ingestion pipeline that loads large, public datasets into PostgreSQL using Python and SQLAlchemy. Future projects will build on this base to cover additional ingestion patterns, transformations, orchestration, analytics-ready modeling, and observability, progressively expanding the repository into a cohesive portfolio of real-world data engineering workflows.

---
### Project 1: Pipeline
End-to-end, Dockerized data ingestion pipeline that loads NYC Yellow Taxi trip data into PostgreSQL using Python, Pandas, and SQLAlchemy. The project demonstrates schema-aware CSV ingestion, chunked loading for large datasets, CLI-driven configuration with Click, and full containerization with Docker and Docker Compose, including Postgres and pgAdmin. Designed to mirror a production-style analytics engineering workflow from raw data download through reproducible database loading and inspection.
