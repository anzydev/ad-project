# 2. ER diagram

![AD Project PostgreSQL ER diagram](evidence/er-diagram.svg)


```mermaid
erDiagram
    USER ||--o{ SNAPSHOT : owns
    USER ||--o{ ALERT : owns

    USER {
        text id PK
        text email UK
        text password_hash
        UserRole role
        timestamp created_at
        timestamp updated_at
    }

    SNAPSHOT {
        text id PK
        text owner_id FK
        timestamp captured_at
        float cpu_percent
        float memory_percent
        text payload
    }

    ALERT {
        text id PK
        text owner_id FK
        text metric
        float threshold
        text message
        timestamp created_at
        boolean resolved
    }
```

Cardinality:

- One `USER` owns zero or many `SNAPSHOT` rows.
- One `USER` owns zero or many `ALERT` rows.
- Every `SNAPSHOT.owner_id` references exactly one `USER`.
- Every `ALERT.owner_id` references exactly one `USER`.
