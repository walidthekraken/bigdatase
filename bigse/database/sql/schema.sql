--- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgres_fdw";

CREATE TABLE IF NOT EXISTS documents (
	docId SERIAL,
	docName TEXT NOT NULL,
	docPath TEXT,
    docLink TEXT,
	docEmbedding TEXT,
    added BOOLEAN DEFAULT FALSE,
	PRIMARY KEY (docId)
);