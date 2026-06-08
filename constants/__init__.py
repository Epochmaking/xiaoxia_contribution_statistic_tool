import dotenv, os

dotenv.load_dotenv("config.ini")

LISTEN_PORT = int(os.getenv("listen_port", "8080"))
