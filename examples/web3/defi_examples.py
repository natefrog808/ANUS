"""
Anus AI Web3 Module - DeFi Examples

This script demonstrates DeFi-focused functionality of the Anus AI Web3 module,
including token swaps, liquidity provision, yield farming analysis, protocol 
interaction, and DeFi strategy creation.

Usage:
    python defi_examples.py

Note: You need appropriate API keys for blockchain providers in your configuration.
Some examples require specific accounts with funds for transactions.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal

# Add the parent directory to the path to allow running this script directly
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(parent_dir)

# Import Anus AI components
from anus.web3 import Web3Agent, Web3Society
from anus.web3.utils import wei_to_eth, eth_to_wei

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# Configuration
# =========================

# You can provide configuration here or use a config file
CONFIG = {
    "ethereum_provider": os.environ.get("ETHEREUM_PROVIDER", "https://eth-mainnet.g.alchemy.com/v2/demo"),
    "memory_path": "./web3_agent_memory",
    "coordination_strategy": "hierarchical"
}

# Example wallet (DON'T USE REAL PRIVATE KEYS HERE)
DEMO_WALLET = {
    "address": "0xYourWalletAddress",  # Replace with your wallet
    "private_key": None,  # Never put private keys in code
}

# =========================
# Example Functions
# =========================

def example_token_swap_quote(agent: Web3Agent):
    """Example: Get a token swap quote."""
    logger.info("=== Example: Token Swap Quote ===")
    
    # Get quote for swapping 1 ETH to USDC
    quote = agent.get_swap_quote(
        token_in="ETH",
        token_out="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        amount_in=1.0,
        protocol="uniswap_v2"
    )
    
    if "error" not in quote:
        logger.info(f"Swap Quote: 1 ETH = {quote['amount_out']} USDC")
        logger.info(f"Price Impact: {quote['price_impact']}")
        logger.info(f"Route: {' -> '.join(quote['route'])}")
    else:
        logger.error(f"Error getting swap quote: {quote['error']}")
    
    return quote

def example_get_liquidity_pool_info(agent: Web3Agent):
    """Example: Get information about a liquidity pool."""
    logger.info("\n=== Example: Liquidity Pool Info ===")
    
    # Get ETH-USDC pool information on Uniswap V2
    pool_info = agent.run_tool("defi", {
        "action": "get_reserves",
        "protocol": "uniswap_v2",
        "token_a": "ETH",
        "token_b": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
    })
    
    if "error" not in pool_info:
        logger.info(f"Pool Reserves:")
        logger.info(f"  {pool_info['token_a']}: {pool_info['reserve_a']}")
        logger.info(f"  {pool_info['token_b']}: {pool_info['reserve_b']}")
        logger.info(f"Price:")
        logger.info(f"  1 {pool_info['token_a']} = {pool_info['price_a_in_b']} {pool_info['token_b']}")
        logger.info(f"  1 {pool_info['token_b']} = {pool_info['price_b_in_a']} {pool_info['token_a']}")
    else:
        logger.error(f"Error getting pool info: {pool_info['error']}")
    
    return pool_info

def example_aave_user_data(agent: Web3Agent):
    """Example: Get user data from Aave protocol."""
    logger.info("\n=== Example: Aave User Data ===")
    
    # Use a known address with Aave positions (example)
    address = "0x57E04786E231Af3343562C062E0d058F25daCE9E"
    
    # Get Aave user data
    aave_data = agent.run_tool("defi", {
        "action": "get_user_data",
        "protocol": "aave",
        "address": address
    })
    
    if "error" not in aave_data:
        logger.info(f"Aave User Data:")
        logger.info(f"  Total Collateral (ETH): {aave_data['total_collateral_eth']}")
        logger.info(f"  Total Debt (ETH): {aave_data['total_debt_eth']}")
        logger.info(f"  Available to Borrow (ETH): {aave_data['available_borrows_eth']}")
        logger.info(f"  Liquidation Threshold: {aave_data['current_liquidation_threshold']}%")
        logger.info(f"  LTV: {aave_data['ltv']}%")
        logger.info(f"  Health Factor: {aave_data['health_factor']}")
    else:
        logger.error(f"Error getting Aave user data: {aave_data['error']}")
    
    return aave_data

def example_token_swap_transaction(agent: Web3Agent):
    """Example: Execute a token swap (simulation only)."""
    logger.info("\n=== Example: Token Swap Transaction (SIMULATION) ===")
    
    # This is a simulation - no real transaction will be executed
    logger.info("This is a simulated example - no real transaction will be executed")
    
    if not DEMO_WALLET["address"] or DEMO_WALLET["private_key"] == None:
        logger.info("Wallet not configured - using simulation mode")
        
        # Simulate the swap call
        swap_result = {
            "transaction_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "status": "simulation",
            "from": "0xYourAddress",
            "token_in": "ETH",
            "token_out": "USDC",
            "amount_in": 0.1,
            "expected_out": 180.45,
            "slippage": 0.5
        }
    else:
        # For a real swap, you would use code like this:
        # swap_result = agent.swap_tokens(
        #     address=DEMO_WALLET["address"],
        #     private_key=DEMO_WALLET["private_key"],
        #     token_in="ETH",
        #     token_out="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        #     amount_in=0.1,
        #     slippage=0.5
        # )
        
        # But for safety, we'll just simulate
        swap_result = {
            "transaction_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "status": "simulation",
            "from": DEMO_WALLET["address"],
            "token_in": "ETH",
            "token_out": "USDC",
            "amount_in": 0.1,
            "expected_out": 180.45,
            "slippage": 0.5
        }
    
    logger.info(f"Swap Transaction:")
    logger.info(f"  Status: {swap_result['status']}")
    logger.info(f"  From: {swap_result['from']}")
    logger.info(f"  Swap: {swap_result['amount_in']} {swap_result['token_in']} -> {swap_result['expected_out']} {swap_result['token_out']}")
    if "transaction_hash" in swap_result:
        logger.info(f"  Transaction Hash: {swap_result['transaction_hash']}")
    
    return swap_result

def example_defi_protocol_analysis(society: Web3Society):
    """Example: Analyze a DeFi protocol using a society of agents."""
    logger.info("\n=== Example: DeFi Protocol Analysis ===")
    
    # Analyze Uniswap protocol
    protocol_name = "Uniswap"
    contract_addresses = [
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # UNI token
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"   # Uniswap V2 Router
    ]
    
    logger.info(f"Analyzing {protocol_name} protocol...")
    logger.info(f"This analysis will take some time as it requires multiple agent collaboration.")
    
    # Perform the analysis
    analysis = society.analyze_defi_protocol(protocol_name, contract_addresses)
    
    # Display a summary
    logger.info(f"Analysis completed for {protocol_name}.")
    logger.info(f"Analysis length: {len(analysis['analysis'])} characters")
    
    # Show the first few lines
    summary_lines = analysis["analysis"].split("\n")[:5]
    logger.info("Analysis summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return analysis

def example_create_defi_strategy(society: Web3Society):
    """Example: Create a DeFi investment strategy."""
    logger.info("\n=== Example: Create DeFi Strategy ===")
    
    # Define strategy parameters
    investment_amount = 10000  # $10,000
    risk_profile = "moderate"
    tokens = ["ETH", "USDC", "AAVE", "WBTC"]
    
    logger.info(f"Creating DeFi strategy for ${investment_amount:,} with {risk_profile} risk profile...")
    logger.info(f"Tokens of interest: {', '.join(tokens)}")
    logger.info(f"This will take some time as it requires multiple agent collaboration.")
    
    # Create the strategy
    strategy = society.create_defi_strategy(investment_amount, risk_profile, tokens)
    
    # Display a summary
    logger.info(f"Strategy creation completed.")
    logger.info(f"Strategy length: {len(strategy['strategy'])} characters")
    
    # Show the first few lines
    summary_lines = strategy["strategy"].split("\n")[:5]
    logger.info("Strategy summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return strategy

def example_yield_comparison(agent: Web3Agent):
    """Example: Compare yields across different protocols."""
    logger.info("\n=== Example: Yield Comparison ===")
    
    # For simplicity, we'll create a simulated yield comparison
    tokens = ["ETH", "USDC", "DAI", "WBTC"]
    protocols = ["Aave", "Compound", "Yearn", "Lido"]
    
    # Simulated yields (in a real implementation, this would be fetched from protocols)
    simulated_yields = {
        "ETH": {
            "Aave": 1.25,
            "Compound": 1.05,
            "Yearn": 1.15,
            "Lido": 3.75
        },
        "USDC": {
            "Aave": 2.85,
            "Compound": 2.75,
            "Yearn": 3.12,
            "Lido": None
        },
        "DAI": {
            "Aave": 2.91,
            "Compound": 2.82,
            "Yearn": 3.21,
            "Lido": None
        },
        "WBTC": {
            "Aave": 0.87,
            "Compound": 0.75,
            "Yearn": 1.05,
            "Lido": None
        }
    }
    
    # Display yield comparison
    logger.info("Yield Comparison (APY %):")
    logger.info(f"{'Token':<6} | {'Aave':^10} | {'Compound':^10} | {'Yearn':^10} | {'Lido':^10}")
    logger.info("-" * 62)
    
    for token in tokens:
        yields = simulated_yields[token]
        aave_yield = f"{yields['Aave']:.2f}%" if yields['Aave'] is not None else "N/A"
        compound_yield = f"{yields['Compound']:.2f}%" if yields['Compound'] is not None else "N/A"
        yearn_yield = f"{yields['Yearn']:.2f}%" if yields['Yearn'] is not None else "N/A"
        lido_yield = f"{yields['Lido']:.2f}%" if yields['Lido'] is not None else "N/A"
        
        logger.info(f"{token:<6} | {aave_yield:^10} | {compound_yield:^10} | {yearn_yield:^10} | {lido_yield:^10}")
    
    return simulated_yields

def example_tokenomics_analysis(society: Web3Society):
    """Example: Analyze token economics."""
    logger.info("\n=== Example: Tokenomics Analysis ===")
    
    # UNI token address
    token_address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    
    logger.info(f"Analyzing tokenomics for UNI token ({token_address})...")
    logger.info(f"This analysis will take some time as it requires multiple agent collaboration.")
    
    # Perform the analysis
    analysis = society.analyze_token_economics(token_address)
    
    # Display a summary
    logger.info(f"Analysis completed for token.")
    logger.info(f"Analysis length: {len(analysis['analysis'])} characters")
    
    # Show the first few lines
    summary_lines = analysis["analysis"].split("\n")[:5]
    logger.info("Analysis summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return analysis

# =========================
# Main Function
# =========================

def main():
    """Run all examples."""
    try:
        # Initialize Web3 agent and society
        agent = Web3Agent(CONFIG)
        society = Web3Society(CONFIG)
        
        # Run basic DeFi examples with agent
        example_token_swap_quote(agent)
        example_get_liquidity_pool_info(agent)
        example_aave_user_data(agent)
        example_token_swap_transaction(agent)
        example_yield_comparison(agent)
        
        # Run advanced DeFi examples with society
        # These examples use multiple agents and take longer
        if "--advanced" in sys.argv:
            example_defi_protocol_analysis(society)
            example_create_defi_strategy(society)
            example_tokenomics_analysis(society)
        else:
            logger.info("\nSkipping advanced examples. Run with --advanced to include them.")
        
        logger.info("\nAll examples completed successfully!")
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
