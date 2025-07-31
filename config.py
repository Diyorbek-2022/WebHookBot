from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

BOT_TOKEN = env.str("LINK")  # Bot Token
NGROK_TUNNEL_URL = env.str("NGROK_TUNNEL_URL")  # Bot Token

# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
