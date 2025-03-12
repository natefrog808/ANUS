"""
Unit tests for Web3Agent class.

This module contains tests for the Web3Agent class, ensuring proper 
functionality for all agent methods and behaviors.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any, List

# Import the agent to test
from anus.web3 import Web3Agent

# Import test fixtures
from tests.web3.fixtures.mock_web3 import (
    mock_web3_instance,
    mock_solana_client,
    mock_contract,
    TEST_ADDRESS,
    TEST_CONTRACT_ADDRESS,
    TEST_TOKEN_ADDRESS,
    TEST_NFT_CONTRACT,
    TEST_NFT_ID,
    TEST_ENS_NAME,
    TEST_IPFS_CID
)

# =====================================
# Web3Agent Initialization Tests
# =====================================

def test_web3_agent_initialization():
    """Test Web3Agent initialization."""
    # Test with empty config
    agent = Web3Agent()
    assert agent.role == "web3_specialist"
    assert hasattr(agent, "connection_tool")
    assert hasattr(agent, "tools")
    assert len(agent.tools) >= 7  # Should have at least 7 Web3 tools
    
    # Test with config
    config = {
        "ethereum_provider": "http://localhost:8545",
        "memory_path": "./test_memory"
    }
    agent = Web3Agent(config)
    assert agent.config == config
    assert agent.connection_tool.config == config

# =====================================
# Web3Agent Connection Tests
# =====================================

def test_connect_wallet():
    """Test Web3Agent connect_wallet method."""
    agent = Web3Agent()
    agent.run_tool = MagicMock(return_value={"status": "connected", "block_number": 12345})
    
    result = agent.connect_wallet("ethereum")
    
    agent.run_tool.assert_called_with("web3_connection", {"network": "ethereum"})
    assert result["status"] == "connected"
    assert result["block_number"] == 12345
    
    # Test with custom provider
    result = agent.connect_wallet("ethereum", provider_url="custom_url")
    
    agent.run_tool.assert_called_with("web3_connection", {"network": "ethereum", "provider_url": "custom_url"})
    assert result["status"] == "connected"
    
    # Test with network type
    result = agent.connect_wallet("ethereum", "sepolia")
    
    agent.run_tool.assert_called_with("web3_connection", {"network": "ethereum", "network_type": "sepolia"})
    assert result["status"] == "connected"

# =====================================
# Web3Agent Token Tests
# =====================================

def test_token_balance():
    """Test Web3Agent token_balance method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={"balance": 1.5, "symbol": "ETH"})
    
    # Test native token balance
    result = agent.token_balance(TEST_ADDRESS)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "native_balance",
        "address": TEST_ADDRESS
    })
    assert result["balance"] == 1.5
    assert result["symbol"] == "ETH"
    
    # Test ERC-20 token balance
    result = agent.token_balance(TEST_ADDRESS, TEST_TOKEN_ADDRESS)
    
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "token_balance",
        "address": TEST_ADDRESS,
        "token_address": TEST_TOKEN_ADDRESS
    })
    assert result["balance"] == 1.5
    
    # Test with different network
    result = agent.token_balance(TEST_ADDRESS, network="solana")
    
    agent.connect_wallet.assert_called_with("solana", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "solana",
        "network_type": "mainnet",
        "action": "native_balance",
        "address": TEST_ADDRESS
    })
    assert result["balance"] == 1.5

