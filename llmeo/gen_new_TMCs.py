import os
import random
import re
import string
import sys
import pandas as pd
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llmeo._utils.llm import Claude3, GPTo1, LLMConfig
from llmeo._utils.mol_calculation import calculate_fitness_ligand_space
from llmeo._utils.utils import extract_english_letters, extract_integers, dataframe_to_str, get_ligand_info
from prompts import PROMPT_Unbounded_Both, PROMPT_Unbounded_P

# Define common paths
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_PATH, "../data")
CONFIG_PATH = os.path.join(ROOT_PATH, "llm_config.yaml")

# Data file paths
LIGAND_FILE = os.path.join(DATA_PATH, "1M-space_50-ligands-full.csv")
SAMPLE_TMC_FILE = os.path.join(DATA_PATH, "lig50_top100_S.csv")
TMC_OUTPUT_FILE = os.path.join(ROOT_PATH, "Opt_TMC_maxBoth.csv")


def add_new_lig(new_sample, lig_df, new_lig_df):

    """This function updates the ligand pool with new ligands generated in the current iteration.
    It ensures that new ligands are added to the ligand pool and avoids duplicates.

    Input:
    - new_sample: DataFrame containing the new TMCs generated in the current iteration.
    - lig_df: DataFrame containing the existing ligand pool.
    - new_lig_df: DataFrame containing the new ligands extracted from the LLM response.

    Output:
    - Updated lig_df with new ligands added.

    How it works:
    1. If new_lig_df is not empty, it renames columns to match the format of lig_df and drops the 'index' column.
    2. Iterates over each row in new_sample:
    a. Skips the row if 'polarisability' is empty or NaN (meaning errors in this TMC, therefore no calculated value).
    b. For each ligand in the TMC (lig1 to lig4):
        i. Checks if the ligand is already in lig_df.
        ii. If not, adds the ligand from new_lig_df if available.
        iii. If not available in new_lig_df, generates a new id and adds the ligand to lig_df.
    4. Returns the updated lig_df.
    """
    if(not new_lig_df.empty):
        new_lig_df.rename(columns={'smiles':'SMILES'}, inplace=True)
        new_lig_df.rename(columns={'connecting_atom':'connecting atom element'}, inplace=True)
        new_lig_df.rename(columns={'connecting_index':'connecting atom index'}, inplace=True)
        new_lig_df.drop(columns=['index'], inplace=True)
 
    for idx, row in new_sample.iterrows():
        if(row['polarisability'] == "" or pd.isna(row['polarisability'])):
            continue
        for i in range(1, 5):
            lig_id = row["lig"+str(i)]
            if lig_id not in lig_df["SMILES"].values:
                if(not new_lig_df.empty):
                    lig_df = pd.concat([lig_df, new_lig_df[new_lig_df["SMILES"]==lig_id]])
                else:
                    id = (''.join(random.choices(string.ascii_letters, k=6))).upper()+"_subgraph_"+str(random.randint(1, 9))
                    lig_df.loc[len(lig_df)] = [lig_id, id, row["lig"+str(i)+"_charge"], row["lig"+str(i)+"_element"], row["lig"+str(i)+"_index"]]
    lig_df.drop_duplicates(subset=['SMILES'], keep='first', inplace=True)
    return lig_df

