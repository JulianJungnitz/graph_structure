import os

NEO4J_URL = "bolt://localhost:7687"
NEO4J_LOGIN = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "neo4j"

LOG_FILE = "./log.txt"

FEATURES_FOLDER = "./patient_features"
percentage_sections = [-1,-0.75, -0.5, -0.25, -0.1, 0, 0.1, 0.25, 0.5, 0.75, 1]



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
    
def get_disease_folder_name(disease_name):
    return f"{FEATURES_FOLDER}/{disease_name}"

def save_feature_analysis_to_file(
    disease_name,
    common_group,
    total_association,
    disease_count,
    node_type,
    relationship_type,
    ):
    folder_name = get_disease_folder_name(disease_name)
    features_file_name = f"{folder_name}/{relationship_type}_{node_type}.csv"
    general_file_name = f"{folder_name}/general.csv"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(features_file_name, "w") as f:
        f.write("Node, Occurrences\n")
        for node, count in common_group.items():
            f.write(f"{node}, {count}\n")
    with open(general_file_name, "w") as f:
        f.write("Total associations, Total samples\n")
        f.write(f"{total_association}, {disease_count}\n")
