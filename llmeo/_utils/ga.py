import random
from typing import Dict, List, Optional

import numpy as np


def ga_sample(
    df_samples_current,
    LIG_CHARGE: Dict[str, int],
    num_offspring: int = 1,
) -> List[str]:
    """
    Generate new transition metal complexes (TMCs) using genetic algorithm operations.
    
    Args:
        df_samples_current: DataFrame containing current TMC samples
        LIG_CHARGE: Dictionary mapping ligand IDs to their charges
        num_offspring: Number of new TMCs to generate
    
    Returns:
        List of new TMC strings in format "Pd_lig1_lig2_lig3_lig4"
    """
    if df_samples_current.empty:
        raise ValueError("Input DataFrame is empty")
    
    new_tmcs = []
    
    # Convert DataFrame rows to TMC strings
    tmcs = [
        f"Pd_{row['lig1']}_{row['lig2']}_{row['lig3']}_{row['lig4']}"
        for _, row in df_samples_current.iterrows()
    ]
    
    # Generate specified number of offspring
    for _ in range(num_offspring):
        # Randomly choose between crossover (50%) and mutation (50%)
        if np.random.random() > 0.5:
            new_tmc = crossover(tmcs, ligand_dict=LIG_CHARGE)
        else:
            # Randomly select a TMC for mutation
            parent_tmc = random.choice(tmcs)
            new_tmc = mutate(parent_tmc, ligand_dict=LIG_CHARGE)
            
        new_tmcs.append(new_tmc)
    
    return new_tmcs

def crossover(
    tmcs: List[str], 
    degree: Optional[int] = None, 
    ligand_dict: Optional[Dict[str, int]] = None
) -> str:
    """
    Perform crossover operation between TMCs.
    
    Args:
        tmcs: List of TMC strings to perform crossover on
        degree: Number of ligand positions to swap (1-3). If None, randomly chosen
        ligand_dict: Dictionary of ligand charges for charge validation
    
    Returns:
        A new TMC string created through crossover
    """
    # Split TMCs into lists of ligands (removing "Pd_")
    ligs = [tmc.split("_")[1:] for tmc in tmcs]
    
    # Select base TMC ligands to modify
    base_sample = random.choice(ligs)
    new_ligs = base_sample.copy()
    
    # Determine number of positions to swap if not specified
    if degree is None:
        degree = random.randint(1, 3)
    
    # Select random positions for crossover
    crossover_locs = random.sample(range(4), degree)
    
    # Get other samples excluding the base sample
    other_samples = [l for l in ligs if l != base_sample]
    if not other_samples:
        return "Pd_" + "_".join(base_sample)
    
    # Try to create valid TMC (charge between -1 and 1)
    max_attempts = 10
    for _ in range(max_attempts):
        # Perform crossover
        new_ligs = base_sample.copy()
        for loc in crossover_locs:
            donor_sample = random.choice(other_samples)
            new_ligs[loc] = donor_sample[loc]
        
        # Calculate total charge of new TMC
        tmc_charge = sum([ligand_dict[l] for l in new_ligs]) + 2  # +2 for Pd
        
        # If charge is valid, return new TMC
        if -1 <= tmc_charge <= 1:
            return "Pd_" + "_".join(new_ligs)
            
    # If no valid TMC found after max attempts, return original
    return "Pd_" + "_".join(base_sample)

def mutate(
    tmc: str,
    ligand_dict: Optional[Dict[str, int]] = None
) -> str:
    """
    Mutate a single TMC by replacing one ligand.
    
    Args:
        tmc: TMC string to mutate
        ligand_dict: Dictionary of ligand charges for charge validation
    
    Returns:
        A new TMC string created through mutation
    """
    # Split TMC into ligands
    ligs = tmc.split("_")[1:]  # Remove "Pd_"
    
    # Select random position to mutate (1-4)
    mutate_loc = random.randint(1, 4)
    to_be_replaced = ligs[mutate_loc - 1]
    
    # Calculate partial charge (total charge without the ligand to be replaced)
    # Formula: sum of remaining ligands + Pd charge(+2) - charge of replaced ligand
    partial_charge = (
        sum([ligand_dict[l] for l in ligs if l != "Pd"])
        - ligand_dict[to_be_replaced]
        + 2
    )
    
    # Find ligands that would result in valid total charge (-1 to 1)
    valid_ligands = [
        ligand for ligand, charge in ligand_dict.items()
        if -1 <= (partial_charge + charge) <= 1  # Check if resulting charge would be valid
        and ligand != to_be_replaced  # Don't replace with same ligand
    ]
    
    # If no valid ligands, return original TMC
    if not valid_ligands:
        return tmc
    
    # Select random ligand from valid options
    mutate_lig = random.choice(valid_ligands)
    ligs[mutate_loc - 1] = mutate_lig
    
    # Construct and return new TMC string
    return "Pd_" + "_".join(ligs)