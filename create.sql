CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    password VARCHAR(200) NOT NULL
);