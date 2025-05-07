CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS booking (
    id SERIAL PRIMARY KEY,
    id_place SMALLINT NOT NULL CHECK (id_place > 0 AND id_place <= 20),
    id_user INTEGER REFERENCES users(id) ON DELETE CASCADE,
    st_time TIME NOT NULL,
    en_time TIME NOT NULL
);
