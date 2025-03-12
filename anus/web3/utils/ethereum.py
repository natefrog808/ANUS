"""
Ethereum Utility Functions for Anus AI Web3 Module

This module provides Ethereum-specific utility functions for working with
addresses, transactions, ABIs, smart contracts, and more.
"""

import re
import time
import json
import secrets
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from decimal import Decimal
import binascii
import hashlib

from anus.utils.logging import get_logger

# Setup logging
logger = get_logger("anus.web3.utils.ethereum")

# =========================
# Common Ethereum ABIs
# =========================

# ERC-20 Token Standard ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "spender", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    }
]

# ERC-721 Non-Fungible Token Standard ABI
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"},
            {"name": "data", "type": "bytes"}
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "approved", "type": "bool"}
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "operator", "type": "address"}
        ],
        "name": "isApprovedForAll",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "getApproved",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": True, "name": "tokenId", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "approved", "type": "address"},
            {"indexed": True, "name": "tokenId", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "operator", "type": "address"},
            {"indexed": False, "name": "approved", "type": "bool"}
        ],
        "name": "ApprovalForAll",
        "type": "event"
    }
]

# ERC-1155 Multi Token Standard ABI
ERC1155_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "id", "type": "uint256"}
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "accounts", "type": "address[]"},
            {"name": "ids", "type": "uint256[]"}
        ],
        "name": "balanceOfBatch",
        "outputs": [{"name": "", "type": "uint256[]"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "id", "type": "uint256"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"}
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "ids", "type": "uint256[]"},
            {"name": "values", "type": "uint256[]"},
            {"name": "data", "type": "bytes"}
        ],
        "name": "safeBatchTransferFrom",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "operator", "type": "address"},
            {"name": "approved", "type": "bool"}
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "operator", "type": "address"}
        ],
        "name": "isApprovedForAll",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "id", "type": "uint256"}],
        "name": "uri",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "operator", "type": "address"},
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "id", "type": "uint256"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "TransferSingle",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "operator", "type": "address"},
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "ids", "type": "uint256[]"},
            {"indexed": False, "name": "values", "type": "uint256[]"}
        ],
        "name": "TransferBatch",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "account", "type": "address"},
            {"indexed": True, "name": "operator", "type": "address"},
            {"indexed": False, "name": "approved", "type": "bool"}
        ],
        "name": "ApprovalForAll",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "value", "type": "string"},
            {"indexed": True, "name": "id", "type": "uint256"}
        ],
        "name": "URI",
        "type": "event"
    }
]

# =========================
# Address Utilities
# =========================

def is_eth_address(address: str) -> bool:
    """Check if a string is a valid Ethereum address.
    
    Args:
        address: The address to check
        
    Returns:
        True if the address is valid, False otherwise
    """
    if not address:
        return False
        
    # Basic format check (0x followed by 40 hex characters)
    if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
        return False
    
    # Optionally, validate checksum if it's a mixed-case address
    if re.match(r'^0x[0-9a-fA-F]*[a-fA-F][0-9a-fA-F]*[A-F][0-9a-fA-F]*$', address):
        # Has mixed case, so should be checksummed
        return address == checksum_address(address.lower())
    
    return True

def normalize_eth_address(address: str) -> Optional[str]:
    """Normalize an Ethereum address to lowercase.
    
    Args:
        address: The address to normalize
        
    Returns:
        Normalized address or None if invalid
    """
    if not address:
        return None
        
    # Strip whitespace and lowercase
    address = address.strip().lower()
    
    # Add 0x prefix if missing
    if not address.startswith('0x'):
        address = '0x' + address
    
    # Validate format
    if not re.match(r'^0x[0-9a-f]{40}$', address):
        return None
    
    return address

def checksum_address(address: str) -> str:
    """Convert an Ethereum address to checksum format (EIP-55).
    
    Args:
        address: The address to convert
        
    Returns:
        Checksummed address
    """
    # Normalize address
    address = normalize_eth_address(address)
    if not address:
        raise ValueError("Invalid Ethereum address")
    
    # Remove 0x prefix for hashing
    address = address[2:].lower()
    address_hash = hashlib.sha3_256(address.encode()).hexdigest()
    
    # Apply checksum rules
    checksum_address = '0x'
    for i, char in enumerate(address):
        if char in '0123456789':
            checksum_address += char
        else:
            # Convert to uppercase if corresponding hash character is 8 or higher
            if int(address_hash[i], 16) >= 8:
                checksum_address += char.upper()
            else:
                checksum_address += char
    
    return checksum_address

