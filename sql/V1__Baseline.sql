CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email_address VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    city VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    admin BOOLEAN NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    is_deleted BOOLEAN NOT NULL
);