def test_token_info():
    """Test Web3Agent token_info method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "address": TEST_TOKEN_ADDRESS,
        "name": "Test Token",
        "symbol": "TT",
        "decimals": 18,
        "total_supply": 1000000
    })
    
    result = agent.token_info(TEST_TOKEN_ADDRESS)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "token_info",
        "token_address": TEST_TOKEN_ADDRESS
    })
    assert result["name"] == "Test Token"
    assert result["symbol"] == "TT"
    assert result["decimals"] == 18
    assert result["total_supply"] == 1000000

def test_transfer_tokens():
    """Test Web3Agent transfer_tokens method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "transaction_hash": "0x123456789abcdef",
        "status": "pending"
    })
    
    # Test native token transfer
    result = agent.transfer_tokens(
        from_address=TEST_ADDRESS,
        to_address="0xRecipientAddress",
        amount=1.5,
        private_key="0x123456789abcdef"
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "transfer",
        "address": TEST_ADDRESS,
        "to_address": "0xRecipientAddress",
        "amount": "1.5",
        "private_key": "0x123456789abcdef"
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"
    
    # Test ERC-20 token transfer
    result = agent.transfer_tokens(
        from_address=TEST_ADDRESS,
        to_address="0xRecipientAddress",
        amount=100,
        token_address=TEST_TOKEN_ADDRESS,
        private_key="0x123456789abcdef"
    )
    
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "transfer",
        "address": TEST_ADDRESS,
        "to_address": "0xRecipientAddress",
        "amount": "100",
        "token_address": TEST_TOKEN_ADDRESS,
        "private_key": "0x123456789abcdef"
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"

def test_approve_tokens():
    """Test Web3Agent approve_tokens method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "transaction_hash": "0x123456789abcdef",
        "status": "pending"
    })
    
    result = agent.approve_tokens(
        address=TEST_ADDRESS,
        spender_address="0xSpenderAddress",
        amount=100,
        token_address=TEST_TOKEN_ADDRESS,
        private_key="0x123456789abcdef"
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "approve",
        "address": TEST_ADDRESS,
        "spender_address": "0xSpenderAddress",
        "amount": "100",
        "token_address": TEST_TOKEN_ADDRESS,
        "private_key": "0x123456789abcdef"
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"

def test_check_allowance():
    """Test Web3Agent check_allowance method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "owner": TEST_ADDRESS,
        "spender": "0xSpenderAddress",
        "token_address": TEST_TOKEN_ADDRESS,
        "allowance": 100,
        "allowance_raw": "100000000000000000000"
    })
    
    result = agent.check_allowance(
        owner_address=TEST_ADDRESS,
        spender_address="0xSpenderAddress",
        token_address=TEST_TOKEN_ADDRESS
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("token", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "allowance",
        "address": TEST_ADDRESS,
        "spender_address": "0xSpenderAddress",
        "token_address": TEST_TOKEN_ADDRESS
    })
    assert result["owner"] == TEST_ADDRESS
    assert result["spender"] == "0xSpenderAddress"
    assert result["allowance"] == 100

# =====================================
# Web3Agent NFT Tests
# =====================================

def test_nft_info():
    """Test Web3Agent nft_info method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "owner": TEST_ADDRESS,
        "token_uri": f"ipfs://{TEST_IPFS_CID}",
        "metadata": {
            "name": "Test NFT",
            "description": "A test NFT",
            "image": f"ipfs://{TEST_IPFS_CID}/image.png"
        }
    })
    
    result = agent.nft_info(TEST_NFT_CONTRACT, TEST_NFT_ID)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("nft", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "get_metadata",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "force_refresh": False
    })
    assert result["contract_address"] == TEST_NFT_CONTRACT
    assert result["token_id"] == TEST_NFT_ID
    assert result["owner"] == TEST_ADDRESS
    assert result["metadata"]["name"] == "Test NFT"

def test_nft_owner():
    """Test Web3Agent nft_owner method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "owner": TEST_ADDRESS
    })
    
    result = agent.nft_owner(TEST_NFT_CONTRACT, TEST_NFT_ID)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("nft", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "get_owner",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID
    })
    assert result["contract_address"] == TEST_NFT_CONTRACT
    assert result["token_id"] == TEST_NFT_ID
    assert result["owner"] == TEST_ADDRESS

