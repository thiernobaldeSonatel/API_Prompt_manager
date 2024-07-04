import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app


def get_db_connection():
    conn = psycopg2.connect(current_app.config['DATABASE_URL'], cursor_factory=RealDictCursor)
    return conn


def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(10) NOT NULL,
            group_id INTEGER REFERENCES groups(id)
        );

        CREATE TABLE IF NOT EXISTS prompts (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'En attente',
            price FLOAT DEFAULT 1000,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            prompt_id INTEGER REFERENCES prompts(id),
            vote_value INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ratings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            prompt_id INTEGER REFERENCES prompts(id),
            rating_value INTEGER NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()