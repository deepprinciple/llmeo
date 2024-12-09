
import os
import subprocess
from pathlib import Path

import uxtbpy
from rdkit import Chem

from .mol_analysis import check_structure_validity
from .utils import save_row_to_csv, hash_string_to_number


def find_index(smiles_string, atom_symbol, n):  
    """  
    Find the index of the nth occurrence of an atom in a SMILES string.  
    
    Args:  
        smiles_string: The SMILES representation of the molecule  
        atom_symbol: The atomic symbol to search for  
        n: The nth occurrence to find  
    
    Returns:  
        int: Index of the nth occurrence of the atom (1-based indexing)  
    """  
    mol = Chem.MolFromSmiles(smiles_string)  
    try:  
        n = int(n)  
    except:  
        return None  

    if not mol:  
        print(f"find Index {smiles_string} Invalid SMILES string")  
        return None  

    atom_indices = [atom.GetIdx() for atom in mol.GetAtoms()   
                   if atom.GetSymbol() == atom_symbol]  

    if n <= 0 or n > len(atom_indices):  
        raise ValueError(  
            f"The {n}-th occurrence of atom '{atom_symbol}' does not exist in the SMILES string."  
        )  

    return atom_indices[n - 1] + 1  


def molSimplify_xyz_generation(df, root_path, idx, fileName, tmc, sml_list):
    """
    Generate XYZ coordinates using MolSimplify.
    
    Args:
        df: DataFrame containing molecular data
        root_path: Base directory for file generation
        idx: Row index in DataFrame
        fileName: Unique identifier for the molecule
        tmc: Dictionary containing ligand information
        sml_list: List of SMILES strings for ligands
    """
    xyz_directory = Path(root_path) / "molSimplify_xyz" / str(fileName)
    
    if not xyz_directory.is_dir():
        parameters = [
            '-skipANN', 'True',
            '-core', 'Pd',
            '-geometry', 'sqp',
            '-lig', f"'{tmc[sml_list[0]]}'", f"'{tmc[sml_list[1]]}'", 
                   f"'{tmc[sml_list[2]]}'", f"'{tmc[sml_list[3]]}'",
            '-coord', '4',
            '-ligocc', '1,1,1,1',
            '-smicat', f"'[[{tmc['lig1_index']}],[{tmc['lig2_index']}],"
                      f"[{tmc['lig3_index']}],[{tmc['lig4_index']}]]'",
            '-oxstate', '2',
            '-rundir', f"'{root_path}/molSimplify_xyz/{fileName}'"
        ]
        
        command = ' '.join(['molsimplify', *parameters])
        print(command)
        result = subprocess.run(command, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, shell=True)
        print(result)
        df.loc[idx, "fileName"] = fileName
    else:
        print("Directory exists: ", xyz_directory)

def check_if_molSimplify_file_exist(root_path, fileName):
    """
    Check if MolSimplify output files exist and return their paths.
    
    Args:
        root_path: Base directory for working directory
        fileName: Unique identifier for the molecule
    
    Returns:
        tuple: (path to files, list of subdirectories)
    """
    path = Path(root_path) / "molSimplify_xyz" / str(fileName)

    # Get the only subdirectory inside 
    subdirs = [subdir for subdir in path.iterdir() if subdir.is_dir()]

    if len(subdirs) == 1:
        path = path / subdirs[0]

    subdirs = [subdir for subdir in path.iterdir() if subdir.is_dir()]
    
    if len(subdirs) == 1:
        path = path / subdirs[0]
    
    return path, subdirs

def xtb_calculation(fileName, path, storage_path, df, idx, charge):
    """
    Perform XTB calculations on the molecular structure.
    
    Args:
        fileName: Unique identifier for the molecule
        path: Path to input XYZ file
        storage_path: Path for saving results
        df: DataFrame containing molecular data
        idx: Row index in DataFrame
        charge: Total molecular charge
    
    Returns:
        tuple: (calculation results, continue flag)
    """
    tmp_dir = Path.cwd() / "xtb_xyz" / str(fileName)
    
    with open(path) as fh:
        xyz = fh.read()

    try:
        xtb_runner = uxtbpy.XtbRunner(xtb_directory=str(tmp_dir), 
                                     output_format='dict')
    except:
        print("Error: uxtbpy.XtbRunner failed")
        df.loc[idx, "_error"] = "Error: uxtbpy.XtbRunner failed"
        save_row_to_csv(df.loc[idx], idx, storage_path)
        return None, True

    xtb_parameters = [f'--opt tight --uhf 0 --norestart -v -c {charge}']
    
    try:
        result = xtb_runner.run_xtb_from_xyz(xyz, parameters=xtb_parameters)
        return result, False
    except:
        print("Error: xtb_runner.run_xtb_from_xyz failed")
        df.loc[idx, "_error"] = "Error: xtb_runner.run_xtb_from_xyz failed"
        save_row_to_csv(df.loc[idx], idx, storage_path)
        return None, True

