import os
from itertools import product
from typing import Dict, List, Set, Tuple

import pandas as pd
from llmeo._utils.mol_calculation import calculate_fitness_ligand_space


class TMCGenerator:
    """Generator for Pd+2 centered square planar transition metal complexes (TMCs)"""
    
    def __init__(self, ligand_pool_path: str):
        """
        Initialize TMC generator with ligand pool file
        
        Args:
            ligand_pool_path: Path to CSV file containing ligand information
        """
        self.ligand_df = pd.read_csv(ligand_pool_path)
        self.charge_dict = self._create_charge_dict()
        
    def _create_charge_dict(self) -> Dict[str, int]:
        """Create dictionary mapping ligand IDs to their charges"""
        return dict(zip(self.ligand_df['id'], self.ligand_df['charge']))
    
    def _is_rotation_duplicate(self, combo: Tuple[str], seen: Set[Tuple[str]]) -> bool:
        """
        Check if a TMC combination is a rotational duplicate
        
        Args:
            combo: Tuple of 4 ligand IDs
            seen: Set of previously seen combinations
            
        Returns:
            bool: True if combination is a duplicate
        """
        rotations = [combo[i:] + combo[:i] for i in range(4)]
        return any(rot in seen for rot in rotations)
    
    def _is_charge_valid(self, ligands: List[str]) -> bool:
        """
        Check if TMC total charge is within allowed range (-1 to 1)
        
        Args:
            ligands: List of 4 ligand IDs
            
        Returns:
            bool: True if charge is valid
        """
        total_charge = sum(self.charge_dict[lig] for lig in ligands) + 2  # +2 for Pd
        return -1 <= total_charge <= 1
    
    def generate_tmc_combinations(self) -> pd.DataFrame:
        """
        Generate all valid TMC combinations
        
        Returns:
            DataFrame containing valid TMC combinations with their properties
        """
        ligands = self.ligand_df["id"].tolist()
        seen_combinations = set()
        valid_combinations = []
        
        # Generate all possible 4-ligand combinations
        for combo in product(ligands, repeat=4):
            if not self._is_rotation_duplicate(combo, seen_combinations):
                seen_combinations.add(combo)
                if self._is_charge_valid(combo):
                    charge = sum(self.charge_dict[lig] for lig in combo) + 2
                    valid_combinations.append((*combo, charge))
        
        # Create DataFrame with valid combinations
        return pd.DataFrame(
            valid_combinations,
            columns=['lig1', 'lig2', 'lig3', 'lig4', 'charge']
        )
    
    def add_ligand_properties(self, tmc_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add ligand properties to TMC combinations
        
        Args:
            tmc_df: DataFrame containing TMC combinations
            
        Returns:
            DataFrame with added ligand properties
        """
        # Create lookup dictionary for ligand properties
        lig_properties = {
            row['id']: (
                row['connecting atom element'],
                row['connecting atom index'],
                row['SMILES']
            )
            for _, row in self.ligand_df.iterrows()
        }
        
        # Add properties for each ligand
        for i in range(1, 5):
            lig_col = f'lig{i}'
            tmc_df[f'{lig_col}_element'] = tmc_df[lig_col].map(
                lambda x: lig_properties[x][0]
            )
            tmc_df[f'{lig_col}_index'] = tmc_df[lig_col].map(
                lambda x: lig_properties[x][1]
            )
            tmc_df[f'{lig_col}_smiles'] = tmc_df[lig_col].map(
                lambda x: lig_properties[x][2]
            )
            
        return tmc_df

def main():
    """  
    Main function to generate TMCs and calculate their properties.  
    
    Process:  
    1. Loads ligand pool data  
    2. Generates valid TMC combinations  
    3. Adds ligand properties to combinations  
    4. Calculates chemical properties using XTB  
    5. Saves results to CSV  
    
    File Structure:  
    - Input:  
        - data/ligands10_maxBoth.csv: Ligand pool data  
    - Intermediate:  
        - lig10_Space.csv: Storage for intermediate calculation results  
    - Output:  
        - ligand_pool_calculated_result.csv: Final results with all properties  
    
    Note:  
        Property calculations can take multiple days depending on the machine  
        and number of combinations.  
    """  
    # Setup paths
    root_path = os.path.dirname(os.path.abspath(__file__))
    ligand_pool_path = os.path.join(root_path, "../data", "ligands10_maxBoth.csv")
    output_path = os.path.join(root_path, "../data", "ligand_pool_calculated_result.csv")
    space_path = os.path.join(root_path, "../data", "lig10_Space.csv")
    
    # Generate TMCs
    generator = TMCGenerator(ligand_pool_path)
    tmc_combinations = generator.generate_tmc_combinations()
    tmc_with_properties = generator.add_ligand_properties(tmc_combinations)
    
    print(f"Generated {len(tmc_with_properties)} valid TMC combinations")
    
    # Calculate properties
    result = calculate_fitness_ligand_space(
        tmc_with_properties,
        root_path,
        space_path
    )
    
    # Save results
    result.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
