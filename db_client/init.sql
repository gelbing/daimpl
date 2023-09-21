CREATE TABLE todos (
    id SERIAL,
    client_id VARCHAR NOT NULL,
    title VARCHAR,
    description VARCHAR,
    completed BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, client_id)
);

CREATE INDEX idx_todos_client_id ON todos(client_id);
CREATE INDEX idx_todos_title ON todos(title);
CREATE INDEX idx_todos_description ON todos(description);
CREATE INDEX idx_todos_completed ON todos(completed);

ALTER TABLE todos REPLICA IDENTITY FULL;