def extract_lig_info_ligSpace(df, row, idx, lig_smile_list, lig_list, 
                            lig_connecting_atom_list, lig_connecting_atom_index):
    """
    Extract ligand information from the DataFrame for ligand space calculations.
    
    Args:
        df: DataFrame containing molecular data
        row: Current row being processed
        idx: Row index
        lig_smile_list: List of SMILES column names
        lig_list: List of ligand column names
        lig_connecting_atom_list: List of connecting atom column names
        lig_connecting_atom_index: List of connecting atom index column names
    
    Returns:
        tuple: (Dictionary of ligand information, continue flag)
    """
    flag_continue = False
    tmc = {}
    
    for i in range(4):
        # Extract SMILES
        tmc[lig_smile_list[i]] = row[lig_smile_list[i]]
        # Extract ligand ID
        tmc[lig_list[i]] = row[lig_list[i]]
        
        # Find connecting index
        try:
            index = find_index(tmc[lig_smile_list[i]], 
                             row[lig_connecting_atom_list[i]], 
                             row[lig_connecting_atom_index[i]])
            tmc[lig_list[i]+"_index"] = index
        except:
            print(f"Find Index Failed: {tmc[lig_smile_list[i]]} - {i}")
            df.loc[idx, "_error"] = f" - {tmc[lig_smile_list[i]]} invalid smiles - find index failed"
            flag_continue = True
            break
            
    return tmc, flag_continue

def calculate_fitness_ligand_space(df, root_path, storage_path, unbounded=False):
    """  
    Calculate chemical properties for a set of TMC structures.  
    
    This function processes each TMC structure through several steps:  
    1. Structure generation using molSimplify  
    2. Geometry optimization using XTB  
    3. Property calculation (HOMO-LUMO gap, polarisability)  
    4. Structure validation  
    
    Args:  
        df (pd.DataFrame): DataFrame containing TMC data with columns:  
            - lig1, lig2, lig3, lig4: Ligand IDs  
            - lig{n}_smiles: SMILES strings for each ligand  
            - lig{n}_element: Connecting atom elements  
            - lig{n}_index: Connecting atom indices  
            - charge: Total complex charge  
        root_path (str): Base directory for file generation and calculations  
        storage_path (str): Path for saving intermediate results  
    
    Returns:  
        pd.DataFrame: Updated DataFrame with additional columns:  
            - _error: Error messages if any  
            - fileName: Unique identifier for the structure  
            - homo_lumo_gap: Calculated HOMO-LUMO gap  
            - polarisability: Calculated molecular polarisability  
    
    Notes:  
        - Results are saved incrementally to storage_path  
        - Failed calculations are logged but don't stop the process  
        - Directory structure:  
            root_path/  
            ├── molSimplify_xyz/  # Initial structures  
            └── xtb_xyz/         # Optimized structures  
    """  
    # Initialize DataFrame columns
    df["_error"] = ""
    df["fileName"] = ""
    df["homo_lumo_gap"] = ""
    df["polarisability"] = ""
    
    # Define column name lists
    lig_list = ['lig1', 'lig2', 'lig3', 'lig4']
    lig_smile_list = ['lig1_smiles', 'lig2_smiles', 'lig3_smiles', 'lig4_smiles']
    lig_connecting_atom_list = ['lig1_element', 'lig2_element', 'lig3_element', 'lig4_element']
    lig_connecting_atom_index = ['lig1_index', 'lig2_index', 'lig3_index', 'lig4_index']

    if(unbounded):
        for i in range(4):
            df[lig_smile_list[i]] = df[lig_list[i]]

    
    # Create necessary directories
    os.makedirs(f"{root_path}/molSimplify_xyz/", exist_ok=True)
    os.makedirs(f"{root_path}/xtb_xyz/", exist_ok=True)
    
    # Process each row in the DataFrame
    for idx, row in df.iterrows():
        # Extract ligand information
        tmc, flag_continue = extract_lig_info_ligSpace(
            df, row, idx, lig_smile_list, lig_list, 
            lig_connecting_atom_list, lig_connecting_atom_index
        )
        if flag_continue:
            save_row_to_csv(df.loc[idx], idx, storage_path)
            continue
            
        # Generate unique filename
        fileName = hash_string_to_number(tmc["lig1"]+tmc["lig2"]+tmc["lig3"]+tmc["lig4"])
        if unbounded:
            charge = int(row["lig1_charge"])+int(row["lig2_charge"])+int(row["lig3_charge"])+int(row["lig4_charge"])
        else:
            charge = int(row["charge"])

        
        # Generate molecular structure
        molSimplify_xyz_generation(df, root_path, idx, fileName, tmc, lig_smile_list)
        
        # Check for generated files
        path, subdirs = check_if_molSimplify_file_exist(root_path, fileName)
        
        # Search for XYZ files
        directory = Path(path)
        files = list(directory.rglob('*.xyz'))
        if len(files) == 0:
            print("No xyz files found: ", str(path))
            save_row_to_csv(df.loc[idx], idx, file_name=storage_path)
            continue
        
        if "badjob" in str(files[0]):
            print("Bad file: ", str(files[0]))
            df.loc[idx, "_error"] = f"Bad Structure: {fileName} MolSimplify failed"
            save_row_to_csv(df.loc[idx], idx, file_name=storage_path)
            continue
        
        # Set paths
        path = path / subdirs[0] / files[0]
        mol_xyz_path = path
        
        # Run XTB calculations
        result, continue_flag = xtb_calculation(fileName, path, storage_path, df, idx, charge)
        if continue_flag:
            continue
        
        # Extract properties
        gap = result["homo_lumo_gap"]
        polar = result["polarisability"]
        xtb_xyz_path = Path.cwd() / "xtb_xyz" / fileName / "xtbopt.xyz"
        
        # Validate structure
        continue_flag = check_structure_validity(df, xtb_xyz_path, mol_xyz_path, storage_path, idx, result)
        if continue_flag:
            continue
        
        # Store results
        print("HomoLumo gap: ", gap)
        print("Polarisability: ", polar)
        df.loc[idx, "fileName"] = fileName
        df.loc[idx, "homo_lumo_gap"] = gap
        df.loc[idx, "polarisability"] = polar
        
        # Save results
        save_row_to_csv(df.loc[idx], idx, file_name=storage_path)
    
    return df