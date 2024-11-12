# %%
import matplotlib.pyplot as plt
import math
from random import randrange
from utils import (
    request,
    log_to_file,
    clear_log_file,
    save_feature_analysis_to_file,
    percentage_sections,
)
import utils
from neo4j import GraphDatabase
import graph_structure
import os
from plot_util import plot_common_group_for_disease, plot_common_group_comparison, plot_occ_diff_count


def analyze_common_group_for_disease(
    disease_count,
    disease_name,
    driver,
    node_type,
    relationship_type,
    plot=False,
    save_analysis=False,
):
    total_association = get_total_association_count_for_disease(
        disease_name, driver, node_type, relationship_type
    )
    common_group = get_type_occurrence_for_disease(
        disease_count, disease_name, driver, node_type, relationship_type
    )
    if save_analysis:
        save_feature_analysis_to_file(
            disease_name,
            common_group,
            total_association,
            disease_count,
            node_type,
            relationship_type,
        )
    if plot:
        plot_common_group_for_disease(
            common_group, disease_name, total_association, disease_count, node_type
        )
    return common_group, total_association


def get_total_association_count_for_disease(
    disease_name, driver, node_type, relationship_type
):
    query = f"""
    MATCH (d:Disease {{name:\"{disease_name}\"}})<-[:HAS_DISEASE]-(s:Biological_sample)-[:{relationship_type}]->(n:{node_type})
    RETURN d.name AS Disease, count(DISTINCT n) AS total_associations
    ORDER BY total_associations DESC
    """
    total_associations_result = request(driver, query)
    if len(total_associations_result) == 0:
        print(
            f"No associations found for {disease_name} and {node_type} and {relationship_type}"
        )
        return 0
    total_association = total_associations_result[0]["total_associations"]
    return total_association


def get_type_occurrence_for_disease(
    disease_count, disease_name, driver, node_type, relationship_type
):

    query = f"""
    MATCH (d:Disease {{name:\"{disease_name}\"}})<-[:HAS_DISEASE]-(s:Biological_sample)-[r:{relationship_type}]->(n:{node_type})
    WITH count(DISTINCT r) AS samples_with_node, n AS n
    RETURN n.name AS node_name, samples_with_node
    """
    all_common_group_result = request(driver, query)
    if len(all_common_group_result) == 0:
        return {}
    common_group = {}
    for sample in all_common_group_result:
        if sample["node_name"] is None:
            continue
        common_group[sample["node_name"]] = sample["samples_with_node"]

    return common_group


def compare_common_group_for_disease(
    common_group_disease=None,
    common_group_control=None,
    total_disease_count=None,
    total_control_count=None,
    node_type=None,
    plot=False,
    save_plot=False,
    disease_name=None,
):
    print("Total disease count", total_disease_count)
    percentage_map_disease = {}
    percentage_map_control = {}
    for type, common_group in common_group_disease.items():
        percentage_map_disease[type] = common_group / total_disease_count

    for type, common_group in common_group_control.items():
        percentage_map_control[type] = common_group / total_control_count

    all_nodes = set()
    all_nodes.update(percentage_map_disease.keys())
    all_nodes.update(percentage_map_control.keys())

    percentage_diff = {}
    for node in all_nodes:
        percentage_diff[node] = percentage_map_disease.get(
            node, 0
        ) - percentage_map_control.get(node, 0)
    if plot:
        plot_common_group_comparison(
            percentage_diff,
            percentage_map_disease,
            percentage_map_control,
            node_type,
            save_plot,
            disease_name,
        )
    section_count_map = count_percentage_diff_in_sections(percentage_diff)

    return percentage_diff, section_count_map


def count_percentage_diff_in_sections(percentage_diff):
    section_map = {section: 0 for section in percentage_sections}

    for node, percentage in percentage_diff.items():
        last_section = -1
        for section in percentage_sections:
            if percentage > last_section and percentage <= section:
                section_map[section] += 1
                last_section = section
                break

    return section_map


def get_all_control_disease_comparisons(control_name, driver, min_occurrence=5):
    connections = [
        ("HAS_PHENOTYPE", "Phenotype"),
        ("HAS_DAMAGE", "Gene"),
        ("HAS_PROTEIN", "Protein"),
    ]
    
    control_occurences = get_number_of_occurences(control_name, driver)
    control_common_groups = get_common_groups(connections, control_name, driver)

    query = f"""Match (d:Disease)<-[:HAS_DISEASE]-(s:Biological_sample)
                with d, count(s) as count
                where count >= {min_occurrence}
                return d.name as name, count"""
    diseases = request(driver, query)
    for disease in diseases:
        get_control_disease_comparison(
            connections,
            disease["name"],
            driver,
            control_occurences=control_occurences,
            disease_occurences =disease["count"],
            control_common_groups=control_common_groups,
        )


def get_number_of_occurences( control_name, driver):
    query = f"""Match (d:Disease {{name:\"{control_name}\"}})<-[:HAS_DISEASE]-(s:Biological_sample)
                return count(s) as count"""
    res = request(driver, query)
    if len(res) == 0:
        print(f"No occurences found for {control_name}")
        return 0
    return res[0]["count"]

def get_control_disease_comparison(
    connections, disease_name, driver, control_occurences=None, disease_occurences=None, control_common_groups=None
):
    
    disease_common_groups = get_common_groups(connections, disease_name, driver)

    for control, disease in zip(control_common_groups, disease_common_groups):
        control_key = list(control.keys())[0]
        disease_key = list(disease.keys())[0]
        print(control_key, disease_key)
        control_common_group = control[control_key]
        disease_common_group = disease[disease_key]
        

        percentage_diff, section_count_map = compare_common_group_for_disease(
            common_group_disease=disease_common_group,
            common_group_control=control_common_group,
            total_control_count=control_occurences,
            total_disease_count=disease_occurences,
            node_type=control_key,
            plot=True,
            disease_name=disease_name,
            save_plot=True,
        )
        plot_occ_diff_count(
            section_count_map,
            disease_name,
            control_key,
            save_plot=True,
        )


def get_common_groups(connections, disease_name, driver):
    disease_count = graph_structure.get_disease_counts(driver, name=disease_name)[
        disease_name
    ]
    results = []
    for connection in connections:
        node_type = connection[1]
        relationship_type = connection[0]
        common_group, total_associations = analyze_common_group_for_disease(
            disease_count,
            disease_name,
            driver,
            node_type,
            relationship_type,
        )
        results.append(
            {
                node_type:  common_group,
                
            }
        )
    return results


def get_disease_analysis():
    driver = GraphDatabase.driver(
        utils.NEO4J_URL, auth=(utils.NEO4J_LOGIN, utils.NEO4J_PASSWORD)
    )
    clear_log_file()
    log_to_file("Disease analysis\n")
    # control_name = "esophagitis"
    control_name = "control"
    get_all_control_disease_comparisons(control_name, driver, min_occurrence=5)


if __name__ == "__main__":
    get_disease_analysis()
