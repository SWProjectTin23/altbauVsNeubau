# use timescaledb for db

Date: 2025-07-22

## Status

Accepted

## Context

Our project processes sensor data that is sent at regular short intervals (e.g., temperature, humidity, particulate matter). These are time-series data, which require efficient storage, querying, and support for operations like aggregations, range filtering, and long-term archiving.

## Decision

We decided to use **TimescaleDB** as our primary database system, as our application deals with high-frequency, time-stamped sensor data. This type of workload is best handled by a time-series database, which is specifically designed for efficient ingestion, storage, and querying of time-based data.


### Why a Time-Series Database

Compared to a traditional relational database, a time series database offers significant advantages: it supports fast inserts at scale, efficient storage through compression, and powerful time-based query capabilities such as range filtering and aggregations. 

### Why TimescaleDB

- Optimized for time-series data: TimescaleDB extends PostgreSQL with native support for time-series features like hypertables, automatic partitioning, compression, and continuous aggregates.

- PostgreSQL-compatible: Because TimescaleDB is a PostgreSQL extension, we can still use the broader PostgreSQL ecosystem (e.g., SQLAlchemy, pgAdmin, psycopg2).

- Efficient storage and performance: Compared to traditional relational databases, TimescaleDB handles large volumes of time-series data much more efficiently.

### Alternatives Considered

- PostgreSQL without Timescale extension:
    Functional but lacks efficiency for large-scale time-series data handling.

- InfluxDB:
    Designed for time-series, but less flexible for complex relational queries and lacks full SQL support.

## Consequences

- We will set up a PostgreSQL instance with TimescaleDB extension enabled via Docker.

- All sensor data will be stored in hypertables to enable time-based queries.

- Our query structure will follow TimescaleDB best practices for time-series analysis.