def generate_eth_address() -> Tuple[str, str]:
    """Generate a random Ethereum address and private key.
    
    Returns:
        Tuple of (address, private_key)
    """
    try:
        # Import necessary libraries
        from eth_account import Account
        from eth_keys import keys
        import secrets
        
        # Generate random private key
        private_key = "0x" + secrets.token_hex(32)
        
        # Create dictionary of named parameters
        result = {
            "function": function_abi['name'],
            "params": dict(zip(param_names, decoded))
        }
        
        return result
    except Exception as e:
        logger.error(f"Failed to decode transaction input: {str(e)}")
        return {
            "error": f"Decoding error: {str(e)}",
            "raw_data": input_data
        }

# =========================
# ABI Utilities
# =========================

def get_function_signature(function_name: str, param_types: List[str]) -> str:
    """Get function signature.
    
    Args:
        function_name: Name of the function
        param_types: List of parameter types
        
    Returns:
        Function signature
    """
    return f"{function_name}({','.join(param_types)})"

def get_event_signature(event_name: str, param_types: List[str]) -> str:
    """Get event signature.
    
    Args:
        event_name: Name of the event
        param_types: List of parameter types
        
    Returns:
        Event signature
    """
    return f"{event_name}({','.join(param_types)})"

def parse_event_logs(web3, contract_abi: List[Dict[str, Any]], logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse event logs.
    
    Args:
        web3: Web3 instance
        contract_abi: Contract ABI
        logs: List of event logs
        
    Returns:
        Parsed event logs
    """
    try:
        # Create contract instance with provided ABI
        contract = web3.eth.contract(abi=contract_abi)
        
        # Parse each log
        parsed_logs = []
        for log in logs:
            try:
                # Find matching event in ABI and parse
                parsed_event = contract.events._get_event_abi_by_topic(log['topics'][0])
                parsed_log = contract.events[parsed_event['name']]().process_log(log)
                parsed_logs.append(parsed_log)
            except Exception as e:
                logger.debug(f"Failed to parse log: {str(e)}")
                parsed_logs.append({
                    "error": f"Parse error: {str(e)}",
                    "raw_log": log
                })
        
        return parsed_logs
    except Exception as e:
        logger.error(f"Failed to parse event logs: {str(e)}")
        return logs

# =========================
# Conversion Utilities
# =========================

def wei_to_eth(wei_amount: Union[int, str]) -> float:
    """Convert wei to ETH.
    
    Args:
        wei_amount: Amount in wei
        
    Returns:
        Amount in ETH
    """
    # Convert to int if string
    if isinstance(wei_amount, str):
        wei_amount = int(wei_amount)
    
    # Convert wei to ETH (1 ETH = 10^18 wei)
    return wei_amount / 1e18

def eth_to_wei(eth_amount: Union[float, str]) -> int:
    """Convert ETH to wei.
    
    Args:
        eth_amount: Amount in ETH
        
    Returns:
        Amount in wei
    """
    # Convert to float if string
    if isinstance(eth_amount, str):
        eth_amount = float(eth_amount)
    
    # Convert ETH to wei (1 ETH = 10^18 wei)
    return int(eth_amount * 1e18)

def eth_unit_convert(amount: Union[int, float, str], from_unit: str, to_unit: str) -> Union[int, float]:
    """Convert between Ethereum units.
    
    Args:
        amount: Amount to convert
        from_unit: Source unit (wei, gwei, eth, etc.)
        to_unit: Target unit (wei, gwei, eth, etc.)
        
    Returns:
        Converted amount
    """
    # Define unit multipliers (relative to wei)
    units = {
        'wei': 1,
        'kwei': 1e3,
        'mwei': 1e6,
        'gwei': 1e9,
        'microether': 1e12,
        'milliether': 1e15,
        'ether': 1e18,
        'eth': 1e18,
    }
    
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Check if units are valid
    if from_unit not in units:
        raise ValueError(f"Invalid from_unit: {from_unit}")
    if to_unit not in units:
        raise ValueError(f"Invalid to_unit: {to_unit}")
    
    # Convert to float if string
    if isinstance(amount, str):
        amount = float(amount)
    
    # Convert to wei
    wei_amount = amount * units[from_unit]
    
    # Convert from wei to target unit
    result = wei_amount / units[to_unit]
    
    # Return int if result is integer
    if result.is_integer():
        return int(result)
    return result

# =========================
# ENS Utilities
# =========================

def is_ens_name(name: str) -> bool:
    """Check if a string is a valid ENS name.
    
    Args:
        name: The name to check
        
    Returns:
        True if the name is a valid ENS name, False otherwise
    """
    # Basic format check
    if not name or not isinstance(name, str):
        return False
    
    # Must end with .eth or another ENS TLD
    ens_tlds = ['.eth', '.xyz', '.app', '.luxe', '.kred', '.art', '.crypto']
    
    if not any(name.lower().endswith(tld) for tld in ens_tlds):
        return False
    
    # ENS names must be at least 3 characters (not including TLD)
    for tld in ens_tlds:
        if name.lower().endswith(tld) and len(name) <= len(tld) + 2:
            return False
    
    # Characters should be alphanumeric, hyphens, or underscores
    name_without_tld = name.rsplit('.', 1)[0]
    if not re.match(r'^[a-zA-Z0-9_-]+ account
        account = Account.from_key(private_key)
        address = account.address
        
        return (address, private_key)
    except ImportError:
        logger.warning("eth_account package not available, using mock implementation")
        
        # Mock implementation if eth_account not available
        private_key = "0x" + secrets.token_hex(32)
        mock_address = "0x" + secrets.token_hex(20)
        
        return (checksum_address(mock_address), private_key)

# =========================
# Transaction Utilities
# =========================

def estimate_gas(web3, tx_params: Dict[str, Any]) -> int:
    """Estimate gas for a transaction.
    
    Args:
        web3: Web3 instance
        tx_params: Transaction parameters
        
    Returns:
        Estimated gas amount
    """
    try:
        # Clone parameters to avoid modifying the original
        params = tx_params.copy()
        
        # Ensure addresses are checksummed
        if 'from' in params:
            params['from'] = web3.to_checksum_address(params['from'])
        if 'to' in params:
            params['to'] = web3.to_checksum_address(params['to'])
        
        # Estimate gas
        gas_estimate = web3.eth.estimate_gas(params)
        
        # Add buffer (10%)
        gas_with_buffer = int(gas_estimate * 1.1)
        
        logger.debug(f"Gas estimate: {gas_estimate}, with buffer: {gas_with_buffer}")
        return gas_with_buffer
    except Exception as e:
        logger.error(f"Gas estimation failed: {str(e)}")
        raise

def wait_for_transaction_receipt(
    web3, 
    tx_hash: str, 
    timeout: int = 120, 
    poll_interval: float = 0.5
) -> Dict[str, Any]:
    """Wait for a transaction receipt.
    
    Args:
        web3: Web3 instance
        tx_hash: Transaction hash
        timeout: Maximum time to wait (in seconds)
        poll_interval: Time between polls (in seconds)
        
    Returns:
        Transaction receipt
    """
    if not isinstance(tx_hash, str):
        tx_hash = tx_hash.hex()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception as e:
            logger.debug(f"Error getting receipt: {str(e)}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Transaction not mined within {timeout} seconds: {tx_hash}")

def decode_transaction_input(web3, contract_abi: List[Dict[str, Any]], input_data: str) -> Dict[str, Any]:
    """Decode transaction input data.
    
    Args:
        web3: Web3 instance
        contract_abi: Contract ABI
        input_data: Transaction input data
        
    Returns:
        Decoded input data
    """
    try:
        from eth_abi import decode_abi
        from eth_utils import function_abi_to_4byte_selector
        
        # Find the function selector (first 4 bytes after 0x)
        function_selector = input_data[:10]
        
        # Find matching function in ABI
        function_abi = None
        for item in contract_abi:
            if item['type'] == 'function':
                selector = '0x' + function_abi_to_4byte_selector(item).hex()
                if selector == function_selector:
                    function_abi = item
                    break
        
        if not function_abi:
            return {
                "error": "Unknown function selector",
                "selector": function_selector
            }
        
        # Decode parameters
        param_types = [input['type'] for input in function_abi['inputs']]
        param_names = [input['name'] for input in function_abi['inputs']]
        
        # Remove function selector from data and convert to bytes
        data_bytes = binascii.unhexlify(input_data[10:])
        
        # Decode parameters
        decoded = decode_abi(param_types, data_bytes)
        
        # Create, name_without_tld):
        return False
    
    return True

def get_ens_resolver(web3, ens_name: str) -> Optional[str]:
    """Get the resolver address for an ENS name.
    
    Args:
        web3: Web3 instance
        ens_name: ENS name
        
    Returns:
        Resolver address or None if not found
    """
    try:
        # Get resolver contract address
        resolver = web3.ens.resolver(ens_name)
        
        # Return address if valid
        return resolver.address if resolver else None
    except Exception as e:
        logger.error(f"Failed to get ENS resolver: {str(e)}")
        return None

def get_ens_text_record(web3, ens_name: str, key: str) -> Optional[str]:
    """Get a text record for an ENS name.
    
    Args:
        web3: Web3 instance
        ens_name: ENS name
        key: Text record key
        
    Returns:
        Text record value or None if not found
    """
    try:
        # Get text record
        return web3.ens.get_text(ens_name, key)
    except Exception as e:
        logger.error(f"Failed to get ENS text record: {str(e)}")
        return None

def get_ens_content_hash(web3, ens_name: str) -> Optional[str]:
    """Get content hash for an ENS name.
    
    Args:
        web3: Web3 instance
        ens_name: ENS name
        
    Returns:
        Content hash or None if not found
    """
    try:
        resolver = web3.ens.resolver(ens_name)
        if not resolver:
            return None
        
        # Content hash selector
        content_hash_selector = '0xbc1c58d1'
        
        # Call resolver
        result = web3.eth.call({
            'to': resolver.address,
            'data': content_hash_selector + web3.ens.namehash(ens_name).hex()[2:].zfill(64)
        })
        
        # Decode result
        if result == '0x' or result == '0x0':
            return None
        
        # TODO: Implement proper content hash decoding
        return result.hex()
    except Exception as e:
        logger.error(f"Failed to get ENS content hash: {str(e)}")
        return None

# =========================
# Gas Price Utilities
# =========================

def get_recommended_gas_prices(web3) -> Dict[str, int]:
    """Get recommended gas prices.
    
    Args:
        web3: Web3 instance
        
    Returns:
        Dictionary with recommended gas prices (slow, standard, fast)
    """
    try:
        # Get current gas price
        base_fee = web3.eth.get_block('latest').baseFeePerGas
        
        # Calculate recommendations
        return {
            'slow': int(base_fee * 1.0),          # Base fee
            'standard': int(base_fee * 1.1) + 1,  # Base fee + 10%
            'fast': int(base_fee * 1.2) + 2,      # Base fee + 20%
            'rapid': int(base_fee * 1.5) + 3      # Base fee + 50%
        }
    except Exception as e:
        # Fallback to legacy gas price
        try:
            gas_price = web3.eth.gas_price
            return {
                'slow': int(gas_price * 0.9),
                'standard': gas_price,
                'fast': int(gas_price * 1.2),
                'rapid': int(gas_price * 1.5)
            }
        except Exception as e2:
            logger.error(f"Failed to get gas prices: {str(e2)}")
            return {
                'slow': 20000000000,    # 20 Gwei
                'standard': 30000000000, # 30 Gwei
                'fast': 50000000000,    # 50 Gwei
                'rapid': 80000000000    # 80 Gwei
            }

def format_gas_prices(gas_prices: Dict[str, int]) -> Dict[str, Union[int, float]]:
    """Format gas prices into human-readable format.
    
    Args:
        gas_prices: Dictionary with gas prices in wei
        
    Returns:
        Dictionary with gas prices in Gwei
    """
    return {
        key: float(value) / 1e9 for key, value in gas_prices.items()
    }

def estimate_transaction_cost(web3, gas_limit: int, gas_price: int) -> float:
    """Estimate transaction cost in ETH.
    
    Args:
        web3: Web3 instance
        gas_limit: Gas limit
        gas_price: Gas price in wei
        
    Returns:
        Estimated cost in ETH
    """
    # Calculate cost in wei
    cost_wei = gas_limit * gas_price
    
    # Convert to ETH
    return wei_to_eth(cost_wei)

# =========================
# Contract Utilities
# =========================

def is_contract_address(web3, address: str) -> bool:
    """Check if an address is a contract.
    
    Args:
        web3: Web3 instance
        address: Address to check
        
    Returns:
        True if the address is a contract, False otherwise
    """
    try:
        # Ensure address is checksummed
        address = web3.to_checksum_address(address)
        
        # Get code at address
        code = web3.eth.get_code(address)
        
        # Address is a contract if code length > 0
        return len(code) > 0
    except Exception as e:
        logger.error(f"Failed to check if address is contract: {str(e)}")
        return False

def get_contract_creator(web3, contract_address: str) -> Optional[str]:
    """Get the creator of a contract.
    
    Args:
        web3: Web3 instance
        contract_address: Contract address
        
    Returns:
        Creator address or None if not found
    """
    try:
        # Ensure address is checksummed
        contract_address = web3.to_checksum_address(contract_address)
        
        # Get transaction hash of contract creation
        # This requires tracing or an archive node
        creation_tx_hash = None
        
        # Try to get transaction hash from transaction receipt
        receipt = web3.eth.get_transaction_receipt(creation_tx_hash)
        if receipt and receipt.get('contractAddress') == contract_address:
            # Get transaction
            tx = web3.eth.get_transaction(receipt['transactionHash'])
            return tx['from']
        
        # Fallback: return None if not found
        return None
    except Exception as e:
        logger.error(f"Failed to get contract creator: {str(e)}")
        return None

def get_contract_creation_block(web3, contract_address: str) -> Optional[int]:
    """Get the block number when a contract was created.
    
    Args:
        web3: Web3 instance
        contract_address: Contract address
        
    Returns:
        Block number or None if not found
    """
    try:
        # Get creation transaction hash (implementation depends on node)
        # This is a placeholder and might require a specific API or archive node
        creation_tx_hash = None
        
        if creation_tx_hash:
            # Get transaction receipt
            receipt = web3.eth.get_transaction_receipt(creation_tx_hash)
            return receipt['blockNumber']
        
        return None
    except Exception as e:
        logger.error(f"Failed to get contract creation block: {str(e)}")
        return None account
        account = Account.from_key(private_key)
        address = account.address
        
        return (address, private_key)
    except ImportError:
        logger.warning("eth_account package not available, using mock implementation")
        
        # Mock implementation if eth_account not available
        private_key = "0x" + secrets.token_hex(32)
        mock_address = "0x" + secrets.token_hex(20)
        
        return (checksum_address(mock_address), private_key)

# =========================
# Transaction Utilities
# =========================

def estimate_gas(web3, tx_params: Dict[str, Any]) -> int:
    """Estimate gas for a transaction.
    
    Args:
        web3: Web3 instance
        tx_params: Transaction parameters
        
    Returns:
        Estimated gas amount
    """
    try:
        # Clone parameters to avoid modifying the original
        params = tx_params.copy()
        
        # Ensure addresses are checksummed
        if 'from' in params:
            params['from'] = web3.to_checksum_address(params['from'])
        if 'to' in params:
            params['to'] = web3.to_checksum_address(params['to'])
        
        # Estimate gas
        gas_estimate = web3.eth.estimate_gas(params)
        
        # Add buffer (10%)
        gas_with_buffer = int(gas_estimate * 1.1)
        
        logger.debug(f"Gas estimate: {gas_estimate}, with buffer: {gas_with_buffer}")
        return gas_with_buffer
    except Exception as e:
        logger.error(f"Gas estimation failed: {str(e)}")
        raise

def wait_for_transaction_receipt(
    web3, 
    tx_hash: str, 
    timeout: int = 120, 
    poll_interval: float = 0.5
) -> Dict[str, Any]:
    """Wait for a transaction receipt.
    
    Args:
        web3: Web3 instance
        tx_hash: Transaction hash
        timeout: Maximum time to wait (in seconds)
        poll_interval: Time between polls (in seconds)
        
    Returns:
        Transaction receipt
    """
    if not isinstance(tx_hash, str):
        tx_hash = tx_hash.hex()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception as e:
            logger.debug(f"Error getting receipt: {str(e)}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Transaction not mined within {timeout} seconds: {tx_hash}")

def decode_transaction_input(web3, contract_abi: List[Dict[str, Any]], input_data: str) -> Dict[str, Any]:
    """Decode transaction input data.
    
    Args:
        web3: Web3 instance
        contract_abi: Contract ABI
        input_data: Transaction input data
        
    Returns:
        Decoded input data
    """
    try:
        from eth_abi import decode_abi
        from eth_utils import function_abi_to_4byte_selector
        
        # Find the function selector (first 4 bytes after 0x)
        function_selector = input_data[:10]
        
        # Find matching function in ABI
        function_abi = None
        for item in contract_abi:
            if item['type'] == 'function':
                selector = '0x' + function_abi_to_4byte_selector(item).hex()
                if selector == function_selector:
                    function_abi = item
                    break
        
        if not function_abi:
            return {
                "error": "Unknown function selector",
                "selector": function_selector
            }
        
        # Decode parameters
        param_types = [input['type'] for input in function_abi['inputs']]
        param_names = [input['name'] for input in function_abi['inputs']]
        
        # Remove function selector from data and convert to bytes
        data_bytes = binascii.unhexlify(input_data[10:])
        
        # Decode parameters
        decoded = decode_abi(param_types, data_bytes)
        
        # Create
