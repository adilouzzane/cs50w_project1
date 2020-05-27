CREATE TABLE USERS (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    rating INTEGER NOT NULL,
    opinion TEXT,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id)
);