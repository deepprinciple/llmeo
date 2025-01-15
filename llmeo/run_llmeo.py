import argparse
import logging
import os
import sys
from uuid import uuid4

import pandas as pd
from llmeo._utils.ga import ga_sample
from llmeo._utils.llm import GPT4, Claude3, GPTo1, Gemini, LLMConfig, LLMError
from llmeo._utils.utils import (find_tmc_in_space, make_prompt,
                          retrive_tmc_from_message)
from llmeo.prompts import (OFF_SPRING_MAP, PROMPT_G, PROMPT_MB, PROMPT_MPSG,
                           PROMPT_P, PROMPT_PF)


def get_llm_model(opt):
    """Initialize and return appropriate LLM model based on options"""
    config = LLMConfig.from_yaml(opt.llm_config)
    try:
        if opt.model == "o1-preview":
            model = GPTo1(config, name="o1-preview")
        elif opt.model == "o1-mini":
            model = GPTo1(config, name="o1-mini")
        elif opt.model == "gpt-4":
            model = GPT4(config)
        elif opt.model == "claude-3-5-sonnet-20240620":
            model = Claude3(config)
        elif opt.model == "o1":
            model = GPTo1(config, name="o1")
        elif opt.model == "gemini":
            model = Gemini(config, name="gemini-2.0-flash-thinking-exp")
 
        model.create()
        return model
    except LLMError as e:
        raise RuntimeError(f"Failed to initialize LLM model: {str(e)}")

def get_prompt_and_props(opt):
    """Get appropriate prompt template and properties based on optimization target"""
    props = [opt.prop]
    
    if opt.prop == "gap":
        PROMPT = PROMPT_G
    elif opt.prop == "polarisability":
        PROMPT = PROMPT_P
    elif opt.prop == "pf":
        PROMPT = PROMPT_PF
        props = ["gap", "polarisability"]
    elif opt.prop == "mb":
        PROMPT = PROMPT_MB
        props = ["gap", "polarisability"]
    elif opt.prop == "mpsg":
        PROMPT = PROMPT_MPSG
        props = ["gap", "polarisability"]
    else:
        raise ValueError(f"Invalid property: {opt.prop}")
        
    return PROMPT, props

def get_llm_response(model, prompt):
    """Get response from LLM model with appropriate system prompt"""

    system_prompt = "You are a helpful agent who can perform multi-objective optimization for a transition metal complex for certain chemical properties based on your chemistry knowledge."

    return model.call(prompt, system=system_prompt)
    
def get_pareto_frontier(
    df: pd.DataFrame, 
    objective1: str, 
    objective2: str, 
    maximize1: bool = True, 
    maximize2: bool = True
) -> pd.DataFrame:
    """
    Computes the Pareto frontier for two objectives.

    Parameters:
        df (pd.DataFrame): DataFrame containing the data points with two objective columns.
        objective1 (str): Column name of the first objective.
        objective2 (str): Column name of the second objective.
        maximize1 (bool): True to maximize objective1, False to minimize it.
        maximize2 (bool): True to maximize objective2, False to minimize it.

    Returns:
        pd.DataFrame: DataFrame containing the Pareto-optimal points.
    """
    data = df.copy()
    
    # Adjust objectives based on optimization direction
    if not maximize1:
        data[objective1] = -data[objective1]
    if not maximize2:
        data[objective2] = -data[objective2]
        
    # Sort by first objective
    data.sort_values(by=objective1, ascending=False, inplace=True)
    
    # Find Pareto-optimal points
    pareto_indices = []
    best_obj2 = float('-inf')
    
    for index, row in data.iterrows():
        if row[objective2] > best_obj2:
            pareto_indices.append(index)
            best_obj2 = row[objective2]
            
    return df.loc[pareto_indices]

def get_next_round_samples(strategy, df_samples_current, df_samples):
    """
    Determine next round samples based on strategy.
    
    Args:
        strategy: Strategy to use ("best", "all", or "const")
        df_samples_current: Current population DataFrame
        df_samples: Historical samples DataFrame
        
    Returns:
        DataFrame: Selected samples for next round
    """
    if strategy == "best":
        return df_samples_current
    elif strategy == "const":
        return df_samples[df_samples["iter"] == 0]
    else:  # "all" strategy
        return df_samples.drop_duplicates(subset=["id"]).sample(frac=1.0)

