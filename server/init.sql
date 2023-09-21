CREATE TABLE todos (
    id INTEGER,
    client_id VARCHAR NOT NULL,
    title VARCHAR,
    description VARCHAR,
    completed BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    PRIMARY KEY (id, client_id)
);


CREATE INDEX idx_todos_client_id ON todos(client_id);
CREATE INDEX idx_todos_title ON todos(title);
CREATE INDEX idx_todos_description ON todos(description);
CREATE INDEX idx_todos_completed ON todos(completed);

ALTER TABLE todos REPLICA IDENTITY FULL;
