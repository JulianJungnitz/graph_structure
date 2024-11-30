# %%
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import math
from random import randrange
from utils import request, log_to_file, clear_log_file
import utils


def get_node_count(label, driver):
    query = f"MATCH (n:{label}) RETURN count(n) as count"
    result = request(driver, query)
    log_to_file(f"{label}: {result[0]['count']} \n")


def get_rel_min_max_avg(
    start,
    rel,
    end,
    driver,
):

    query = f"""
    MATCH (a:{start})
    Optional MATCH (a:{start})-[r:{rel}]->(b:{end}) 
    With count(distinct r) as rel_count, a as a
    RETURN min(rel_count) as min, max(rel_count) as max, avg(rel_count) as avg, stDev(rel_count) as stDev
    """
    print(query)

    result = request(driver, query)
    log_to_file(
        f"{start} -> [{rel}] -> {end}, min: {result[0]['min']}, max: {result[0]['max']}, avg: {result[0]['avg']}, stDev: {result[0]['stDev']}\n"
    )


def attribute_min_max_avg(
    start,
    rel,
    end,
    attribute,
    driver,
):
    query = f"""
    MATCH (a:{start})-[r:{rel}]->(b:{end}) 
    With collect(r.{attribute}) as values
    UNWIND values as value
    RETURN min(value) as min, max(value) as max, avg(value) as avg
    """
    result = request(driver, query)
    log_to_file(f"{start} -> [{rel}] -> {end}  | Attribute: {attribute}\n")
    log_to_file(
        f"Min: {result[0]['min']}, Max: {result[0]['max']}, Avg: {result[0]['avg']}\n"
    )


def get_all_node_counts(labels, driver):
    log_to_file("\n")
    log_to_file("------------------------- Node counts ------------------------- \n")
    for label in labels:
        get_node_count(label, driver)


def get_all_rel_min_max_avg(relationships, driver):
    log_to_file("\n")
    log_to_file(
        "------------------------- Number of Relationships-------------------------\n"
    )
    for rel in relationships:
        get_rel_min_max_avg(rel[0], rel[1], rel[2], driver)


def get_disease_counts(
    driver,
    top_k=None,
    name=None,
    min_occurrence=1,
):
    log_to_file("\n")
    log_to_file(
        "------------------------- Disease analysis -------------------------\n"
    )
    includeControl = False
    if name == "control":
        includeControl = True

    query = (
        """Match (s:Biological_sample) -[r:HAS_DISEASE]-> (b:Disease """
        + ('{name: "' + name + '"}' if name else "")
        + """)
            with count(r) as disease_count, b.name as name
            where disease_count>= """
        + str(min_occurrence)
        + """
            """
        + ("" if includeControl else "and b.name <> 'control'")
        + """
            return name, disease_count order by disease_count desc """
        + (f" limit {top_k}" if top_k else "")
        + ""
    )
    print(query)
    result = request(driver, query)

    total_disease_count = len(result)
    log_to_file(f"Total number of diseases: {total_disease_count} \n")

    log_to_file("Diseases by count\n")
    index = 0
    disease_counts = {}
    for disease in result:
        if disease["disease_count"] < min_occurrence:
            break
        log_to_file(f"{index}, {disease['disease_count']} \n")
        index += 1
        disease_counts[disease["name"]] = disease["disease_count"]
    return disease_counts


def get_people_analysis(driver):
    log_to_file("\n")
    log_to_file("------------------------- People analysis -------------------------\n")
    # sick people
    query = """Match(b:Disease) <-[r:HAS_DISEASE]-(a:Biological_sample)
            where b.name <> 'control'
            return count(distinct a) as sick_people"""
    result = request(driver, query)
    log_to_file(f"Number of sick people: {result[0]['sick_people']} \n")

    # healthy people
    query = """Match(b:Disease) <-[r:HAS_DISEASE]-(a:Biological_sample)
            where b.name = 'control'
            return count(distinct a) as healthy_people"""
    result = request(driver, query)
    log_to_file(f"Number of healthy people: {result[0]['healthy_people']} \n")

    # without diagnosis
    query = """Match(a:Biological_sample)
            where not (a)-[:HAS_DISEASE]->()
            return count(a) as undiagnosed"""
    result = request(driver, query)
    log_to_file(f"Number of people without diagnosis: {result[0]['undiagnosed']} \n")


def get_all_relationships(driver):
    query = "MATCH (a)-[r]->(b) RETURN distinct type(r) as relationship, labels(a)[0] as a,  labels(b)[0] as b"
    result = request(driver, query)
    print(result)
    relationships = []
    for rel in result:
        relationships.append((rel["a"], rel["relationship"], rel["b"]))
    return relationships


def get_all_node_types(driver):
    query = "MATCH (a) RETURN distinct labels(a) as labels"
    result = request(driver, query)
    nodeTypes = set()
    for node in result:
        if node["labels"]:
            for label in node["labels"]:
                nodeTypes.add(label)
    return nodeTypes


def get_missing_ensamble_id_analysis(driver):
    query = """MATCH (b:Biological_sample)-[r:HAS_DAMAGE]->(g:Gene)
                WHERE g.synonyms[1]=""
                RETURN 
                    count(DISTINCT b) AS number_of_biological_samples, 
                    count(DISTINCT g) AS number_of_genes, 
                    count(r) AS number_of_relationships"""
    result = request(driver, query)
    log_to_file(
        f"------------------------- Missing Ensamble ID analysis -------------------------\n"
    )
    log_to_file(
        f"Number of genes without ensamble id: {result[0]['number_of_genes']}\n"
    )
    log_to_file(
        f"Number of biological samples connected to genes without ensamble id: {result[0]['number_of_biological_samples']}\n"
    )
    log_to_file(
        f"Number of relationships between a sample and a gene withou ensamble id: {result[0]['number_of_relationships']}\n"
    )


def get_graph_structure_overview():
    driver = GraphDatabase.driver(
        utils.NEO4J_URL, auth=(utils.NEO4J_LOGIN, utils.NEO4J_PASSWORD)
    )
    clear_log_file()
    log_to_file("Graph structure overview\n")

    # get_disease_counts(driver, min_occurrence=1)

    # node_count_labels = get_all_node_types(driver)

    # get_all_node_counts(node_count_labels, driver)

    relationships = [
        ("Known_variant", "VARIANT_FOUND_IN_CHROMOSOME", "Chromosome"),
        ("Known_variant", "VARIANT_FOUND_IN_GENE", "Gene"),
        ("Known_variant", "VARIANT_FOUND_IN_PROTEIN", "Protein"),
        ("Biological_sample", "BELONGS_TO_SUBJECT", "Subject"),
        ("Biological_sample", "HAS_DISEASE", "Disease"),
        ("Biological_sample", "HAS_PHENOTYPE", "Phenotype"),
        ("Biological_sample", "HAS_PROTEIN", "Protein"),
        ("Biological_sample", "HAS_DAMAGE", "Gene"),
    ]

     # relationships = get_all_relationships(driver)
    
    get_all_rel_min_max_avg(relationships, driver)

    # get_people_analysis(driver)
    # get_missing_ensamble_id_analysis(driver)


if __name__ == "__main__":
    get_graph_structure_overview()

# %%
