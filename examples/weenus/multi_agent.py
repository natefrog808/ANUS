"""
Anus AI Web3 Module - Multi-Agent Examples

This script demonstrates the multi-agent capabilities of the Anus AI Web3 module
using Web3Society, which combines specialized agents for complex Web3 tasks.

Usage:
    python multi_agent.py

Note: You need appropriate API keys for blockchain providers in your configuration.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Add the parent directory to the path to allow running this script directly
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(parent_dir)

# Import Anus AI components
from anus.web3 import Web3Agent, Web3Society
from anus.agents import Agent

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
    "memory_path": "./web3_society_memory",
    "coordination_strategy": "hierarchical"
}

# =========================
# Example Functions
# =========================

def example_society_overview():
    """Example: Overview of Web3Society and its agents."""
    logger.info("=== Example: Web3Society Overview ===")
    
    # Initialize Web3Society
    society = Web3Society(CONFIG)
    
    # Display society information
    logger.info(f"Web3Society initialized with {len(society.agents)} agents:")
    
    for i, agent in enumerate(society.agents, 1):
        logger.info(f"  Agent {i}: {agent.role}")
        logger.info(f"    Description: {agent.description[:100]}..." if len(agent.description) > 100 else f"    Description: {agent.description}")
        
        # List agent tools
        tool_names = [tool.name for tool in agent.tools] if hasattr(agent, "tools") else []
        logger.info(f"    Tools: {', '.join(tool_names)}")
        
        logger.info("")
    
    # Display coordination strategy
    logger.info(f"Coordination Strategy: {society.coordination_strategy}")
    if society.leader_agent_id:
        leader_agent = next((a for a in society.agents if a.id == society.leader_agent_id), None)
        logger.info(f"Leader Agent: {leader_agent.role if leader_agent else 'Unknown'}")
    
    return society

def example_wallet_analysis(society: Web3Society):
    """Example: Analyze a wallet using the society."""
    logger.info("\n=== Example: Comprehensive Wallet Analysis ===")
    
    # Vitalik's address (example)
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    logger.info(f"Performing comprehensive analysis of wallet {address}...")
    logger.info(f"This analysis will take some time as it requires multiple agent collaboration.")
    
    # Perform the analysis
    start_time = time.time()
    analysis = society.analyze_wallet(address)
    elapsed_time = time.time() - start_time
    
    # Display a summary
    logger.info(f"Analysis completed in {elapsed_time:.2f} seconds.")
    logger.info(f"Analysis length: {len(analysis['analysis'])} characters")
    
    # Show the first few lines
    summary_lines = analysis["analysis"].split("\n")[:5]
    logger.info("Analysis summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return analysis

def example_smart_contract_assessment(society: Web3Society):
    """Example: Assess a smart contract using the society."""
    logger.info("\n=== Example: Smart Contract Assessment ===")
    
    # Uniswap V2 Router contract address
    contract_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    
    logger.info(f"Assessing smart contract at {contract_address}...")
    logger.info(f"This assessment will take some time as it requires multiple agent collaboration.")
    
    # Perform the assessment
    start_time = time.time()
    assessment = society.assess_smart_contract(contract_address)
    elapsed_time = time.time() - start_time
    
    # Display a summary
    logger.info(f"Assessment completed in {elapsed_time:.2f} seconds.")
    logger.info(f"Assessment length: {len(assessment['assessment'])} characters")
    
    # Show the first few lines
    summary_lines = assessment["assessment"].split("\n")[:5]
    logger.info("Assessment summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return assessment

def example_draft_smart_contract(society: Web3Society):
    """Example: Draft a smart contract using the society."""
    logger.info("\n=== Example: Draft Smart Contract ===")
    
    # Contract requirements
    contract_type = "ERC721 NFT Collection"
    requirements = """
    Create a smart contract for an NFT collection with the following requirements:
    
    1. Maximum supply of 10,000 NFTs
    2. Reserved 100 NFTs for team allocation
    3. Whitelist presale mechanism
    4. Public sale with max 5 NFTs per wallet
    5. Reveal mechanism with baseURI update
    6. 5% royalty on secondary sales
    7. Withdrawal function for contract owner
    8. Optional: Staking mechanism for token holders
    """
    
    logger.info(f"Drafting a {contract_type} smart contract...")
    logger.info(f"This will take some time as it requires multiple agent collaboration.")
    
    # Perform the drafting
    start_time = time.time()
    draft = society.draft_smart_contract(requirements, contract_type)
    elapsed_time = time.time() - start_time
    
    # Display a summary
    logger.info(f"Contract draft completed in {elapsed_time:.2f} seconds.")
    logger.info(f"Draft length: {len(draft['draft'])} characters")
    
    # Show the first few lines
    summary_lines = draft["draft"].split("\n")[:5]
    logger.info("Draft summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return draft

def example_cross_chain_analysis(society: Web3Society):
    """Example: Cross-chain asset analysis."""
    logger.info("\n=== Example: Cross-Chain Asset Analysis ===")
    
    # Example wallet with cross-chain assets
    # Using Vitalik's address for example purposes
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    # List of networks to check
    networks = ["ethereum", "polygon", "arbitrum"]
    
    # Simulated cross-chain analysis - in a full implementation, 
    # this would query multiple networks and aggregate the data
    
    logger.info(f"Analyzing cross-chain assets for {address}...")
    logger.info(f"Networks: {', '.join(networks)}")
    
    # Get basic wallet info from society's web3_agent
    wallet_status = society.web3_agent.wallet_status(address, networks=["ethereum"])
    
    # Simulate full society analysis with aggregated data
    simulated_analysis = f"""
    # Cross-Chain Asset Analysis for {address}
    
    ## Overview
    
    This wallet maintains significant positions across multiple networks, with Ethereum serving as its primary blockchain for value storage and NFT holdings. The wallet shows strategic diversification and an active presence in DeFi protocols on Layer 2 solutions.
    
    ## Network Breakdown
    
    ### Ethereum Mainnet
    - Main holdings: ETH, USDC, several ERC-20 governance tokens
    - Total Value: Approximately $281.5M USD
    - Key positions: Large ETH holdings, Maker DAO governance tokens
    - Notable NFTs: Several CryptoPunks, Art Blocks pieces
    
    ### Polygon Network
    - Main holdings: MATIC, USDC, wETH
    - Total Value: Approximately $3.2M USD
    - Key activities: Liquidity provision on QuickSwap, some gaming NFTs
    
    ### Arbitrum
    - Main holdings: ETH, ARB, GMX
    - Total Value: Approximately $4.6M USD
    - Key activities: Yield farming on GMX, trading on Camelot
    
    ## Asset Allocation
    - 85.7% on Ethereum Mainnet
    - 9.8% on Arbitrum
    - 4.5% on Polygon
    
    ## Transaction Patterns
    The wallet demonstrates strategic usage of each network:
    - Ethereum: Long-term holdings and high-value transactions
    - Polygon: Gaming and lower-value DeFi interactions
    - Arbitrum: Active trading and yield optimization
    
    ## Recommendations
    1. Consider further diversifying into Optimism ecosystem given the growth patterns
    2. The Polygon position could benefit from exploring Polygon zkEVM opportunities
    3. Monitor gas costs on Ethereum transactions - some optimization possible
    """
    
    # Display a summary
    logger.info("Cross-chain analysis completed.")
    
    # Show the first few lines
    summary_lines = simulated_analysis.split("\n")[:6]
    logger.info("Analysis summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return {
        "address": address,
        "networks": networks,
        "basic_info": wallet_status,
        "analysis": simulated_analysis
    }

def example_interactive_collaboration(society: Web3Society):
    """Example: Interactive collaboration between agents."""
    logger.info("\n=== Example: Interactive Agent Collaboration ===")
    
    # This example demonstrates how multiple agents in the society
    # collaborate to solve a complex problem
    
    # Example task requiring multiple agent expertise
    task = """
    Create a strategy for launching a new DeFi protocol with the following aspects:
    
    1. Token economics with proper incentive mechanisms
    2. Smart contract architecture focused on security and upgradability
    3. Initial liquidity strategy with minimal impermanent loss risk
    4. Governance mechanism with quadratic voting
    5. Marketing approach for reaching both retail and institutional users
    """
    
    logger.info("Demonstrating agent collaboration process...")
    logger.info("Task: Create a DeFi protocol launch strategy")
    
    # In a real implementation, we would call society.run(task)
    # But for this demo, we'll simulate the interaction between agents
    
    # Simulate research agent gathering information
    logger.info("\nResearch Agent: Gathering information about current DeFi landscape...")
    time.sleep(1)
    research_output = "Research completed on recent successful DeFi protocols and their launch strategies."
    
    # Simulate smart contract expert designing architecture
    logger.info("\nSmart Contract Expert: Designing secure contract architecture...")
    time.sleep(1)
    contract_output = "Proposed modular contract system with time-locks, proxy patterns, and formal verification."
    
    # Simulate DeFi specialist creating tokenomics
    logger.info("\nDeFi Specialist: Creating tokenomics model...")
    time.sleep(1)
    defi_output = "Designed token distribution with initial boosted rewards and long-term emission curve."
    
    # Simulate blockchain analyst running simulations
    logger.info("\nBlockchain Analyst: Running economic simulations...")
    time.sleep(1)
    analyst_output = "Simulations suggest 25% initial liquidity with 4-year vesting for team tokens."
    
    # Simulate core web3 agent coordinating and finalizing
    logger.info("\nWeb3 Agent: Coordinating inputs and finalizing strategy...")
    time.sleep(1)
    
    # Simulated final output
    simulated_response = """
    # DeFi Protocol Launch Strategy
    
    ## Overview
    Based on the collaborative analysis of market conditions and successful precedents, we recommend a phased launch strategy that prioritizes security, sustainable tokenomics, and community building.
    
    ## Token Economics
    - **Token Distribution**: 
      - 15% Team (4-year vesting with 1-year cliff)
      - 25% Strategic Partners (2-year vesting)
      - 20% Community Treasury (governed by DAO)
      - 10% Initial Liquidity
      - 30% Emissions Rewards (10-year schedule)
    
    - **Incentive Mechanism**: 
      - Boosted rewards for early users with decline by 15% quarterly
      - Staking with vote-escrowed mechanism for governance weight
      - Protocol fee sharing for long-term stakers
    
    ## Smart Contract Architecture
    - Modular system with isolated components
    - Timelock controller for all admin functions (72-hour delay)
    - Upgradeable proxy pattern with transparent admin
    - Emergency pause functionality with multi-sig control
    - Comprehensive formal verification before launch
    
    ## Initial Liquidity Strategy
    - Launch on Ethereum with 80% of initial liquidity
    - Cross-chain deployment to Arbitrum with 20% of initial liquidity
    - Concentrated liquidity positions to minimize impermanent loss
    - Liquidity mining program with 2-week epochs and adjustable rewards
    
    ## Governance System
    - Quadratic voting based on token
