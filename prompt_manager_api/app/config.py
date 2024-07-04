import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://prompts_user:passer@localhost/prompts_db'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KET') or 'super_jwt_secret_key'