#based on the given format, it retrieves the TMCs information from the LLM response
def retrive_tmc_from_text(text):
    """
    This function extracts TMC information from the LLM response text.
    
    Input:
    - text: A string of LLM response with TMC and ligand details.

    Output:
    - df: DataFrame containing the extracted TMC information with columns for ligands and their properties.
    - lig_df: DataFrame containing the extracted ligand information with columns for SMILES, id, charge, connecting atom element, and connecting atom index.

    How it works:
    1 Iterates over each TMC entry and uses a regex pattern to extract ligand details.
    2. Iterates over each ligand in the TMC and extracts the SMILES, id, charge, connecting atom element, and connecting atom index.
    3. If 4 ligands are found, a TMC is created.
    4. Iterate this process for all TMCs in the text.
    8. Returns the DataFrames df and lig_df.

    """
    tmc_list = text.split("Ligand Details")[1:]
    df = None
    lig_df = None
    for i in range(len(tmc_list)):
        ligand_pattern = r'SMILES(?:[\W]+)\s`*([^\n`]+)`*\n(?:[\W]+)id(?:[\W]+)\s`*([^\n]+)`*\n(?:[\W]+)charge(?:[\W]+)\s([^\n]+)\n(?:[\W]+)connecting atom element(?:[\W]+)\s([^\n]+)\n(?:[\W]+)connecting atom index(?:[\W]+)\s*([^\n]+)\n'
        matches = re.findall(ligand_pattern, tmc_list[i])
        cur_df = pd.DataFrame(matches, columns=['smiles', 'id', 'charge', 'connecting_atom', 'connecting_index'])
        for idx, row in cur_df.iterrows():
            cur_df.loc[idx, 'charge'] = extract_integers(row['charge'])
            cur_df.loc[idx, 'connecting_atom'] = extract_english_letters(row['connecting_atom'])
            cur_df.loc[idx, 'connecting_index'] = extract_integers(row['connecting_index'])
            cur_df.loc[idx, 'smiles'] = extract_english_letters(row['smiles'])

        lig_df = pd.concat([lig_df, cur_df])
        data_list = []
        if(len(cur_df) == 4):
            for idx, row in cur_df.iterrows():

                data_list.append(extract_english_letters(row["smiles"]))
                data_list.append(extract_integers(row["charge"]))
                data_list.append(extract_english_letters(row["connecting_atom"]))
                data_list.append(extract_integers(row["connecting_index"]))
            cur_df = pd.DataFrame([data_list], columns=['lig1','lig1_charge', 'lig1_element', 'lig1_index', 'lig2','lig2_charge', 'lig2_element', 'lig2_index', 'lig3','lig3_charge', 'lig3_element', 'lig3_index', 'lig4','lig4_charge', 'lig4_element', 'lig4_index'])
        else:
            logging.info("Ligs Number not 4")
            logging.info(cur_df)
            continue
        df = pd.concat([df, cur_df])
    if df is not None:
        df = df.reset_index()
    if lig_df is not None:
        lig_df = lig_df.reset_index()

    return df, lig_df

def make_text_for_existing_tmcs(
    df: pd.DataFrame,
    LIG_CHARGE: dict,
    lig_df: pd.DataFrame,
    props
):
    """
    This function converts the TMC data from a DataFrame into a text format suitable for LLM prompts.
    
    Input:
    - df: Explored TMC data.
    - LIG_CHARGE: Dictionary containing ligand charges.
    - lig_df: DataFrame containing ligand information.
    - props: List of properties(Homo-Lumo gap, polarizability or both) to be included in the output text.

    Output:
    - text: A string representing the TMC data in text format.

    How it works:
        dataframe's TMC data will be translated to text format for LLM prompt
        It needs to distinguish between data successfully calculated and data with errors
        For successfully calculated data, besides ligands info, calculated value needs to be included
        For data with errors, ligands info and error message need to be included
        Output will be a string
    """
    text = ""
    props_e = props + ["_error"]
    lig_dict = {}
    for idx, row in lig_df.iterrows():
        lig_dict[row["SMILES"]] = row["id"]
    for _, row in df.iterrows():
        if(row["id"] != 0 and not pd.isna(row["id"])):
            tmc = "Pd_" + "_".join([row["lig1"], row["lig2"], row["lig3"], row["lig4"]])
            total_charge = 2 + sum(LIG_CHARGE[row[f"lig{i}"]] for i in range(1, 5))
            vals = [str(row[prop]) for prop in props]

        else:
            if(row["lig1"] not in lig_dict or row["lig2"] not in lig_dict or row["lig3"] not in lig_dict or row["lig4"] not in lig_dict):
                tmc = "Pd_" + "_".join([row["lig1"], row["lig2"], row["lig3"], row["lig4"]])
            else:
                lig1_id = lig_dict[row["lig1"]]
                lig2_id = lig_dict[row["lig2"]]
                lig3_id = lig_dict[row["lig3"]]
                lig4_id = lig_dict[row["lig4"]]
                tmc = "Pd_" + "_".join([lig1_id, lig2_id, lig3_id, lig4_id])
            
            if(row["lig1_charge"] == None or row["lig2_charge"]==None or row["lig3_charge"]==None or row["lig4_charge"]== None):
                total_charge = ""
            else:
                total_charge = 2 + int(row["lig1_charge"]) + int(row["lig2_charge"]) + int(row["lig3_charge"]) + int(row["lig4_charge"])
            vals = [str(row[prop]) for prop in props_e]
        text += "{" + ", ".join([tmc, str(total_charge)] + vals) + "}\n"
    return text 

