from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Use override=True to replace existing env vars
print(os.getenv("DB_NAME"))
