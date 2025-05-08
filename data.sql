CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS booking (
    id SERIAL PRIMARY KEY,
    id_place SMALLINT NOT NULL CHECK (id_place > 0 AND id_place <= 20),
    id_user INTEGER REFERENCES users(id) ON DELETE CASCADE,
    st_datetime TIMESTAMP NOT NULL,
    en_datetime TIMESTAMP NOT NULL,
    duration SMALLINT CHECK (duration >= 0 AND duration <= 1440),
);
