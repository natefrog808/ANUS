"""
Utility Functions for Anus AI Web3 Module

This package provides utility functions and helpers for working with
blockchain networks, decentralized storage, and other Web3 technologies.
"""

from typing import Dict, Any, List, Optional, Union, Callable, Tuple
import json
import time
import logging
from decimal import Decimal

from anus.utils.logging import get_logger

# Setup logging
logger = get_logger("anus.web3.utils")

# Import utility functions from submodules
from anus.web3.utils.ethereum import (
    # Address utilities
    is_eth_address,
    normalize_eth_address,
    checksum_address,
    generate_eth_address,
    
    # Transaction utilities
    estimate_gas,
    wait_for_transaction_receipt,
    decode_transaction_input,
    
    # ABI utilities
    get_function_signature,
    get_event_signature,
    parse_event_logs,
    
    # Conversion utilities
    wei_to_eth,
    eth_to_wei,
    eth_unit_convert,
    
    # ENS utilities
    is_ens_name,
    get_ens_resolver,
    
    # Common ABIs
    ERC20_ABI,
    ERC721_ABI,
    ERC1155_ABI,
)

from anus.web3.utils.solana import (
    # Address utilities
    is_sol_address,
    normalize_sol_address,
    generate_sol_keypair,
    
    # Transaction utilities
    estimate_sol_fee,
    wait_for_sol_transaction,
    
    # Account utilities
    get_sol_account_info,
    
    # Conversion utilities
    lamports_to_sol,
    sol_to_lamports,
)

from anus.web3.utils.ipfs import (
    # IPFS utilities
    ipfs_uri_to_http,
    is_ipfs_uri,
    normalize_ipfs_uri,
    extract_ipfs_cid,
    
    # Gateway utilities
    get_ipfs_gateway_url,
    get_gateway_list,
    select_fastest_gateway,
)

# Define module exports
__all__ = [
    # Ethereum utilities
    "is_eth_address",
    "normalize_eth_address",
    "checksum_address",
    "generate_eth_address",
    "estimate_gas",
    "wait_for_transaction_receipt",
    "decode_transaction_input",
    "get_function_signature",
    "get_event_signature",
    "parse_event_logs",
    "wei_to_eth",
    "eth_to_wei",
    "eth_unit_convert",
    "is_ens_name",
    "get_ens_resolver",
    "ERC20_ABI",
    "ERC721_ABI",
    "ERC1155_ABI",
    
    # Solana utilities
    "is_sol_address",
    "normalize_sol_address",
    "generate_sol_keypair",
    "estimate_sol_fee",
    "wait_for_sol_transaction",
    "get_sol_account_info",
    "lamports_to_sol",
    "sol_to_lamports",
    
    # IPFS utilities
    "ipfs_uri_to_http",
    "is_ipfs_uri",
    "normalize_ipfs_uri",
    "extract_ipfs_cid",
    "get_ipfs_gateway_url",
    "get_gateway_list",
    "select_fastest_gateway",
]

# Common Web3 utility functions not specific to any blockchain

def retry_web3_operation(
    operation: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions_to_retry: Tuple = (Exception,)
) -> Any:
    """Retry a Web3 operation with exponential backoff.
    
    Args:
        operation: The function to retry
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (in seconds)
        backoff_factor: Factor to increase delay for each retry
        exceptions_to_retry: Tuple of exceptions that should trigger a retry
        
    Returns:
        The result of the operation if successful
        
    Raises:
        The last exception if all retries fail
    """
    last_exception = None
    current_delay = retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except exceptions_to_retry as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Web3 operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}"
                )
                time.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                logger.error(f"Web3 operation failed after {max_retries + 1} attempts: {str(e)}")
    
    raise last_exception

def format_blockchain_error(error: Any) -> Dict[str, Any]:
    """Format blockchain errors in a consistent way.
    
    Args:
        error: The error object
        
    Returns:
        Formatted error dictionary
    """
    # Extract error message
    if hasattr(error, "message"):
        message = error.message
    elif hasattr(error, "args") and len(error.args) > 0:
        message = error.args[0]
    else:
        message = str(error)
    
    # Try to extract error code
    error_code = None
    if hasattr(error, "code"):
        error_code = error.code
    
    # Create error response
    error_response = {
        "error": message
    }
    
    if error_code is not None:
        error_response["error_code"] = error_code
    
    # Add error details if available
    if hasattr(error, "data"):
        error_response["details"] = error.data
    
    return error_response

def safe_json_dumps(obj: Any) -> str:
    """Safely convert an object to JSON string, handling Decimal and other special types.
    
    Args:
        obj: The object to convert
        
    Returns:
        JSON string representation
    """
    def default_serializer(o):
        if isinstance(o, Decimal):
            return str(o)
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    
    return json.dumps(obj, default=default_serializer)

def parse_token_amount(amount: Union[str, int, float], decimals: int) -> int:
    """Parse a human-readable token amount into token units.
    
    Args:
        amount: The amount in human-readable form
        decimals: The token decimals
        
    Returns:
        The amount in token units (wei, lamports, etc.)
    """
    if isinstance(amount, str):
        # Handle scientific notation
        if 'e' in amount.lower():
            amount = float(amount)
        # Handle percentages
        elif amount.endswith('%'):
            amount = float(amount.strip('%')) / 100.0
    
    # Convert to Decimal for precision
    dec_amount = Decimal(str(amount))
    
    # Calculate token units
    return int(dec_amount * (10 ** decimals))

def format_token_amount(amount: Union[str, int], decimals: int, precision: int = 8) -> str:
    """Format token units into a human-readable amount.
    
    Args:
        amount: The amount in token units
        decimals: The token decimals
        precision: The number of decimal places to display
        
    Returns:
        Human-readable token amount
    """
    # Convert to Decimal for precision
    dec_amount = Decimal(str(amount)) / (10 ** decimals)
    
    # Format with appropriate precision
    formatted = f"{dec_amount:.{precision}f}"
    
    # Remove trailing zeros and decimal point if not needed
    formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    
    return formatted
