import numpy as np
from scipy.sparse.csgraph import connected_components
from molSimplify.Classes.mol3D import mol3D
import numpy as np

# List of chemical elements by their symbols
element_identifiers = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
                    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K',
                    'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni',
                    'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb',
                    'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
                    'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs',
                    'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd',
                    'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                    'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb',
                    'Bi', 'Po', 'At', 'Rn']

# Atomic numbers for transition metals, organized by blocks
transition_metal_atomic_numbers = [
    # First block
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    # Second block                          
    39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    # Lanthanides
    57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
    # Third block
    72, 73, 74, 75, 76, 77, 78, 79, 80,
    # Actinides
    89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103,
    # Additional elements
    104, 105, 106, 107, 108, 109, 110, 111, 112
]

def get_radius_adjacency_matrix(positions: list, radius_cutoff: float):
    """
    Creates an adjacency matrix based on distance between atoms.

    Args:
        positions: List of atomic positions
        radius_cutoff: Maximum distance for considering atoms as connected

    Returns:
        numpy.ndarray: Adjacency matrix
    """
    adjacency_matrix = np.zeros((len(positions), len(positions)))

    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            if (
                np.linalg.norm(np.array(positions[i]) - np.array(positions[j]))
                <= radius_cutoff
            ):
                adjacency_matrix[i, j] = adjacency_matrix[j, i] = 1

    return adjacency_matrix


def radius_graph_is_connected(positions: list, radius_cutoff: float):
    """
    Determines if a molecular graph is fully connected.

    Args:
        positions: List of atomic positions
        radius_cutoff: Maximum distance for considering atoms as connected

    Returns:
        bool: True if graph is connected, False otherwise
    """
    adj = get_radius_adjacency_matrix(positions, radius_cutoff)
    n_connected_components = connected_components(adj)[0]
    return n_connected_components == 1


def parse_xyz(xyz: str):
    """
    Parses XYZ format string into atoms and positions.

    Args:
        xyz: String containing XYZ format molecular data

    Returns:
        tuple: (list of atom symbols, list of atomic positions)
    """
    atoms = []
    positions = []

    lines = xyz.split("\n")
    for i in range(2, len(lines)):
        line_split = lines[i].split()

        if len(line_split) != 4:
            break

        atoms.append(line_split[0])
        positions.append([float(line_split[j]) for j in [1, 2, 3]])

    return atoms, positions


def compare_connecting_idx(xtb_xyz_path, molSimp_xyz_path):
    """
    Compare molecular graphs before and after optimization.

    Args:
        xtb_xyz_path: Path to XTB optimized structure
        molSimp_xyz_path: Path to MolSimplify generated structure

    Returns:
        bool: True if molecular graphs are identical for center metal atom
    """
    mol_opt = mol3D()
    mol_opt.readfromxyz(xtb_xyz_path)
    mol_opt.createMolecularGraph(oct=False)

    mol_init = mol3D()
    mol_init.readfromxyz(molSimp_xyz_path)
    mol_init.createMolecularGraph(oct=False)

    return np.array_equal(mol_opt.graph[0], mol_init.graph[0])


def check_structure_validity(df, xtb_xyz_path, mol_xyz_path, storage_path, idx, result):
    """
    Validate the optimized molecular structure.

    Args:
        df: DataFrame containing molecular data
        xtb_xyz_path: Path to XTB optimized structure
        mol_xyz_path: Path to MolSimplify generated structure
        storage_path: Path for saving results
        idx: Row index in DataFrame
        result: XTB calculation results

    Returns:
        bool: True if structure is invalid and should be skipped
    """
    if not compare_connecting_idx(xtb_xyz_path, mol_xyz_path):
        print("Connecting indices different")
        df.loc[idx, "_error"] = "Connecting indices change, Bad Optimized Structure"
        df.loc[idx].to_frame().T.to_csv(
            storage_path, mode="a", header=(idx == 0), index=False
        )
        return True

    is_connected = radius_graph_is_connected(parse_xyz(result["optimised_xyz"])[1], 3.0)
    if not is_connected:
        print("Graph not connected")
        df.loc[idx, "_error"] = "Graph not connected, metal bond is break after xtb"
        df.loc[idx].to_frame().T.to_csv(
            storage_path, mode="a", header=(idx == 0), index=False
        )
        return True

    return False
