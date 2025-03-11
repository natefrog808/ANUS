"""
Anus AI Web3 Module - NFT Examples

This script demonstrates NFT-focused functionality of the Anus AI Web3 module,
including fetching NFT metadata, analyzing collections, monitoring sales,
and creating NFT-related strategies.

Usage:
    python nft_examples.py

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
from anus.web3.utils import ipfs_uri_to_http, is_ipfs_uri

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
    "coordination_strategy": "hierarchical",
    "ipfs": {
        "gateway": "https://ipfs.io/ipfs/"
    }
}

# Example wallet for demonstrations
DEMO_WALLET = {
    "address": "0xYourWalletAddress",  # Replace with your wallet
    "private_key": None,  # Never put private keys in code
}

# =========================
# Example Functions
# =========================

def example_nft_metadata(agent: Web3Agent):
    """Example: Get NFT metadata."""
    logger.info("=== Example: NFT Metadata ===")
    
    # CryptoPunk #7804 (example)
    contract_address = "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"
    token_id = 7804
    
    logger.info(f"Getting metadata for CryptoPunk #{token_id}...")
    
    # Get NFT metadata
    metadata = agent.nft_info(contract_address, token_id)
    
    if "error" not in metadata:
        logger.info(f"NFT Owner: {metadata.get('owner')}")
        logger.info(f"Token URI: {metadata.get('token_uri')}")
        
        # Display metadata if available
        if "metadata" in metadata and metadata["metadata"]:
            nft_metadata = metadata["metadata"]
            logger.info("Metadata:")
            for key, value in nft_metadata.items():
                if isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value)[:100] + "..." if len(json.dumps(value)) > 100 else json.dumps(value)
                logger.info(f"  {key}: {value}")
    else:
        logger.error(f"Error getting NFT metadata: {metadata['error']}")
    
    return metadata

def example_nft_owner(agent: Web3Agent):
    """Example: Get NFT owner."""
    logger.info("\n=== Example: NFT Owner ===")
    
    # Bored Ape #8817 (example)
    contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
    token_id = 8817
    
    logger.info(f"Getting owner for Bored Ape #{token_id}...")
    
    # Get NFT owner
    result = agent.nft_owner(contract_address, token_id)
    
    if "error" not in result:
        logger.info(f"NFT Owner: {result['owner']}")
    else:
        logger.error(f"Error getting NFT owner: {result['error']}")
    
    return result

def example_nft_collection_tokens(agent: Web3Agent):
    """Example: Get tokens in an NFT collection owned by an address."""
    logger.info("\n=== Example: NFT Collection Tokens ===")
    
    # CryptoPunks contract
    contract_address = "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"
    
    # Example address with CryptoPunks (can be changed)
    owner_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    
    logger.info(f"Getting CryptoPunks owned by {owner_address}...")
    
    # Get owned tokens
    result = agent.run_tool("nft", {
        "action": "owned_by",
        "address": owner_address,
        "contract_address": contract_address
    })
    
    if "error" not in result:
        logger.info(f"Token Balance: {result.get('token_balance', 0)} NFTs")
        logger.info(f"Note: {result.get('note', '')}")
    else:
        logger.error(f"Error getting owned tokens: {result['error']}")
    
    return result

def example_ipfs_nft_metadata(agent: Web3Agent):
    """Example: Get NFT metadata from IPFS."""
    logger.info("\n=== Example: IPFS NFT Metadata ===")
    
    # Example IPFS URI for an NFT
    ipfs_uri = "ipfs://QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/1"
    
    logger.info(f"Getting metadata from IPFS: {ipfs_uri}")
    
    # Get content from IPFS
    result = agent.get_ipfs_content(ipfs_uri)
    
    if "error" not in result:
        logger.info(f"Content Type: {result.get('content_type')}")
        content = result.get("content")
        
        if isinstance(content, dict):
            logger.info("Metadata:")
            for key, value in content.items():
                if isinstance(value, dict) or isinstance(value, list):
                    value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                logger.info(f"  {key}: {value}")
            
            # Check for image URL
            if "image" in content and is_ipfs_uri(content["image"]):
                image_url = ipfs_uri_to_http(content["image"])
                logger.info(f"Image URL: {image_url}")
        else:
            logger.info(f"Content: {str(content)[:100]}..." if len(str(content)) > 100 else str(content))
    else:
        logger.error(f"Error getting IPFS content: {result['error']}")
    
    return result

def example_nft_transfer(agent: Web3Agent):
    """Example: Transfer an NFT (simulation only)."""
    logger.info("\n=== Example: NFT Transfer (SIMULATION) ===")
    
    # This is a simulation - no real transaction will be executed
    logger.info("This is a simulated example - no real transaction will be executed")
    
    # Example NFT details
    contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"  # BAYC
    token_id = 1234
    
    if not DEMO_WALLET["address"] or DEMO_WALLET["private_key"] == None:
        logger.info("Wallet not configured - using simulation mode")
        
        # Simulate the transfer call
        transfer_result = {
            "transaction_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "status": "simulation",
            "from": "0xYourAddress",
            "to": "0xRecipientAddress",
            "contract_address": contract_address,
            "token_id": token_id
        }
    else:
        # For a real transfer, you would use code like this:
        # transfer_result = agent.transfer_nft(
        #     from_address=DEMO_WALLET["address"],
        #     to_address="0xRecipientAddress",
        #     contract_address=contract_address,
        #     token_id=token_id,
        #     private_key=DEMO_WALLET["private_key"]
        # )
        
        # But for safety, we'll just simulate
        transfer_result = {
            "transaction_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "status": "simulation",
            "from": DEMO_WALLET["address"],
            "to": "0xRecipientAddress",
            "contract_address": contract_address,
            "token_id": token_id
        }
    
    logger.info(f"NFT Transfer:")
    logger.info(f"  Status: {transfer_result['status']}")
    logger.info(f"  From: {transfer_result['from']}")
    logger.info(f"  To: {transfer_result['to']}")
    logger.info(f"  Contract: {transfer_result['contract_address']}")
    logger.info(f"  Token ID: {transfer_result['token_id']}")
    if "transaction_hash" in transfer_result:
        logger.info(f"  Transaction Hash: {transfer_result['transaction_hash']}")
    
    return transfer_result

def example_nft_collection_analysis(society: Web3Society):
    """Example: Analyze an NFT collection using a society of agents."""
    logger.info("\n=== Example: NFT Collection Analysis ===")
    
    # Bored Ape Yacht Club
    collection_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
    
    logger.info(f"Analyzing BAYC collection ({collection_address})...")
    logger.info(f"This analysis will take some time as it requires multiple agent collaboration.")
    
    # Perform the analysis
    analysis = society.monitor_nft_collection(collection_address, period="30d")
    
    # Display a summary
    logger.info(f"Analysis completed for collection.")
    logger.info(f"Analysis length: {len(analysis['analysis'])} characters")
    
    # Show the first few lines
    summary_lines = analysis["analysis"].split("\n")[:5]
    logger.info("Analysis summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return analysis

def example_nft_price_history(agent: Web3Agent):
    """Example: Get NFT price history."""
    logger.info("\n=== Example: NFT Price History ===")
    
    # Since we don't have direct access to price history in this demo,
    # we'll create simulated price history data
    
    # CryptoPunks contract
    contract_address = "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"
    token_id = 7804
    
    logger.info(f"Getting price history for CryptoPunk #{token_id}...")
    
    # Simulate price history (in a real implementation, this would be fetched from an API or indexer)
    simulated_history = [
        {"date": "2021-03-11", "price": 4200.0, "currency": "ETH"},
        {"date": "2020-11-23", "price": 80.0, "currency": "ETH"},
        {"date": "2019-07-15", "price": 12.5, "currency": "ETH"},
        {"date": "2018-05-02", "price": 2.5, "currency": "ETH"},
        {"date": "2017-09-18", "price": 0.25, "currency": "ETH"}
    ]
    
    # Display price history
    logger.info(f"Price History for CryptoPunk #{token_id}:")
    logger.info(f"{'Date':<12} | {'Price':>10} {'Currency':<5}")
    logger.info("-" * 30)
    
    for entry in simulated_history:
        logger.info(f"{entry['date']:<12} | {entry['price']:>10.2f} {entry['currency']:<5}")
    
    # Calculate ROI
    first_price = simulated_history[-1]["price"]
    last_price = simulated_history[0]["price"]
    roi = ((last_price - first_price) / first_price) * 100
    
    logger.info(f"\nROI since first sale: {roi:,.2f}%")
    
    return simulated_history

def example_nft_rarity_analysis(agent: Web3Agent):
    """Example: Analyze NFT rarity."""
    logger.info("\n=== Example: NFT Rarity Analysis ===")
    
    # Since we don't have direct access to trait data in this demo,
    # we'll create simulated rarity data for a CryptoPunk
    
    punk_id = 7804
    logger.info(f"Analyzing rarity for CryptoPunk #{punk_id}...")
    
    # Simulated traits and their rarity
    simulated_traits = {
        "Type": {"value": "Alien", "rarity": 0.09, "count": 9},
        "Accessory 1": {"value": "Cap Forward", "rarity": 2.5, "count": 254},
        "Accessory 2": {"value": "Small Shades", "rarity": 3.7, "count": 378},
        "Accessory 3": {"value": "Pipe", "rarity": 3.2, "count": 317}
    }
    
    # Display trait rarity
    logger.info(f"Trait Rarity for CryptoPunk #{punk_id}:")
    logger.info(f"{'Trait':<12} | {'Value':<15} | {'Rarity %':>10} | {'Count':>8}")
    logger.info("-" * 55)
    
    for trait, data in simulated_traits.items():
        logger.info(f"{trait:<12} | {data['value']:<15} | {data['rarity']:>10.2f}% | {data['count']:>8}")
    
    # Calculate overall rarity score
    # A simple multiplicative model for demonstration
    rarity_score = 1
    for trait, data in simulated_traits.items():
        rarity_score *= (100 / data["rarity"])
    
    # Log rarity score
    logger.info(f"\nOverall Rarity Score: {rarity_score:,.2f}")
    logger.info(f"Rarity Rank: 13 / 10000 (simulated)")
    
    return {
        "punk_id": punk_id,
        "traits": simulated_traits,
        "rarity_score": rarity_score,
        "rank": 13
    }

def example_nft_recommendations(society: Web3Society):
    """Example: Get NFT investment recommendations."""
    logger.info("\n=== Example: NFT Investment Recommendations ===")
    
    # Simulate a query to the society
    query = """
    Given current market conditions, what are the top 5 NFT collections 
    to consider for long-term investment? Consider factors like team, 
    utility, community strength, and market performance.
    """
    
    logger.info("Generating NFT investment recommendations...")
    logger.info("This analysis will take some time as it requires multiple agent collaboration.")
    
    # Simulate the response (in a real implementation, this would call society.run())
    simulated_response = """
    # Top 5 NFT Collections for Long-Term Investment
    
    Based on current market conditions as of March 2025, here are the top 5 NFT collections that show promise for long-term investment:
    
    ## 1. Bored Ape Yacht Club (BAYC)
    
    **Strengths:**
    - Established brand with strong IP commercialization
    - Ongoing utility through Yuga Labs ecosystem
    - Consistent floor price resilience during market downturns
    - Active community and continued development
    
    ## 2. Art Blocks Curated
    
    **Strengths:**
    - Focus on high-quality generative art with lasting artistic significance
    - Selective curation process ensures quality
    - Strong performance among art collectors and institutions
    - Multiple successful artists have emerged from the platform
    
    ## 3. Azuki
    
    **Strengths:**
    - Innovative "Physical Backed Token" (PBT) technology
    - Strong anime-inspired aesthetic with global appeal
    - Detailed roadmap with physical/digital crossover products
    - Experienced team with background in gaming and technology
    
    ## 4. Createra Legacy
    
    **Strengths:**
    - Pioneering AI-collaborative art with renowned artists
    - Utility focused on creative tooling and education
    - Strong partnerships with traditional art galleries
    - Sustainable royalty model benefiting both collectors and creators
    
    ## 5. Checks
    
    **Strengths:**
    - Simple but iconic on-chain art with cultural significance
    - Strong community governance and transparent development
    - Multiple successful derivative projects
    - Built-in deflationary mechanics with token burn events
    
    **Investment Considerations:**
    
    - Diversify across different NFT categories (PFPs, art, gaming)
    - Focus on collections with ongoing utility and development
    - Consider floor prices relative to all-time highs for entry points
    - Look for projects with sustainable royalty models and treasury management
    """
    
    # Display a summary
    logger.info("Recommendations generated.")
    
    # Show the first few lines
    summary_lines = simulated_response.split("\n")[:6]
    logger.info("Recommendations summary (first few lines):")
    for line in summary_lines:
        logger.info(f"  {line}")
    
    return {
        "query": query,
        "recommendations": simulated_response
    }

# =========================
# Main Function
# =========================

def main():
    """Run all examples."""
    try:
        # Initialize Web3 agent and society
        agent = Web3Agent(CONFIG)
        society = Web3Society(CONFIG)
        
        # Run basic NFT examples with agent
        example_nft_metadata(agent)
        example_nft_owner(agent)
        example_nft_collection_tokens(agent)
        example_ipfs_nft_metadata(agent)
        example_nft_transfer(agent)
        example_nft_price_history(agent)
        example_nft_rarity_analysis(agent)
        
        # Run advanced NFT examples with society
        # These examples use multiple agents and take longer
        if "--advanced" in sys.argv:
            example_nft_collection_analysis(society)
            example_nft_recommendations(society)
        else:
            logger.info("\nSkipping advanced examples. Run with --advanced to include them.")
        
        logger.info("\nAll examples completed successfully!")
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
