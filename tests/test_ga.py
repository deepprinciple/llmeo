import pandas as pd
import pytest
from llmeo import ga_sample


def test_ga_sample_basic(sample_tmc_data, lig_charges):
    """Test basic GA sampling functionality"""
    offspring = ga_sample(sample_tmc_data, lig_charges, num_offspring=2)

    assert len(offspring) == 2
    for tmc in offspring:
        # Check TMC format
        assert tmc.startswith("Pd_")
        parts = tmc.split("_")
        assert len(parts) == 5

        # Check ligand IDs are valid
        ligs = parts[1:]
        for lig in ligs:
            assert lig in lig_charges

        # Check total charge is valid (-1, 0, or 1)
        total_charge = sum(lig_charges[lig] for lig in ligs) + 2  # +2 for Pd
        assert total_charge in [-1, 0, 1]


def test_ga_sample_empty_input():
    """Test GA sampling with empty input"""
    empty_df = pd.DataFrame(
        columns=["id", "polarisability", "gap", "lig1", "lig2", "lig3", "lig4", "iter"]
    )
    lig_charges = {"WECJIA-subgraph-3": 0, "OBONEA-subgraph-1": -1}

    with pytest.raises(ValueError, match="Input DataFrame is empty"):
        ga_sample(empty_df, lig_charges, num_offspring=1)


def test_ga_sample_charge_constraints(sample_tmc_data):
    """Test GA sampling with various charge constraints"""
    # Test with ligands that would make invalid charge combinations
    invalid_charges = {
        "WECJIA-subgraph-3": -1,
        "MEBXUN-subgraph-1": -1,
        "ULUSIE-subgraph-1": -1,
        "OBONEA-subgraph-1": -1,
        "CORTOU-subgraph-2": -1,
        "IRIXUC-subgraph-3": -1,
    }

    offspring = ga_sample(sample_tmc_data, invalid_charges, num_offspring=5)

    tmcs = [
        f"Pd_{row['lig1']}_{row['lig2']}_{row['lig3']}_{row['lig4']}"
        for _, row in sample_tmc_data.iterrows()
    ]
    valid_offspring = [tmc for tmc in offspring if tmc not in tmcs]
    assert len(valid_offspring) == 0


@pytest.mark.parametrize("input_size", [1, 5, 10, 20])
def test_ga_sample_different_population_sizes(sample_tmc_data, lig_charges, input_size):
    offspring = ga_sample(sample_tmc_data, lig_charges, num_offspring=input_size)

    assert len(offspring) == input_size
