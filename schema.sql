CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    ingredients TEXT,
    recipe TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES items,
    user_id INTEGER REFERENCES users,
    comment TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE item_classes (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES items,
    title TEXT,
    value TEXT
);