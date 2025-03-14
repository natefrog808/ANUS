"""
Solana Utility Functions for Anus AI Web3 Module

This module provides Solana-specific utility functions for working with
addresses, transactions, accounts, and more.
"""

import re
import time
import base58
import base64
import json
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from decimal import Decimal

from anus.utils.logging import get_logger

# Setup logging
logger = get_logger("anus.web3.utils.solana")

# =========================
# Address Utilities
# =========================

def is_sol_address(address: str) -> bool:
    """Check if a string is a valid Solana address.
    
    Args:
        address: The address to check
        
    Returns:
        True if the address is valid, False otherwise
    """
    if not address:
        return False
    
    # Solana addresses are base58 encoded and 32-44 characters long
    if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address):
        return False
    
    # Try to decode it
    try:
        decoded = base58.b58decode(address)
        return len(decoded) == 32  # Solana addresses are 32 bytes
    except Exception:
        return False

def normalize_sol_address(address: str) -> Optional[str]:
    """Normalize a Solana address.
    
    Args:
        address: The address to normalize
        
    Returns:
        Normalized address or None if invalid
    """
    if not address:
        return None
    
    # Strip whitespace
    address = address.strip()
    
    # Validate format
    if not is_sol_address(address):
        return None
    
    return address

def generate_sol_keypair() -> Tuple[str, str]:
    """Generate a random Solana keypair.
    
    Returns:
        Tuple of (address, private_key)
    """
    try:
        # Import Solana libraries
        from solana.keypair import Keypair
        
        # Generate keypair
        keypair = Keypair()
        
        # Get address (public key)
        address = str(keypair.public_key)
        
        # Get private key
        private_key = base58.b58encode(keypair.secret_key).decode('ascii')
        
        return (address, private_key)
    except ImportError:
        logger.warning("solana package not available, using mock implementation")
        
        # Mock implementation
        import os
        
        # Generate random bytes for secret key
        secret_key = os.urandom(32)
        
        # Derive public key (in a real implementation, this would use Ed25519)
        # In this mock, we're just using a different hash of the secret
        import hashlib
        public_key = hashlib.sha256(secret_key).digest()
        
        # Encode as base58
        address = base58.b58encode(public_key).decode('ascii')
        private_key = base58.b58encode(secret_key).decode('ascii')
        
        return (address, private_key)

# =========================
# Transaction Utilities
# =========================

def estimate_sol_fee(client, num_signatures: int = 1, num_instructions: int = 1) -> int:
    """Estimate transaction fee for a Solana transaction.
    
    Args:
        client: Solana client
        num_signatures: Number of signatures
        num_instructions: Number of instructions
        
    Returns:
        Estimated fee in lamports
    """
    try:
        # Get recent blockhash
        response = client.get_recent_blockhash()
        
        if "error" in response:
            logger.error(f"Failed to get recent blockhash: {response['error']}")
            # Use default fee as fallback
            return 5000
        
        # Extract fee calculator
        fee_calculator = response["result"]["value"]["feeCalculator"]
        
        # Calculate fee
        # Note: This is a simplified calculation and may not match actual fees
        lamports_per_signature = fee_calculator.get("lamportsPerSignature", 5000)
        
        # Base fee is the cost per signature
        base_fee = lamports_per_signature * num_signatures
        
        # Each instruction adds a small overhead
        instruction_overhead = 100 * num_instructions
        
        return base_fee + instruction_overhead
    except Exception as e:
        logger.error(f"Failed to estimate fee: {str(e)}")
        return 5000  # Default fee

