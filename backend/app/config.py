import os


APP_NAME = os.getenv("APP_NAME", "Harbor AI API")
APP_ENV = os.getenv("APP_ENV", "development")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")