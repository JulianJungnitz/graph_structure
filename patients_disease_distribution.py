# %%
import matplotlib.pyplot as plt
from random import randrange
import matplotlib.pyplot as plt
import re

LOG_FILE = "log_hauner.txt"

def get_disease_distribution(log_file_path):
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()
    except FileNotFoundError:
        print(f"File not found: {log_file_path}")
        return
    
    disease_section = re.search(
        r"------------------------- Disease analysis -------------------------.*?-------------------------",
        log_content, re.S
    )
    
    if not disease_section:
        print("Disease analysis section not found in the log file.")
        return
    
    total_number_of_diseases = int(re.search(r"Total number of diseases:\s*(\d+)", log_content).group(1))
    if not total_number_of_diseases:
        print("Total number of diseases not found.")
        return
    
    disease_section_text = disease_section.group(0)
    disease_data = re.findall(r"(.+?),\s*(\d+)", disease_section_text)
    counts = [int(d[1]) for d in disease_data]
    
    hidden_disease_counts = get_hidden_diseases(total_number_of_diseases, counts)
    plot_disease_distribution(counts, hidden_disease_counts)
    
   
def plot_disease_distribution(counts, hidden_disease_counts):
    existing_indices = range(len(counts))
    plt.figure(figsize=(10, 6))

    existing_indices = range(len(counts))
    
    plt.plot(existing_indices, counts, color='cornflowerblue', linestyle='-', alpha=1, linewidth=5)



    hidden_scatter_indices = range(len(counts), len(counts) + len(hidden_disease_counts))
    plt.plot(hidden_scatter_indices, hidden_disease_counts, color='orange', linestyle='-', alpha=1, linewidth=5) 

    plt.xlabel('Diseases')
    plt.ylabel('Count')
    plt.title('Diseases by Count')
    plt.tight_layout()
    plt.show()

def get_hidden_diseases(total_number_of_diseases, counts):
    top = min(5, max(counts)) 
    bottom = 1  
    disease_count = len(counts)

    hidden_disease_counts = [randrange(bottom, top + 1) for _ in range(total_number_of_diseases - disease_count)]
    hidden_disease_counts.sort(reverse=True)
    return hidden_disease_counts

get_disease_distribution(LOG_FILE)