def test_transfer_nft():
    """Test Web3Agent transfer_nft method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "transaction_hash": "0x123456789abcdef",
        "status": "pending",
        "from": TEST_ADDRESS,
        "to": "0xRecipientAddress",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID
    })
    
    result = agent.transfer_nft(
        from_address=TEST_ADDRESS,
        to_address="0xRecipientAddress",
        contract_address=TEST_NFT_CONTRACT,
        token_id=TEST_NFT_ID,
        private_key="0x123456789abcdef"
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("nft", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "transfer",
        "address": TEST_ADDRESS,
        "to_address": "0xRecipientAddress",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "private_key": "0x123456789abcdef",
        "token_standard": "ERC721"
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"
    assert result["from"] == TEST_ADDRESS
    assert result["to"] == "0xRecipientAddress"

# =====================================
# Web3Agent Smart Contract Tests
# =====================================

def test_call_contract():
    """Test Web3Agent call_contract method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={"result": 100})
    
    contract_abi = [{"name": "balanceOf", "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]}]
    
    result = agent.call_contract(
        contract_address=TEST_CONTRACT_ADDRESS,
        method_name="balanceOf",
        args=[TEST_ADDRESS],
        contract_abi=contract_abi
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("smart_contract", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "read",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "method_name": "balanceOf",
        "args": [TEST_ADDRESS],
        "contract_abi": contract_abi
    })
    assert result["result"] == 100

def test_send_contract_transaction():
    """Test Web3Agent send_contract_transaction method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "transaction_hash": "0x123456789abcdef",
        "status": "pending"
    })
    
    contract_abi = [{"name": "transfer", "inputs": [{"type": "address"}, {"type": "uint256"}], "outputs": [{"type": "bool"}]}]
    
    result = agent.send_contract_transaction(
        contract_address=TEST_CONTRACT_ADDRESS,
        method_name="transfer",
        args=["0xRecipientAddress", 100],
        contract_abi=contract_abi,
        from_address=TEST_ADDRESS,
        private_key="0x123456789abcdef",
        gas=200000
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("smart_contract", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "write",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "method_name": "transfer",
        "args": ["0xRecipientAddress", 100],
        "contract_abi": contract_abi,
        "from_address": TEST_ADDRESS,
        "private_key": "0x123456789abcdef",
        "gas": 200000
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"

# =====================================
# Web3Agent ENS Tests
# =====================================

def test_resolve_ens():
    """Test Web3Agent resolve_ens method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "name": TEST_ENS_NAME,
        "address": TEST_ADDRESS
    })
    
    result = agent.resolve_ens(TEST_ENS_NAME)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("ens", {
        "action": "resolve",
        "name": TEST_ENS_NAME,
        "force_refresh": False
    })
    assert result["name"] == TEST_ENS_NAME
    assert result["address"] == TEST_ADDRESS

def test_lookup_ens():
    """Test Web3Agent lookup_ens method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "address": TEST_ADDRESS,
        "name": TEST_ENS_NAME
    })
    
    result = agent.lookup_ens(TEST_ADDRESS)
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("ens", {
        "action": "lookup",
        "address": TEST_ADDRESS,
        "force_refresh": False
    })
    assert result["address"] == TEST_ADDRESS
    assert result["name"] == TEST_ENS_NAME

# =====================================
# Web3Agent IPFS Tests
# =====================================

def test_get_ipfs_content():
    """Test Web3Agent get_ipfs_content method."""
    agent = Web3Agent()
    agent.run_tool = MagicMock(return_value={
        "cid": TEST_IPFS_CID,
        "content": "Test content",
        "content_type": "text/plain",
        "size": 12
    })
    
    result = agent.get_ipfs_content(TEST_IPFS_CID)
    
    agent.run_tool.assert_called_with("ipfs", {
        "action": "get",
        "cid": TEST_IPFS_CID,
        "path": "",
        "force_refresh": False
    })
    assert result["cid"] == TEST_IPFS_CID
    assert result["content"] == "Test content"
    assert result["content_type"] == "text/plain"
    assert result["size"] == 12

def test_add_to_ipfs():
    """Test Web3Agent add_to_ipfs method."""
    agent = Web3Agent()
    agent.run_tool = MagicMock(return_value={
        "cid": TEST_IPFS_CID,
        "size": 12
    })
    
    data = {"test": "data"}
    result = agent.add_to_ipfs(data)
    
    agent.run_tool.assert_called_with("ipfs", {
        "action": "add",
        "data": data
    })
    assert result["cid"] == TEST_IPFS_CID
    assert result["size"] == 12

# =====================================
# Web3Agent DeFi Tests
# =====================================

def test_swap_tokens():
    """Test Web3Agent swap_tokens method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "transaction_hash": "0x123456789abcdef",
        "status": "pending",
        "from": TEST_ADDRESS,
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0",
        "expected_out": "1800.0"
    })
    
    result = agent.swap_tokens(
        address=TEST_ADDRESS,
        private_key="0x123456789abcdef",
        token_in="ETH",
        token_out="USDC",
        amount_in=1.0,
        slippage=0.5
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("defi", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "swap",
        "protocol": "uniswap_v2",
        "address": TEST_ADDRESS,
        "private_key": "0x123456789abcdef",
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0",
        "slippage": 0.5
    })
    assert result["transaction_hash"] == "0x123456789abcdef"
    assert result["status"] == "pending"
    assert result["token_in"] == "ETH"
    assert result["token_out"] == "USDC"
    assert result["amount_in"] == "1.0"
    assert result["expected_out"] == "1800.0"

