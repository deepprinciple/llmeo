from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
from llmeo.run_llmeo import (
    get_next_round_samples,
    get_prompt_and_props,
    main,
    move_one_iter,
)


# Test prompt and property selection
@pytest.mark.parametrize(
    "prop,expected_props",
    [
        ("gap", ["gap"]),
        ("polarisability", ["polarisability"]),
        ("pf", ["gap", "polarisability"]),
        ("mb", ["gap", "polarisability"]),
        ("mpsg", ["gap", "polarisability"]),
    ],
)
def test_get_prompt_and_props(prop, expected_props):
    """Test prompt and property selection for different optimization targets"""

    class OptMock:
        def __init__(self, prop):
            self.prop = prop

    prompt, props = get_prompt_and_props(OptMock(prop))
    assert props == expected_props
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_get_prompt_and_props_invalid():
    """Test invalid property selection"""

    class OptMock:
        prop = "invalid"

    with pytest.raises(ValueError, match="Invalid property"):
        get_prompt_and_props(OptMock())


# Test iteration movement
def test_move_one_iter_ga(
    mock_opt_args, sample_tmc_data, sample_search_space, lig_charges, mock_logger
):
    """Test one iteration of GA optimization"""
    mock_opt_args.model = "ga"
    mock_opt_args.strategy = "best"
    mock_opt_args.num_offspring = 3

    df_samples_current = sample_tmc_data.copy()
    df_samples = sample_tmc_data.copy()
    failed_messages = []

    new_df_current, new_df_samples, new_failed = move_one_iter(
        mock_opt_args,
        None,  # No model needed for GA
        0,  # iteration
        df_samples_current,
        df_samples,
        failed_messages,
        sample_search_space,
        "test_ligands",
        lig_charges,
        mock_logger,
    )

    assert isinstance(new_df_current, pd.DataFrame)
    assert isinstance(new_df_samples, pd.DataFrame)
    assert isinstance(new_failed, list)
    assert len(new_df_samples) == len(df_samples) + mock_opt_args.num_offspring


@patch("llmeo.run_llmeo.get_llm_response")
def test_move_one_iter_llm(
    mock_get_response,
    mock_opt_args,
    sample_tmc_data,
    sample_search_space,
    lig_charges,
    mock_logger,
    mock_llm_response,
):
    """Test one iteration of LLM optimization"""
    mock_opt_args.prop = "polarisability"
    mock_opt_args.model = "claude-3-5-sonnet-20240620"
    mock_opt_args.strategy = "all"
    mock_opt_args.num_offspring = 3

    # Mock LLM response
    mock_get_response.return_value = mock_llm_response

    df_samples_current = sample_tmc_data.copy()
    df_samples = sample_tmc_data.copy()
    failed_messages = []

    new_df_current, new_df_samples, new_failed = move_one_iter(
        mock_opt_args,
        MagicMock(),  # Mock LLM model
        0,  # iteration
        df_samples_current,
        df_samples,
        failed_messages,
        sample_search_space,
        "test_ligands",
        lig_charges,
        mock_logger,
    )

    assert isinstance(new_df_current, pd.DataFrame)
    assert isinstance(new_df_samples, pd.DataFrame)
    assert isinstance(new_failed, list)
    assert len(new_df_samples) == len(df_samples) + mock_opt_args.num_offspring
    assert mock_get_response.called


# Test different optimization strategies
@patch("llmeo.run_llmeo.get_llm_response")
@pytest.mark.parametrize("strategy", ["best", "all", "const"])
def test_different_strategies(
    mock_get_response,
    strategy,
    mock_opt_args,
    sample_tmc_data,
    sample_search_space,
    lig_charges,
    mock_logger,
    mock_llm_response,
):
    """Test different optimization strategies"""
    mock_opt_args.model = "claude-3-5-sonnet-20240620"
    mock_opt_args.prop = "polarisability"
    mock_opt_args.strategy = strategy

    # Mock LLM response
    mock_get_response.return_value = mock_llm_response

    df_samples_current = sample_tmc_data.copy()
    df_samples = sample_tmc_data.copy()
    failed_messages = []

    new_df_current, new_df_samples, _ = move_one_iter(
        mock_opt_args,
        None,
        0,
        df_samples_current,
        df_samples,
        failed_messages,
        sample_search_space,
        "test_ligands",
        lig_charges,
        mock_logger,
    )

    # Test the sample selection logic
    next_round_samples = get_next_round_samples(
        strategy, new_df_current, new_df_samples
    )

    if strategy == "best":
        assert len(next_round_samples) == len(new_df_current)
        pd.testing.assert_frame_equal(next_round_samples, new_df_current)
    elif strategy == "all":
        assert len(next_round_samples) == len(new_df_samples)
    elif strategy == "const":
        assert len(next_round_samples) == len(df_samples)
        assert (next_round_samples["iter"] == 0).all()


# Test main optimization loop
@patch("llmeo.run_llmeo.get_llm_response")
@patch("llmeo.run_llmeo.get_llm_model")
@pytest.mark.parametrize("model", ["o1-preview"])
def test_main_optimization_loop(
    mock_get_model,
    mock_get_response,
    mock_llm_response,
    model,
    mock_opt_args,
    sample_tmc_data,
    sample_search_space,
    sample_ligand_data,
    temp_output_dir,
):
    """Test main optimization loop"""
    mock_opt_args.model = model
    mock_opt_args.path = temp_output_dir

    if model == "o1-preview":
        # Mock LLM response
        mock_get_model.return_value = MagicMock()
        mock_get_response.return_value = mock_llm_response

    # Mock file read operation
    mock_file_content = "mock ligand content"
    mock_file = mock_open(read_data=mock_file_content)

    # Create a mock read_csv that returns different data based on the input file
    def mock_read_csv(filepath, *args, **kwargs):
        if "ligands" in filepath:
            return sample_ligand_data
        else:  # ground truth file
            return sample_search_space

    with patch("pandas.read_csv", side_effect=mock_read_csv), \
        patch.object(pd.DataFrame, "sample", return_value=sample_tmc_data), \
        patch("os.path.exists", return_value=True), \
        patch("builtins.open", mock_file):
        output_df = main(mock_opt_args)

    assert (
        len(output_df)
        == mock_opt_args.num_offspring * mock_opt_args.num_iter
        + mock_opt_args.population
    )
