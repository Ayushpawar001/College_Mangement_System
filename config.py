import os


def load_local_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if not os.path.isfile(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.strip().strip("\"'")
            os.environ.setdefault(key.strip(), value)


load_local_env()

DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Ayushpawar01")
DB_NAME     = os.getenv("DB_NAME",     "college_db")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))

# Set DB_SSL=true in Render environment variables for cloud MySQL
DB_SSL      = os.getenv("DB_SSL", "false").lower() == "true"
