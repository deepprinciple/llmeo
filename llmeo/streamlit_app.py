import streamlit as st
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llmeo.run_llmeo import main as run_optimization

def create_config_file(api_keys):
    """Create temporary config file with API keys"""
    config = {
        "OPENAI_API_KEY": api_keys["openai"],
        "ANTHROPIC_API_KEY": api_keys["anthropic"],
        "temperature": 0.5,
        "top_p": 1.0,
        "max_tokens": 4096
    }
    
    config_path = Path("./llm_config.yaml")
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f)
    return config_path

def format_help_text(text_dict):
    """Format help text with proper line breaks and bullet points"""
    return "\n\n".join([f"• {key}: {value}" for key, value in text_dict.items()])

def main():
    st.title("Property Optimization Platform")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Keys (with secure input)
        st.subheader("API Keys")
        api_keys = {
            "openai": st.text_input("OpenAI API Key", type="password"),
            "anthropic": st.text_input("Anthropic API Key", type="password")
        }
        
        # Dataset Selection
        st.subheader("Dataset Selection")
        dataset_type = st.selectbox(
            "Dataset",
            ["TMC (Transition Metal Complex)"],
            help=format_help_text({
                "TMC": "Transition Metal Complex dataset for property optimization",
                "Coming Soon": "Support for additional datasets will be added in future updates"
            })
        )
        
        # Optimization Problem Selection
        st.subheader("Optimization Settings")
        optimization_type = st.selectbox(
            "Optimization Type",
            ["Single Objective", "Multiple Objectives"]
        )
        
        # Property Selection based on optimization type
        if optimization_type == "Single Objective":
            property_type = st.selectbox(
                "Property to Optimize",
                ["gap", "polarisability"],
                help=format_help_text({
                    "gap": "HOMO-LUMO gap in electron volts (eV)",
                    "polarisability": "Molecular polarizability in atomic units (au)"
                })
            )
        else:
            property_type = st.selectbox(
                "Multi-Objective Strategy",
                ["pf", "mb", "mpsg"],
                help=format_help_text({
                    "pf": "Pareto frontier optimization - Find optimal trade-offs between properties",
                    "mb": "Maximize both properties simultaneously",
                    "mpsg": "Maximize polarisability while maintaining small gap"
                })
            )
        
        # Model Selection
        model_type = st.selectbox(
            "Model",
            ["ga", "o1-preview", "o1-mini", "gpt-4", "claude-3-5-sonnet-20240620"],
            help=format_help_text({
                "ga": "Genetic Algorithm - Fastest option with no API costs",
                "o1-preview": "OpenAI o1-preview model - Latest OpenAI model",
                "o1-mini": "OpenAI o1-mini model - Smaller, faster OpenAI model",
                "gpt-4": "GPT-4 model - Strong general-purpose model",
                "claude-3-5-sonnet-20240620": "Anthropic's Claude model - Advanced reasoning capabilities"
            })
        )
        
        # Optimization Parameters
        st.subheader("Optimization Parameters")
        num_iter = st.slider(
            "Number of Iterations", 
            1, 50, 20,
            help="Number of optimization iterations to run"
        )
        population = st.slider(
            "Population Size", 
            5, 50, 20,
            help="Size of the population in each iteration"
        )
        num_offspring = st.slider(
            "Number of Offspring", 
            1, 20, 10,
            help="Number of new candidates generated in each iteration"
        )
        
        # Strategy Selection
        strategy = st.selectbox(
            "Parent Selection Strategy",
            ["best", "all", "const"],
            help=format_help_text({
                "best": "Only use best performing TMCs as parents",
                "all": "Use all previously generated TMCs as potential parents",
                "const": "Use only initial population as parents"
            })
        )
        
        # Random Seed
        seed = st.number_input(
            "Random Seed", 
            value=0,
            help="Seed for reproducible results"
        )

    # Main content area
    st.header("Run Optimization")
    
    if st.button("Start Optimization"):
        # Validate API keys if needed
        if model_type != "ga":
            if not api_keys["openai"] and model_type in ["o1-preview", "o1-mini", "gpt-4"]:
                st.error("OpenAI API key is required for the selected model")
                return
            if not api_keys["anthropic"] and model_type == "claude-3-5-sonnet-20240620":
                st.error("Anthropic API key is required for the selected model")
                return
        
        # Create temporary config file
        config_path = create_config_file(api_keys)
        
        # Create results directory
        results_dir = Path("./llm-results")
        results_dir.mkdir(exist_ok=True)
        
        # Setup arguments
        args = argparse.Namespace(
            prop=property_type,
            num_iter=num_iter,
            population=population,
            num_offspring=num_offspring,
            seed=seed,
            model=model_type,
            strategy=strategy,
            llm_config=str(config_path),
            path=str(results_dir)
        )
        
        # Run optimization with progress bar
        with st.spinner("Running optimization..."):
            try:
                results = run_optimization(args)
                
                # Display results
                st.success("Optimization completed!")
                st.subheader("Results")
                st.dataframe(results)
                
                # Plot results
                st.subheader("Optimization Progress")
                fig = plot_optimization_progress(results)
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Error during optimization: {str(e)}")
            finally:
                # Cleanup temporary config file
                if config_path.exists():
                    config_path.unlink()

def plot_optimization_progress(results):
    """Create visualization of optimization progress"""
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if "gap" in results.columns and "polarisability" in results.columns:
        # For multi-objective optimization
        scatter = ax.scatter(
            results["gap"],
            results["polarisability"],
            c=results["iter"],
            cmap="viridis"
        )
        plt.colorbar(scatter, label="Iteration")
        ax.set_xlabel("HOMO-LUMO Gap (eV)")
        ax.set_ylabel("Polarisability (au)")
        ax.set_title("Optimization Progress")
    else:
        # For single objective optimization
        property_col = "gap" if "gap" in results.columns else "polarisability"
        ax.plot(results["iter"], results[property_col], marker='o')
        ax.set_xlabel("Iteration")
        ax.set_ylabel(property_col.capitalize())
        ax.set_title(f"{property_col.capitalize()} vs Iteration")
    
    return fig

if __name__ == "__main__":
    main() 