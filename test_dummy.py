class Config:
    OLD_API_KEY = "123"

def get_key():
    return Config.OLD_API_KEY

def log_key():
    print(f"Using key: {Config.OLD_API_KEY}")
