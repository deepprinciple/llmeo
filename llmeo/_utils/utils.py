import hashlib
import re
from typing import Dict, List, Optional

import pandas as pd


def find_tmc_in_space(df: pd.DataFrame, tmcs: List[str]) -> Optional[pd.DataFrame]:
    """
    Find TMCs in the search space by checking all possible rotations of ligands.
    
    Args:
        df: DataFrame containing the TMC search space
        tmcs: List of TMC strings to search for
        
    Returns:
        DataFrame containing matched TMCs, or None if no matches found
    """
    matched_tmcs = []
    
    for tmc in tmcs:
        if tmc is None:
            continue
            
        # Get ligands from TMC string
        ligs = tmc.split("_")[1:]
        
        # Check all possible rotational combinations of ligands
        rotations = [
            ligs[i:] + ligs[:i] for i in range(4)
        ]
        
        # Search for each rotation in the DataFrame
        for rot_ligs in rotations:
            match_df = df[
                (df["lig1"] == rot_ligs[0]) &
                (df["lig2"] == rot_ligs[1]) &
                (df["lig3"] == rot_ligs[2]) &
                (df["lig4"] == rot_ligs[3])
            ]
            
            if len(match_df):
                matched_tmcs.append(match_df)
                break  # Found a match, move to next TMC
                
    return pd.concat(matched_tmcs) if matched_tmcs else None

def make_text_for_existing_tmcs(
    df: pd.DataFrame, 
    lig_charge: Dict[str, int], 
    props: List[str]
) -> str:
    """
    Create formatted text representation of TMCs with their properties.
    
    Args:
        df: DataFrame containing TMC data
        lig_charge: Dictionary mapping ligands to their charges
        props: List of property names to include
        
    Returns:
        Formatted string containing TMC information
    """
    lines = []
    for _, row in df.iterrows():
        # Construct TMC string
        tmc = "Pd_" + "_".join([row["lig1"], row["lig2"], row["lig3"], row["lig4"]])
        
        # Calculate total charge
        total_charge = 2 + sum(lig_charge[row[f"lig{i}"]] for i in range(1, 5))
        
        # Get property values
        prop_values = [str(round(row[prop], 3)) for prop in props]
        
        # Format line
        line = "{" + ", ".join([tmc, str(total_charge)] + prop_values) + "}"
        lines.append(line)
        
    return "\n".join(lines)

def make_prompt(
    template: str,
    ligands: str,
    df_samples: pd.DataFrame,
    lig_charge: Dict[str, int],
    num_samples: str = "ONE",
    props: List[str] = ["gap"]
) -> str:
    """
    Create prompt for LLM by filling template with TMC information.
    
    Args:
        template: Prompt template
        ligands: String containing ligand information
        df_samples: DataFrame with sample TMCs
        lig_charge: Dictionary of ligand charges
        num_samples: Number of samples to request
        props: List of properties to include
        
    Returns:
        Formatted prompt string
    """
    replacements = {
        "CSV_FILE_CONTENT": ligands,
        "CURRENT_SAMPLES": make_text_for_existing_tmcs(df_samples, lig_charge, props),
        "NUM_SAMPLES": num_samples,
        "NUM_PROVIDED_SAMPLES": str(len(df_samples))
    }
    
    for key, value in replacements.items():
        template = template.replace(key, value)
        
    return template

def retrive_tmc_from_message(message: str, expected_returns: int = 1) -> List[str]:
    """
    Extract TMC strings from LLM response message.
    
    Args:
        message: Response message from LLM
        expected_returns: Expected number of TMCs to extract
        
    Returns:
        List of extracted TMC strings
    """
    # TMC pattern matching regex
    pattern = r"Pd_(\w{6})-subgraph-(\d+)_(\w{6})-subgraph-(\d+)_(\w{6})-subgraph-(\d+)_(\w{6})-subgraph-(\d+)"
    
    # Possible delimiters for TMC in message
    delimiters = [
        "*TMC*", "<<<TMC>>>:", "<TMC>", "TMC:", " TMC"
    ]
    
    # Try to split message using different delimiters
    message_parts = None
    for delimiter in delimiters:
        if delimiter in message:
            message_parts = message.split(delimiter)
            break
            
    if message_parts is None:
        print("Unidentified pattern for splitting the LLM message.")
        return []
    
    # Extract TMCs
    tmcs = []
    for i in range(expected_returns):
        try:
            idx = -expected_returns + i
            match = re.search(pattern, message_parts[idx])
            
            if match:
                tmc = match.group()
                if len(tmc.split("_")) == 5:  # Validate TMC format
                    tmcs.append(tmc)
                else:
                    print(f"Invalid TMC format: {tmc}")
                    
        except IndexError:
            continue
            
    return tmcs


def hash_string_to_number(input_string, output_length=10):  
    """  
    Generate a numeric hash from a string.  
    
    Args:  
        input_string: String to be hashed  
        output_length: Desired length of the output number  
    
    Returns:  
        str: First n digits of the hashed number  
    """  
    hash_object = hashlib.sha256(input_string.encode())  
    hash_int = int(hash_object.hexdigest(), 16)  
    return str(hash_int)[:output_length]  


def save_row_to_csv(row, idx, file_name):  
    """  
    Save a single row to a CSV file.  
    
    Args:  
        row: DataFrame row to save  
        idx: Index of the row  
        file_name: Path to the CSV file  
    """  
    store_header = (idx == 0)  
    row.to_frame().T.to_csv(file_name, mode='a', header=store_header, index=False) 


# Text extraction helper functions

def extract_english_letters(text):
    """
    Extract only English letters, digits, and certain special characters from a given text.
    This is used to extract SMILES expression under condition that has other special characters. 
    
    Args:
        text: The text to process and extract characters from
    
    Returns:
        A string containing only the English letters, digits, and specified symbols
    """
    return ''.join(re.findall(r'[a-zA-Z#0-9\[\]\(\)=\-]', text))

def extract_integers(text):
    """
    Extract only integer characters from a given text.
    
    Args:
        text: The text to process and extract integer characters from
    
    Returns:
        A string containing only the integer characters
    """
    return ''.join(re.findall(r'[0-9\-]', text))
    

#prompt generation helper functions 
def dataframe_to_str(df):
    df_str = df.to_string(header=True, index=False, index_names=False).split('\n')
    return "\n".join([','.join(row.split()) for row in df_str])

#it creates the ligand dictionary from the ligand information table
def get_ligand_info(ligand_info_path):
    ligand_table = pd.read_csv(ligand_info_path)
    ligand_dict = {}
    for _, row in ligand_table.iterrows():
        ligand_dict[row["id"]] = (row["SMILES"], row["charge"], row["attach_idx"])
    return ligand_dict