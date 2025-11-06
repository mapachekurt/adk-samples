import os
from dotenv import load_dotenv

load_dotenv()

# Your script's logic here
print("GCP_ACCESS_TOKEN:", os.getenv("GCP_ACCESS_TOKEN"))