def move_one_iter(
    opt,
    model,
    ii,
    df_samples_current,
    df_samples,
    failed_messages,
    df_1Mspace,
    ligands,
    LIG_CHARGE,
    logger,
):
    """  
    Perform one iteration of the optimization process.  
    
    Args:  
        opt: Command line arguments  
        model: LLM model instance or None for GA  
        ii: Current iteration number  
        df_samples_current: Current population DataFrame  
        df_samples: Historical samples DataFrame  
        failed_messages: List of failed LLM messages  
        df_1Mspace: Complete search space DataFrame  
        ligands: String containing ligand information  
        LIG_CHARGE: Dictionary mapping ligand IDs to charges  
        logger: Logger instance
        
    Returns:  
        tuple: (updated_current_samples, updated_historical_samples, updated_failed_messages)  
    """  
    # Determine next round samples based on strategy
    next_round_samples_in = get_next_round_samples(opt.strategy, df_samples_current, df_samples)

    # Get appropriate prompt and properties
    PROMPT, props = get_prompt_and_props(opt)

    # Generate TMCs using either LLM or GA approach
    if opt.model != "ga":
        prompt = make_prompt(
            PROMPT,
            ligands,
            next_round_samples_in,
            LIG_CHARGE,
            num_samples=OFF_SPRING_MAP[opt.num_offspring],
            props=props,
        )
        
        try:
            text_out = get_llm_response(model, prompt)
            logger.info(f"message: {text_out}")
            
            tmcs = retrive_tmc_from_message(
                message=text_out,
                expected_returns=opt.num_offspring,
            )
            if not len(tmcs):
                failed_messages.append(text_out)
                
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return df_samples_current, df_samples, failed_messages

    else:
        tmcs = ga_sample(
            next_round_samples_in,
            LIG_CHARGE,
            num_offspring=opt.num_offspring,
        )

    # Process results
    df_new = find_tmc_in_space(df_1Mspace, tmcs)
    if df_new is None:
        logger.warning(f"no match: {tmcs}")
        if opt.model != "ga":
            failed_messages.append(text_out)
        return df_samples_current, df_samples, failed_messages

    logger.info(f"{ii}, proposed: {tmcs}, {df_new[props[0]].values}")

    df_new["iter"] = ii + 1
    df_samples = pd.concat([df_samples, df_new])
    
    # Update current samples based on optimization property
    if opt.prop == "pf":
        df_samples["x"] = df_samples.apply(lambda row: row["gap"] * row["polarisability"], axis=1)
        df_samples_current = get_pareto_frontier(df_samples, "gap", "polarisability")
        _df = df_samples_current[["id", "x", "polarisability", "gap", "iter"]]
    elif opt.prop == "mb":
        df_samples["x"] = df_samples.apply(lambda row: row["gap"] * row["polarisability"], axis=1)
        df_samples_current = df_samples.drop_duplicates(subset=["id"]).nlargest(opt.population, "x")
        _df = df_samples_current[["id", "x", "polarisability", "gap", "iter"]]
    elif opt.prop == "mpsg":
        df_samples["alpha/g"] = df_samples.apply(lambda row: row["polarisability"] / row["gap"], axis=1)
        df_samples_current = df_samples.drop_duplicates(subset=["id"]).nlargest(opt.population, "alpha/g")
        _df = df_samples_current[["id", "alpha/g", "polarisability", "gap", "iter"]]
    else:
        df_samples_current = df_samples.drop_duplicates(subset=["id"]).nlargest(opt.population, props[0])
        _df = df_samples_current[["id", "polarisability", "gap", "iter"]]

    logger.info(f"current: {_df}")

    return df_samples_current, df_samples, failed_messages

