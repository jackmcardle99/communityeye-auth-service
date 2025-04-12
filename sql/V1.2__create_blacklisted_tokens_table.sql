-- 
-- File: V1.2__create_blacklisted_tokens_table.sql
-- Author: Jack McArdle

-- This file is part of CommunityEye.

-- Email: mcardle-j9@ulster.ac.uk
-- B-No: B00733578
-- 

CREATE TABLE blacklisted_tokens (
    token VARCHAR(500) PRIMARY KEY,
    blacklisted_at TIMESTAMP NOT NULL
);