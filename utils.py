NEO4J_URL = "bolt://83.229.84.12"
NEO4J_LOGIN = "tumaiReadonly"
NEO4J_PASSWORD = "MAKEATHON2024"
NEO4J_DATABASE = "graph2.db"

LOG_FILE = "./log.txt"

def log_to_file(message):
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message)

def clear_log_file():
    with open(LOG_FILE, "w") as f:
        f.write("")


def request(driver, query):
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query).data()
        return result