def main(opt):
    # Set up logging and directories
    os.makedirs(opt.path, exist_ok=True)
    _id = str(uuid4()).split("-")[0]
    logfile = f"{opt.path}/{opt.prop}-pop_{opt.population}-offspring_{opt.num_offspring}-iter_{opt.num_iter}-seed_{opt.seed}-model_{opt.model}-ss_{opt.strategy}-{_id}.log"
    csvfile = f"{opt.path}/{opt.prop}-pop_{opt.population}-offspring_{opt.num_offspring}-iter_{opt.num_iter}-seed_{opt.seed}-model_{opt.model}-ss_{opt.strategy}-{_id}.csv"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Command used: %s", " ".join(sys.argv))
    logger.info("Options: %s", vars(opt))

    # Initialize LLM model if needed
    model = None
    if opt.model != "ga":
        try:
            model = get_llm_model(opt)
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {str(e)}")
            return

    # Load data
    ligand_file = "../data/1M-space_50-ligands-full.csv"
    gt_tmc_file = "../data/ground_truth_fitness_values.csv"

    df_ligands = pd.read_csv(ligand_file)
    LIG_CHARGE = {row["id"]: row["charge"] for _, row in df_ligands.iterrows()}

    with open(ligand_file, "r") as fo:
        ligands = fo.read()

    df_1Mspace = pd.read_csv(gt_tmc_file)
    # df_1Mspace = df_1Mspace.rename(columns={"homo_lumo_gap": "gap"})

    # Initialize samples
    df_samples = df_1Mspace.sample(opt.population, random_state=opt.seed)
    df_samples["iter"] = 0
    df_samples_current = df_samples.copy()

    # Main optimization loop
    failed_messages = []
    for ii in range(opt.num_iter):
        df_samples_current, df_samples, failed_messages = move_one_iter(
            opt,
            model,
            ii,
            df_samples_current,
            df_samples,
            failed_messages,
            df_1Mspace,
            ligands,
            LIG_CHARGE,
            logger,
        )
        df_samples.to_csv(csvfile, index=False)

    logger.info("===== End =====")
    df_samples.to_csv(csvfile, index=False)
    return df_samples

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Property selection  
    parser.add_argument(  
        "--prop",  
        type=str,  
        default="gap",  
        choices=["gap", "polarisability", "pf", "mb", "mpsg"],  
        help="""  
        Optimization target property:  
        - gap: Maximize HOMO-LUMO gap for better stability  
        - polarisability: Maximize molecular polarisability for optical applications  
        - pf: Optimize Pareto frontier between gap and polarisability (multi-objective)  
        - mb: Maximize both properties simultaneously (multi-objective)  
        - mpsg: Maximize polarisability while maintaining small gap (constrained optimization)  
        """  
    )  

    # Optimization parameters  
    parser.add_argument(  
        "--num_iter",   
        type=int,   
        default=20,  
        help="Number of optimization iterations to run. Higher values allow for more exploration but increase computation time"  
    )  
    
    parser.add_argument(  
        "--population",   
        type=int,   
        default=20,  
        help="Size of the population in each generation. Larger populations provide more diversity but require more computation"  
    )  
    
    parser.add_argument(  
        "--num_offspring",   
        type=int,   
        default=10,  
        help="Number of new TMCs to generate in each iteration. Should be less than or equal to population size"  
    )  
    
    parser.add_argument(  
        "--seed",   
        type=int,   
        default=0,  
        help="Random seed for initial population sampling."  
    )  

    # Method selection  
    parser.add_argument(  
        "--model",  
        type=str,  
        default="ga",  
        choices=["ga", "o1", "o1-preview", "o1-mini", "gpt-4", "claude-3-5-sonnet-20240620", "gemini"],  

        help="""  
        Model to use for TMC generation:  
        - ga: Genetic Algorithm (fastest, no API costs)  
        - o1: OpenAI o1 model  
        - o1-preview: OpenAI o1-preview model  
        - o1-mini: OpenAI o1-mini model  
        - gpt-4: GPT-4o model 
        - claude-3-5-sonnet-20240620: Anthropic's Claude model  
        - gemini: Google Gemini model  
        """  
    )  
    
    parser.add_argument(  
        "--strategy",  
        type=str,  
        default="all",  
        choices=["best", "all", "const"],  
        help="""  
        Strategy for selecting parent TMCs:  
        - best: Only use best performing TMCs as parents  
        - all: Use all previously generated TMCs as potential parents  
        - const: Use only initial population as parents
        """  
    )  

    # LLM configuration  
    parser.add_argument(  
        "--llm_config",   
        type=str,   
        default="./llm_config.yaml",  
        help="Path to YAML configuration file containing LLM API keys and settings"  
    )  

    # Output path  
    parser.add_argument(  
        "--path",   
        type=str,   
        default="./llm-results",  
        help="Directory path where optimization results and logs will be saved"  
    )  

    opt = parser.parse_args()
    main(opt)