def wait_for_sol_transaction(
    client,
    signature: str,
    timeout: int = 60,
    poll_interval: float = 0.5
) -> Dict[str, Any]:
    """Wait for a Solana transaction to be confirmed.
    
    Args:
        client: Solana client
        signature: Transaction signature
        timeout: Maximum time to wait (in seconds)
        poll_interval: Time between polls (in seconds)
        
    Returns:
        Transaction status
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check transaction status
            response = client.get_signature_statuses([signature])
            
            if "error" in response:
                logger.error(f"Error checking transaction status: {response['error']}")
                time.sleep(poll_interval)
                continue
            
            status = response["result"]["value"][0]
            
            if status is not None:
                if status.get("confirmationStatus") == "finalized":
                    # Transaction is finalized
                    return {
                        "signature": signature,
                        "status": "finalized",
                        "confirmations": status.get("confirmations", 0)
                    }
                elif status.get("confirmationStatus") == "confirmed":
                    # Transaction is confirmed but not finalized
                    return {
                        "signature": signature,
                        "status": "confirmed",
                        "confirmations": status.get("confirmations", 0)
                    }
            
            # Wait for next poll
            time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Error waiting for transaction: {str(e)}")
            time.sleep(poll_interval)
    
    # Timeout reached
    raise TimeoutError(f"Transaction not confirmed within {timeout} seconds: {signature}")

def get_sol_transaction(client, signature: str) -> Dict[str, Any]:
    """Get details of a Solana transaction.
    
    Args:
        client: Solana client
        signature: Transaction signature
        
    Returns:
        Transaction details
    """
    try:
        # Get transaction details
        response = client.get_transaction(signature)
        
        if "error" in response:
            return {
                "error": response["error"],
                "signature": signature
            }
        
        return response["result"]
    except Exception as e:
        logger.error(f"Failed to get transaction: {str(e)}")
        return {
            "error": f"Failed to get transaction: {str(e)}",
            "signature": signature
        }

# =========================
# Account Utilities
# =========================

def get_sol_account_info(client, address: str) -> Dict[str, Any]:
    """Get information about a Solana account.
    
    Args:
        client: Solana client
        address: Account address
        
    Returns:
        Account information
    """
    try:
        # Get account information
        response = client.get_account_info(address)
        
        if "error" in response:
            return {
                "error": response["error"],
                "address": address
            }
        
        account_info = response["result"]["value"]
        
        # Check if account exists
        if account_info is None:
            return {
                "error": "Account not found",
                "address": address
            }
        
        # Process account data
        data = account_info["data"]
        if isinstance(data, list) and len(data) == 2:
            # Data is [encoded_data, encoding]
            encoding = data[1]
            if encoding == "base64":
                # Decode base64 data
                try:
                    decoded_data = base64.b64decode(data[0])
                    account_info["decoded_data"] = decoded_data
                except Exception as e:
                    logger.debug(f"Failed to decode account data: {str(e)}")
            
        return {
            "address": address,
            "lamports": account_info["lamports"],
            "owner": account_info["owner"],
            "executable": account_info["executable"],
            "rent_epoch": account_info["rentEpoch"],
            "data": data
        }
    except Exception as e:
        logger.error(f"Failed to get account info: {str(e)}")
        return {
            "error": f"Failed to get account info: {str(e)}",
            "address": address
        }

def is_sol_program_account(client, address: str) -> bool:
    """Check if an account is a program account.
    
    Args:
        client: Solana client
        address: Account address
        
    Returns:
        True if account is a program account, False otherwise
    """
    try:
        # Get account information
        account_info = get_sol_account_info(client, address)
        
        # Check if there was an error
        if "error" in account_info:
            return False
        
        # Program accounts are executable
        return account_info.get("executable", False)
    except Exception as e:
        logger.error(f"Failed to check if account is program: {str(e)}")
        return False

def get_sol_token_accounts(client, owner_address: str) -> List[Dict[str, Any]]:
    """Get token accounts owned by an address.
    
    Args:
        client: Solana client
        owner_address: Owner address
        
    Returns:
        List of token accounts
    """
    try:
        # Get token accounts
        response = client.get_token_accounts_by_owner(
            owner_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}  # SPL Token program ID
        )
        
        if "error" in response:
            logger.error(f"Failed to get token accounts: {response['error']}")
            return []
        
        token_accounts = response["result"]["value"]
        
        # Process accounts
        processed_accounts = []
        for account in token_accounts:
            account_info = account["account"]
            data = account_info["data"]
            
            if isinstance(data, list) and len(data) == 2 and data[1] == "base64":
                # Decode token account data
                try:
                    decoded_data = base64.b64decode(data[0])
                    
                    # Extract relevant token information
                    # This is a simplified parsing and may not work for all token accounts
                    processed_account = {
                        "address": account["pubkey"],
                        "mint": "Unknown",  # Would require proper parsing
                        "amount": "Unknown",  # Would require proper parsing
                        "owner": owner_address,
                        "raw_data": data[0]
                    }
                    
                    processed_accounts.append(processed_account)
                except Exception as e:
                    logger.debug(f"Failed to decode token account data: {str(e)}")
                    processed_accounts.append({
                        "address": account["pubkey"],
                        "owner": owner_address,
                        "error": f"Failed to decode data: {str(e)}"
                    })
        
        return processed_accounts
    except Exception as e:
        logger.error(f"Failed to get token accounts: {str(e)}")
        return []

# =========================
# Conversion Utilities
# =========================

def lamports_to_sol(lamports: Union[int, str]) -> float:
    """Convert lamports to SOL.
    
    Args:
        lamports: Amount in lamports
        
    Returns:
        Amount in SOL
    """
    # Convert to int if string
    if isinstance(lamports, str):
        lamports = int(lamports)
    
    # Convert lamports to SOL (1 SOL = 10^9 lamports)
    return lamports / 1e9

def sol_to_lamports(sol_amount: Union[float, str]) -> int:
    """Convert SOL to lamports.
    
    Args:
        sol_amount: Amount in SOL
        
    Returns:
        Amount in lamports
    """
    # Convert to float if string
    if isinstance(sol_amount, str):
        sol_amount = float(sol_amount)
    
    # Convert SOL to lamports (1 SOL = 10^9 lamports)
    return int(sol_amount * 1e9)

# =========================
# Program Utilities
# =========================

def get_sol_program_accounts(client, program_id: str) -> List[Dict[str, Any]]:
    """Get all accounts owned by a program.
    
    Args:
        client: Solana client
        program_id: Program ID
        
    Returns:
        List of accounts
    """
    try:
        # Get accounts owned by program
        response = client.get_program_accounts(program_id)
        
        if "error" in response:
            logger.error(f"Failed to get program accounts: {response['error']}")
            return []
        
        accounts = response["result"]
        
        # Process accounts
        processed_accounts = []
        for account in accounts:
            pubkey = account["pubkey"]
            account_info = account["account"]
            
            processed_account = {
                "address": pubkey,
                "lamports": account_info["lamports"],
                "owner": account_info["owner"],
                "executable": account_info["executable"],
                "rent_epoch": account_info["rentEpoch"],
                "data": account_info["data"]
            }
            
            # Try to decode data if it's base64 encoded
            data = account_info["data"]
            if isinstance(data, list) and len(data) == 2 and data[1] == "base64":
                try:
                    decoded_data = base64.b64decode(data[0])
                    processed_account["decoded_data"] = decoded_data
                except Exception as e:
                    logger.debug(f"Failed to decode account data: {str(e)}")
            
            processed_accounts.append(processed_account)
        
        return processed_accounts
    except Exception as e:
        logger.error(f"Failed to get program accounts: {str(e)}")
        return []

def is_sol_token_account(account_info: Dict[str, Any]) -> bool:
    """Check if an account is a token account.
    
    Args:
        account_info: Account information
        
    Returns:
        True if account is a token account, False otherwise
    """
    # Check if account is owned by the SPL Token program
    return account_info.get("owner") == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

def decode_sol_token_account(data: str) -> Dict[str, Any]:
    """Decode Solana token account data.
    
    Args:
        data: Base64 encoded token account data
        
    Returns:
        Decoded token account information
    """
    try:
        # Decode base64
        decoded = base64.b64decode(data)
        
        # Token account data structure (simplified)
        # This is a simplified parsing and may not work for all token accounts
        if len(decoded) >= 165:  # Minimum size for token accounts
            mint_start = 0
            mint_end = 32
            owner_start = 32
            owner_end = 64
            amount_start = 64
            amount_end = 72
            
            mint = base58.b58encode(decoded[mint_start:mint_end]).decode('ascii')
            owner = base58.b58encode(decoded[owner_start:owner_end]).decode('ascii')
            amount = int.from_bytes(decoded[amount_start:amount_end], byteorder='little')
            
            return {
                "mint": mint,
                "owner": owner,
                "amount": amount
            }
        
        return {
            "error": "Invalid token account data size",
            "raw_data": data
        }
    except Exception as e:
        logger.error(f"Failed to decode token account data: {str(e)}")
        return {
            "error": f"Failed to decode data: {str(e)}",
            "raw_data": data
        }

# =========================
# Common Solana Program IDs
# =========================

SOLANA_PROGRAM_IDS = {
    "token": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "associated_token": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
    "system": "11111111111111111111111111111111",
    "stake": "Stake11111111111111111111111111111111111111",
    "vote": "Vote111111111111111111111111111111111111111",
    "bpf_loader": "BPFLoaderUpgradeab1e11111111111111111111111",
    "config": "Config1111111111111111111111111111111111111",
    "serum_dex_v3": "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
    "memo": "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr",
    "metadata": "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
    "name_service": "namesLPneVptA9Z5rqUDD9tMTWEJwofgaYwp8cawRkX",
    "raydium_amm": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "wormhole": "worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth",
    "marinade": "MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD",
    "jupiter_aggregator": "JUP6i4ozu5ydDCnLiMogSckDPpbtr7BJ4FtzYWkb5Rk",
    "pyth": "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
}

# =========================
# NFT Utilities
# =========================

def get_sol_nft_metadata(client, mint_address: str) -> Dict[str, Any]:
    """Get Solana NFT metadata.
    
    Args:
        client: Solana client
        mint_address: NFT mint address
        
    Returns:
        NFT metadata
    """
    try:
        # Metadata program ID
        metadata_program_id = SOLANA_PROGRAM_IDS["metadata"]
        
        # Calculate metadata account address
        import hashlib
        seeds = [
            b"metadata",
            bytes(metadata_program_id, "utf-8"),
            base58.b58decode(mint_address)
        ]
        
        # Find program derived address
        # This is simplified and may not match the actual implementation
        seed_bytes = b"".join(seeds)
        metadata_address_bytes = hashlib.sha256(seed_bytes).digest()[:32]
        metadata_address = base58.b58encode(metadata_address_bytes).decode("utf-8")
        
        # Get metadata account
        metadata_account = get_sol_account_info(client, metadata_address)
        
        if "error" in metadata_account:
            return {
                "error": f"Failed to get metadata account: {metadata_account['error']}",
                "mint": mint_address
            }
        
        # Parse metadata
        # This is a placeholder - actual implementation would parse the account data
        # according to the Metaplex metadata schema
        return {
            "mint": mint_address,
            "metadata_address": metadata_address,
            "raw_data": metadata_account.get("data"),
            "parsed": "Metadata parsing not implemented yet"
        }
    except Exception as e:
        logger.error(f"Failed to get NFT metadata: {str(e)}")
        return {
            "error": f"Failed to get NFT metadata: {str(e)}",
            "mint": mint_address
        }

def get_sol_token_metadata(client, mint_address: str) -> Dict[str, Any]:
    """Get Solana token metadata.
    
    Args:
        client: Solana client
        mint_address: Token mint address
        
    Returns:
        Token metadata
    """
    try:
        # First get the mint account info
        mint_account = get_sol_account_info(client, mint_address)
        
        if "error" in mint_account:
            return mint_account
        
        # Then try to get metadata account (same as NFT metadata)
        metadata = get_sol_nft_metadata(client, mint_address)
        
        # Combine information
        token_info = {
            "mint": mint_address,
            "decimals": None,  # Would require parsing mint account data
            "supply": None,    # Would require parsing mint account data
            "metadata": metadata if "error" not in metadata else None
        }
        
        return token_info
    except Exception as e:
        logger.error(f"Failed to get token metadata: {str(e)}")
        return {
            "error": f"Failed to get token metadata: {str(e)}",
            "mint": mint_address
        }

# =========================
# Common Solana Constants
# =========================

# Standard rent exemption for accounts in lamports
SOLANA_RENT_EXEMPTION = {
    "account": 2039280,  # Standard account (for small data)
    "token_account": 2039280,  # Token account
    "mint": 1461600,  # Mint account
}

# Common commitment levels
SOLANA_COMMITMENT_LEVELS = [
    "processed",  # Processed by current node but not confirmed
    "confirmed",  # Confirmed by supermajority of the cluster
    "finalized",  # Finalized by the cluster
]

# Epochs per year (approximate)
SOLANA_EPOCHS_PER_YEAR = 365 * 2  # ~2 days per epoch

# Current solana URL endpoints
SOLANA_RPC_ENDPOINTS = {
    "mainnet": [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana",
        "https://api.metaplex.solana.com"
    ],
    "devnet": [
        "https://api.devnet.solana.com"
    ],
    "testnet": [
        "https://api.testnet.solana.com"
    ],
    "localnet": [
        "http://localhost:8899"
    ]
}

# Public key of token program
TOKEN_PROGRAM_ID = SOLANA_PROGRAM_IDS["token"]

# Public key of associated token program
ASSOCIATED_TOKEN_PROGRAM_ID = SOLANA_PROGRAM_IDS["associated_token"]

# =========================
# Transaction Building Helpers
# =========================

def calculate_sol_transaction_size(
    num_signatures: int,
    num_instructions: int,
    instruction_data_size: int
) -> int:
    """Calculate the size of a Solana transaction.
    
    Args:
        num_signatures: Number of signatures
        num_instructions: Number of instructions
        instruction_data_size: Total size of instruction data
        
    Returns:
        Transaction size in bytes
    """
    # Signature size
    signature_size = 64
    
    # Base transaction size
    base_size = 1 + 1 + signature_size * num_signatures + 32 + 8 + 1
    
    # Instruction size
    instruction_size = num_instructions * (1 + 1 + 32 + 1 + instruction_data_size)
    
    return base_size + instruction_size

def encode_sol_instruction_data(instruction_data: Dict[str, Any]) -> bytes:
    """Encode Solana instruction data.
    
    Args:
        instruction_data: Instruction data
        
    Returns:
        Encoded instruction data
    """
    # This is a placeholder - actual implementation would depend on the format
    # of the instruction data and the specific program being called
    return b''
