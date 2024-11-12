#%%
import matplotlib.pyplot as plt
import math
from random import randrange
from utils import request, log_to_file, clear_log_file
import utils
from neo4j import GraphDatabase
import graph_structure



def analyze_common_group_for_disease(disease_counts, driver, node_type, relationship_type):
    total_associations = get_total_association_count_for_disease(driver, node_type, relationship_type)
    common_groups = get_type_occurrence_for_disease(disease_counts, driver, node_type, relationship_type)
    plot_common_group_for_disease(common_groups, total_associations, disease_counts, node_type)


def get_total_association_count_for_disease(driver, node_type, relationship_type):
    query = f"""
    MATCH (d:Disease)<-[:HAS_DISEASE]-(s:Biological_sample)-[:{relationship_type}]->(n:{node_type})
    RETURN d.name AS Disease, count(DISTINCT n) AS total_associations
    ORDER BY total_associations DESC
    """
    total_associations_result = request(driver, query)
    total_associations = {}
    for disease in total_associations_result:
        total_associations[disease['Disease']] = disease['total_associations']
    return total_associations


def get_type_occurrence_for_disease(disease_counts, driver, node_type, relationship_type):
    common_groups = {}
    for name, count in disease_counts.items():
        query = f"""
        MATCH (d:Disease {{name:\"{name}\"}})<-[:HAS_DISEASE]-(s:Biological_sample)-[r:{relationship_type}]->(n:{node_type})
        WITH count(DISTINCT r) AS samples_with_node, n AS n
        RETURN n.name AS node_name, samples_with_node
        """
        all_common_group_result = request(driver, query)
        if len(all_common_group_result) == 0:
            common_groups[name] = {}
            continue
        common_group = {}
        for sample in all_common_group_result:
            if sample['node_name'] is None:
                continue
            common_group[sample['node_name']] = sample["samples_with_node"] 
        common_groups[name] = common_group
    return common_groups


def plot_common_group_for_disease(common_groups, total_associations, disease_counts, node_type):
    for disease_name, common_group in common_groups.items():
        fig, ax = plt.subplots()
        
        total_associations_count = total_associations.get(disease_name, 1)
        sorted_common_group = dict(sorted(common_group.items(), key=lambda item: item[1], reverse=True))
        percentages = {node: (count / total_associations_count) for node, count in sorted_common_group.items()}
        
        ax.set_title(f"Common group for {disease_name}")
        ax.set_xlabel(node_type)
        ax.set_ylabel('Percentage of associations')
        ax.set_xticks([])
        ax.bar(percentages.keys(), percentages.values())
        
        info_text = f"Total Associations: {total_associations_count}\nSamples: {disease_counts[disease_name]}"
        plt.gcf().text(0.6, 0.8, info_text, fontsize=10, verticalalignment='top')
        
        plt.show()


def get_disease_analysis():
    driver = GraphDatabase.driver(utils.NEO4J_URL, auth=(utils.NEO4J_LOGIN, utils.NEO4J_PASSWORD))
    clear_log_file()
    log_to_file("Graph structure overview\n")
    disease_counts = graph_structure.get_disease_counts(driver, top_k=1)
    analyze_common_group_for_disease(disease_counts, driver, "Gene", "HAS_DAMAGE")
    analyze_common_group_for_disease(disease_counts, driver, "Phenotype", "HAS_PHENOTYPE")
    analyze_common_group_for_disease(disease_counts, driver, "Protein", "HAS_PROTEIN")


if __name__ == "__main__":
    get_disease_analysis()
# %%