def test_get_swap_quote():
    """Test Web3Agent get_swap_quote method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(return_value={
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": 1.0,
        "amount_out": 1800.0,
        "price_impact": "2.00%"
    })
    
    result = agent.get_swap_quote(
        token_in="ETH",
        token_out="USDC",
        amount_in=1.0
    )
    
    agent.connect_wallet.assert_called_with("ethereum", "mainnet")
    agent.run_tool.assert_called_with("defi", {
        "network": "ethereum",
        "network_type": "mainnet",
        "action": "get_swap_quote",
        "protocol": "uniswap_v2",
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0"
    })
    assert result["token_in"] == "ETH"
    assert result["token_out"] == "USDC"
    assert result["amount_in"] == 1.0
    assert result["amount_out"] == 1800.0
    assert result["price_impact"] == "2.00%"

# =====================================
# Web3Agent Analysis Tests
# =====================================

def test_wallet_status():
    """Test Web3Agent wallet_status method."""
    agent = Web3Agent()
    agent.connect_wallet = MagicMock(return_value={"status": "connected"})
    agent.run_tool = MagicMock(side_effect=[
        # First call for ETH balance
        {
            "address": TEST_ADDRESS,
            "balance": 10.5,
            "symbol": "ETH"
        },
        # Second call for ENS lookup
        {
            "address": TEST_ADDRESS,
            "name": TEST_ENS_NAME
        }
    ])
    
    result = agent.wallet_status(TEST_ADDRESS)
    
    assert "ethereum" in result
    assert "native_balance" in result["ethereum"]
    assert result["ethereum"]["native_balance"]["balance"] == 10.5
    assert result["ethereum"]["native_balance"]["symbol"] == "ETH"
    assert result["ethereum"]["ens_name"] == TEST_ENS_NAME
    
    # Test with multiple networks
    agent.run_tool.reset_mock()
    agent.run_tool.side_effect = [
        # ETH balance
        {
            "address": TEST_ADDRESS,
            "balance": 10.5,
            "symbol": "ETH"
        },
        # ENS lookup
        {
            "address": TEST_ADDRESS,
            "name": TEST_ENS_NAME
        },
        # SOL balance
        {
            "address": TEST_ADDRESS,
            "balance": 20.0,
            "symbol": "SOL"
        }
    ]
    
    result = agent.wallet_status(TEST_ADDRESS, networks=["ethereum", "solana"])
    
    assert "ethereum" in result
    assert "solana" in result
    assert result["ethereum"]["native_balance"]["balance"] == 10.5
    assert result["ethereum"]["native_balance"]["symbol"] == "ETH"
    assert result["solana"]["native_balance"]["balance"] == 20.0
    assert result["solana"]["native_balance"]["symbol"] == "SOL"

def test_run_tool():
    """Test Web3Agent run_tool method."""
    agent = Web3Agent()
    
    # Mock the tools
    for tool in agent.tools:
        tool._execute = MagicMock(return_value={"result": "success", "tool": tool.name})
    
    # Test with existing tool
    for tool in agent.tools:
        result = agent.run_tool(tool.name, {"test": "params"})
        tool._execute.assert_called_with({"test": "params"})
        assert result["result"] == "success"
        assert result["tool"] == tool.name
    
    # Test with non-existent tool
    result = agent.run_tool("non_existent_tool", {"test": "params"})
    assert "error" in result
    assert "not found" in result["error"]