#overall prompt generation logic
def generate_prompt(provided_samples, lig_df,prompt, LIG_CHARGE, props): 
    """
    This function converts the TMC data from a DataFrame into a text format suitable for LLM prompts.
    
    Input:
    - provided_samples: Explored TMC data.
    - lig_df: DataFrame containing ligand information.
    - props: List of properties(Homo-Lumo gap, polarizability or both) to be included in the output text.

    Output:
    - text: A string representing the TMC data in text format.

    How it works:
        dataframe's TMC data will be translated to text format for LLM prompt
        It needs to distinguish between data successfully calculated and data with errors
        For successfully calculated data, besides ligands info, calculated value needs to be included
        For data with errors, ligands info and error message need to be included
        Output will be a string
    """
    #read a dataframe, convert to string
    csv_file_str=dataframe_to_str(lig_df)
    
    current_samples_str = make_text_for_existing_tmcs(provided_samples, LIG_CHARGE ,lig_df, props)
    prompt = prompt.replace("CSV_FILE_CONTENT", csv_file_str)
    prompt = prompt.replace("NUM_PROVIDED_SAMPLES", str(len(provided_samples)))
    prompt = prompt.replace("CURRENT_SAMPLES", current_samples_str)
    return prompt


def one_LLM_iteration_unbonded(model, current_round_samples, lig_df, prompt, LIG_CHARGE, props):
    """
    #Create prompt => Send to LLM => Extract TMCs => Calculate fitness => Add new ligands to ligand pool

    Input:
    - model: LLM calling setup.
    - current_round_samples: Explored TMCs that will appeared in this iteration's prompt
    - lig_df: Ligands pool with new added ligands
    - prompt: LLM prompt template
    - LIG_CHARGE: Dictionary containing ligand charges
    - props: Arguments targeted properties
    """
    
    prompt = generate_prompt(current_round_samples, lig_df, prompt, LIG_CHARGE, props )
    logging.info("Prompt: %s", prompt)
    response = model.call(prompt)
    logging.info("Response: %s", response)
    anwser,  new_lig_df = retrive_tmc_from_text(response)
    logging.info(anwser)
    new_sample = calculate_fitness_ligand_space(anwser, ROOT_PATH, TMC_OUTPUT_FILE, unbounded=True)
    lig_df = add_new_lig(new_sample, lig_df, new_lig_df)
    logging.info("Length of lig_df: %d", len(lig_df))
    return anwser, lig_df

# one LLM run => prepare data for next iteration => one LLM run ... => export experiment data
def LLM_unbond_iterative(explored_df,lig_df, number_of_iterations, model, prompt, LIG_CHARGE, props):
    for i in range(number_of_iterations):
        logging.info("Iteration: %d", i)
        response_df, lig_df = one_LLM_iteration_unbonded(model, explored_df, lig_df, prompt, LIG_CHARGE, props)
        response_df["iteration"] = i
        response_df["id"] = 0
        explored_df = pd.concat([explored_df, response_df])
    return explored_df


#main function
def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Root path: %s", ROOT_PATH)
    
    # Load data
    df_ligands = pd.read_csv(LIGAND_FILE)
    LIG_CHARGE = {row["id"]: row["charge"] for _, row in df_ligands.iterrows()}
    config = LLMConfig.from_yaml(CONFIG_PATH)
    model = Claude3(config)
    model.create()
    
    current_round_sample_s = pd.read_csv(SAMPLE_TMC_FILE)
    lig_df = pd.read_csv(LIGAND_FILE)

    new_sample = LLM_unbond_iterative(current_round_sample_s, lig_df, 3, model, PROMPT_Unbounded_Both, LIG_CHARGE, ["polarisability", "homo_lumo_gap"])


if __name__ == "__main__":
    main()
