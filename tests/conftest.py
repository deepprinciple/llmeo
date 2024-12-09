import os
import pytest
import pandas as pd
from typing import Dict

from llmeo import LLMConfig

@pytest.fixture
def test_config():
    """Basic LLM configuration for testing"""
    return LLMConfig(
        openai_api_key="test-key-openai",
        anthropic_api_key="test-key-anthropic",
        temperature=0.5,
        top_p=1.0,
        max_tokens=4096,
        system_prompt="You are a helpful assistant."
    )

@pytest.fixture
def sample_ligand_data():
    """Sample ligand dataset with various properties"""
    return pd.DataFrame({
        'id': ['WECJIA-subgraph-3', 'MEBXUN-subgraph-1', 'ULUSIE-subgraph-1',
                'OBONEA-subgraph-1', 'CORTOU-subgraph-2', 'IRIXUC-subgraph-3'],
        'smiles': ['CP(C)C', 'O', 'N', '[Br-]', '[I-]', '[C-]#N'],
        'charge': [0, 0, 0, -1, -1, -1],
        'connecting_atom': ['P', 'O', 'N', 'Br', 'I', 'C'],
        'connecting_index': [1, 1, 1, 1, 1, 1]
    })

@pytest.fixture
def sample_tmc_data():
    """Sample TMC dataset with various properties and iterations"""
    return pd.DataFrame({
        'id': [5606, 651, 117575, 49703],
        'polarisability': [212.397881, 245.335517, 138.954579, 100.220522],
        'gap': [3.245499549334, 2.257111830265, 1.343931999837, 1.36633170463],
        'lig1': ['CORTOU-subgraph-2', 'OBONEA-subgraph-1',
                 'CORTOU-subgraph-2', 'ULUSIE-subgraph-1'],
        'lig2': ['IRIXUC-subgraph-3', 'WECJIA-subgraph-3',
                 'ULUSIE-subgraph-1', 'MEBXUN-subgraph-1'],
        'lig3': ['WECJIA-subgraph-3', 'WECJIA-subgraph-3',
                 'CORTOU-subgraph-2', 'OBONEA-subgraph-1'],
        'lig4': ['WECJIA-subgraph-3', 'WECJIA-subgraph-3',
                 'OBONEA-subgraph-1', 'OBONEA-subgraph-1'],
        'iter': [0, 0, 0, 0]
    })

@pytest.fixture
def lig_charges() -> Dict[str, int]:
    """Dictionary of ligand charges"""
    return {
        'WECJIA-subgraph-3': 0,
        'MEBXUN-subgraph-1': 0,
        'ULUSIE-subgraph-1': 0,
        'OBONEA-subgraph-1': -1,
        'CORTOU-subgraph-2': -1,
        'IRIXUC-subgraph-3': -1
    }

@pytest.fixture
def mock_llm_response() -> str:
    """Sample LLM response for testing"""
    return """Based on the provided data and my chemistry knowledge, I'll propose three new TMCs that aim to have larger polarisability while maintaining a total charge of -1, 0, or 1. Here are my proposals:
    {<<<Explanation>>>: The high polarizability in this TMC likely comes from the combination of three cyano ligands (IRIXUC-subgraph-3) which provide strong electron-withdrawing character and extended conjugation, along with a phosphine ligand (WECJIA-subgraph-3) that can participate in π-backbonding., <<<TMC>>>: [Pd_WECJIA-subgraph-3_IRIXUC-subgraph-3_IRIXUC-subgraph-3_IRIXUC-subgraph-3], <<<TOTAL_CHARGE>>>: -1, <<<polarisability>>>: 182.4}
    {<<<Explanation>>>: This TMC combines an iodide ligand (CORTOU-subgraph-2) which is highly polarizable due to its large electron cloud, with three phosphine ligands (WECJIA-subgraph-3) that can enhance electron delocalization through π-backbonding., <<<TMC>>>: [Pd_CORTOU-subgraph-2_WECJIA-subgraph-3_WECJIA-subgraph-3_WECJIA-subgraph-3], <<<TOTAL_CHARGE>>>: 1, <<<polarisability>>>: 195.7}
    {<<<Explanation>>>: The combination of two different halide ligands (Br and I) which are highly polarizable due to their large electron clouds, together with two phosphine ligands (WECJIA-subgraph-3) creates a balanced electronic structure that enhances overall polarizability., <<<TMC>>>: [Pd_WECJIA-subgraph-3_OBONEA-subgraph-1_WECJIA-subgraph-3_CORTOU-subgraph-2], <<<TOTAL_CHARGE>>>: 0, <<<polarisability>>>: 201.3}
    
    These proposed TMCs are designed to have larger polarisabilities than the provided examples by incorporating ligands with extended π-systems, electron-donating or electron-withdrawing groups, and anionic ligands known to enhance polarisability. The total charge is maintained at -1, 0, or 1 for each TMC."""

@pytest.fixture
def mock_failed_llm_response() -> str:
    """Sample failed LLM response for testing error handling"""
    return """I apologize, but I cannot generate valid TMC combinations 
    due to insufficient data about the ligand properties."""

@pytest.fixture
def sample_search_space():
    """Large sample search space for testing"""
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "sample_space.csv"))

@pytest.fixture
def mock_opt_args():
    """Mock command line arguments for testing"""
    class OptArgs:
        def __init__(self):
            self.prop = "mpsg"
            self.model = "ga"
            self.num_iter = 5
            self.population = 4
            self.num_offspring = 3
            self.seed = 42
            self.strategy = "best"
            self.llm_config = "test_config.yaml"
            self.path = "test_path"
    return OptArgs()

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    import logging
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    return logger

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir

@pytest.fixture
def mock_llm_config_file(temp_output_dir):
    """Create a temporary LLM config file for testing"""
    config_path = temp_output_dir / "test_llm_config.yaml"
    config_content = """
    OPENAI_API_KEY: test-key-openai
    ANTHROPIC_API_KEY: test-key-anthropic
    temperature: 0.5
    top_p: 1.0
    max_tokens: 4096
    system_prompt: "You are a helpful assistant."
    """
    config_path.write_text(config_content)
    return str(config_path)
