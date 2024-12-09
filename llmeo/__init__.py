"""
LLM-EO: LLM-guided Evolutionary Optimization for TMC Design

A package for optimizing transition metal complexes (TMCs) using large language models (LLMs) and quantum chemistry calculations.
"""

# Import core functionality
from llmeo._utils.llm import (
    LLMConfig,
    LLMError,
    GPT4,
    GPTo1,
    Claude3
)

from llmeo._utils.ga import (
    ga_sample,
    crossover,
    mutate
)

# Define public API
__all__ = [
    # LLM related
    "LLMConfig",
    "LLMError",
    "GPT4",
    "GPTo1", 
    "Claude3",
    
    # Genetic Algorithm
    "ga_sample",
    "crossover",
    "mutate",
]