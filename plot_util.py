import matplotlib.pyplot as plt
from utils import percentage_sections, get_disease_folder_name
import os
from matplotlib.patches import Patch

def plot_common_group_for_disease(
    common_group, disease_name, total_association, disease_count, node_type
):

    fig, ax = plt.subplots()

    total_associations_count = total_association
    sorted_common_group = dict(
        sorted(common_group.items(), key=lambda item: item[1], reverse=True)
    )
    percentages = {
        node: (count / total_associations_count)
        for node, count in sorted_common_group.items()
    }

    ax.set_title(f"Occurences of {node_type} for {disease_name}")
    ax.set_xlabel(node_type)
    ax.set_ylabel("Percentage of occurrences")
    ax.set_xticks([])
    ax.bar(percentages.keys(), percentages.values())

    info_text = (
        f"Total Associations: {total_associations_count}\nSamples: {disease_count}"
    )
    plt.gcf().text(0.6, 0.8, info_text, fontsize=10, verticalalignment="top")

    plt.show()


def plot_common_group_comparison(
    percentage_diff,
    percentage_map_disease,
    percentage_map_control,
    node_type,
    save_plot,
    disease_name,
):
    print("Percentage diff", percentage_diff)
    percentage_diff = dict(
        sorted(percentage_diff.items(), key=lambda item: item[1], reverse=True)
    )
    fig, ax = plt.subplots()
    ax.set_title(f"Occurrences of {node_type}")
    ax.set_xlabel(node_type)
    ax.set_ylabel("Percentage of occurrences")
    ax.set_xticks([])

    ax.bar(
        percentage_diff.keys(),
       [0] * len(percentage_diff),
    )
    ax.bar(
        percentage_map_disease.keys(),
        percentage_map_disease.values(),
        label=disease_name,
        color="blue",
        alpha=0.5,
    )
    ax.bar(
        percentage_map_control.keys(),
        percentage_map_control.values(),
        label="Control",
        color="orange",
        alpha=0.5,
    )
    colors = ['green' if value > 0 else 'red' for value in percentage_diff.values()]
    ax.bar(
        percentage_diff.keys(),
        percentage_diff.values(),
        color=colors,
        alpha=1,
    )

    number_of_key_disease = len(percentage_map_disease)


    for section in percentage_sections:
        ax.axhline(section, color="red", linestyle="--", alpha=0.5)

    all_percentages = (
        list(percentage_diff.values())
        + list(percentage_map_disease.values())
        + list(percentage_map_control.values())
    )
    max_percentage = max(all_percentages)
    min_percentage = min(all_percentages)

    if min_percentage >= -0.1 and max_percentage <= 0.1:
        ax.set_ylim(-0.1, 0.1)
    else:
        y_range = max_percentage - min_percentage
        padding = 0.05 * y_range 
        ax.set_ylim(min_percentage - padding, max_percentage + padding)

    legend_elements = [
        Patch(facecolor='blue', label=disease_name, alpha=0.5),
        Patch(facecolor='orange', label='Control', alpha=0.5),
        Patch(facecolor='green', label='Positive Difference'),
        Patch(facecolor='red', label='Negative Difference'),
        Patch(facecolor='white', label=f'Unique {node_type}s for patients with disease: ' + str(number_of_key_disease)),
    ]

    ax.legend(handles=legend_elements)
    plt.show()

    if save_plot:
        folder_name = get_disease_folder_name(disease_name)
        plot_file_name = f"{folder_name}/occ_diff_{node_type}_plot.png"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        fig.savefig(plot_file_name)
        plt.close(fig)


def plot_occ_diff_count(
    section_count_map,
    disease_name,
    node_type,
    save_plot=False,
):
    fig, ax = plt.subplots()
    ax.set_title(f"Percentage Difference in Occurrences of {node_type}s for {disease_name}")
    ax.set_xlabel("Percentage Difference Range")
    ax.set_ylabel("Count")

    sorted_sections = sorted(percentage_sections)
    x_labels = []
    counts = []

    last_section = -1
    for section in sorted_sections:
        label = f"{last_section} - {section}"
        x_labels.append(label)
        counts.append(section_count_map.get(section, 0))
        last_section = section

    label = f"{last_section} - 1"
    x_labels.append(label)
    counts.append(section_count_map.get(1, 0))

    ax.bar(x_labels, counts)
    ax.set_xticklabels(x_labels, rotation=90)

    plt.show()
    if save_plot:
        folder_name = get_disease_folder_name(disease_name)
        plot_file_name = f"{folder_name}/occ_count_percentage_{node_type}_plot.png"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        fig.savefig(plot_file_name)    