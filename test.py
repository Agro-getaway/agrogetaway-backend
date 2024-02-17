from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
storage_url = os.getenv('STORAGE_BUCKET')
api_key = os.getenv('NODE_ENV')
time  = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

# Use the variables, for example, to configure a database connection
print(int(time))
