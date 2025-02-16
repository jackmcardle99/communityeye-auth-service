CREATE TABLE blacklisted_tokens (
    token VARCHAR(500) PRIMARY KEY,
    blacklisted_at TIMESTAMP NOT NULL
);