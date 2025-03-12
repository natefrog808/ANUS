"""
Unit tests for Web3 tools module.

This module contains tests for each Web3 tool in the Anus AI Web3 module.
Tests use pytest and mock external dependencies to ensure proper functionality.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

# Import tools to test
from anus.web3.tools import (
    Web3BaseTool,
    Web3ConnectionTool,
    SmartContractTool,
    TokenTool,
    NFTTool,
    DeFiTool,
    ENSTool,
    IPFSTool
)

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
# Web3BaseTool Tests
# =====================================

def test_web3_base_tool_initialization():
    """Test Web3BaseTool initialization."""
    tool = Web3BaseTool()
    assert tool.category == "web3"

def test_web3_base_tool_format_error():
    """Test Web3BaseTool error formatting."""
    tool = Web3BaseTool()
    error_message = "Test error message"
    
    # Test without details
    error = tool._format_error(error_message)
    assert error["error"] == error_message
    assert "details" not in error
    
    # Test with details
    details = {"additional": "info"}
    error_with_details = tool._format_error(error_message, details)
    assert error_with_details["error"] == error_message
    assert error_with_details["details"] == details

def test_web3_base_tool_safe_execute():
    """Test Web3BaseTool safe execute method."""
    tool = Web3BaseTool()
    
    # Test with function that succeeds
    def success_func():
        return {"success": True}
    
    result = tool._safe_execute(success_func)
    assert result["success"] is True
    
    # Test with function that raises exception
    def error_func():
        raise ValueError("Test error")
    
    result = tool._safe_execute(error_func)
    assert "error" in result
    assert "Test error" in result["error"]

# =====================================
# Web3ConnectionTool Tests
# =====================================

def test_web3_connection_tool_initialization():
    """Test Web3ConnectionTool initialization."""
    config = {"ethereum_provider": "http://localhost:8545"}
    tool = Web3ConnectionTool(config)
    
    assert tool.name == "web3_connection"
    assert tool.description is not None
    assert tool.config == config

@patch("anus.web3.tools.Web3")
def test_web3_connection_tool_ethereum_execute(mock_web3_class, mock_web3_instance):
    """Test Web3ConnectionTool execute method with Ethereum."""
    mock_web3_class.return_value = mock_web3_instance
    mock_web3_class.HTTPProvider = MagicMock()
    
    config = {"ethereum_provider": "http://localhost:8545"}
    tool = Web3ConnectionTool(config)
    
    params = {"network": "ethereum"}
    result = tool._execute(params)
    
    assert "status" in result
    assert "network" in result
    assert result["network"] == "ethereum"

@patch("anus.web3.tools.Client")
def test_web3_connection_tool_solana_execute(mock_solana_client_class, mock_solana_client):
    """Test Web3ConnectionTool execute method with Solana."""
    mock_solana_client_class.return_value = mock_solana_client
    
    config = {"solana_provider": "https://api.mainnet-beta.solana.com"}
    tool = Web3ConnectionTool(config)
    
    params = {"network": "solana"}
    result = tool._execute(params)
    
    assert "status" in result
    assert "network" in result
    assert result["network"] == "solana"

def test_web3_connection_is_connected():
    """Test Web3ConnectionTool _is_connected method."""
    tool = Web3ConnectionTool()
    tool._connections = {
        "ethereum": MagicMock(),
        "solana": MagicMock()
    }
    
    # Mock Ethereum connection
    tool._connections["ethereum"].is_connected.return_value = True
    assert tool._is_connected("ethereum") is True
    
    # Mock Solana connection
    tool._connections["solana"].is_connected.return_value = True
    assert tool._is_connected("solana") is True
    
    # Test non-existent network
    assert tool._is_connected("unknown_network") is False

def test_web3_connection_get_block_number():
    """Test Web3ConnectionTool _get_block_number method."""
    tool = Web3ConnectionTool()
    tool._connections = {
        "ethereum": MagicMock(),
        "solana": MagicMock()
    }
    
    # Mock Ethereum block number
    tool._connections["ethereum"].eth.block_number = 12345
    assert tool._get_block_number("ethereum") == 12345
    
    # Mock Solana block height
    tool._connections["solana"].get_block_height.return_value = {"result": 67890}
    assert tool._get_block_number("solana") == 67890
    
    # Test with non-connected network
    tool._is_connected = MagicMock(return_value=False)
    assert tool._get_block_number("ethereum") is None

# =====================================
# SmartContractTool Tests
# =====================================

def test_smart_contract_tool_initialization():
    """Test SmartContractTool initialization."""
    connection_tool = MagicMock()
    tool = SmartContractTool(connection_tool)
    
    assert tool.name == "smart_contract"
    assert tool.description is not None
    assert tool.connection_tool == connection_tool

def test_smart_contract_tool_execute_missing_params():
    """Test SmartContractTool execute method with missing parameters."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    
    tool = SmartContractTool(connection_tool)
    
    # Test with missing contract_address
    result = tool._execute({
        "network": "ethereum",
        "action": "read",
        "method_name": "balanceOf",
        "args": [TEST_ADDRESS],
        "contract_abi": []
    })
    assert "error" in result
    
    # Test with missing contract_abi
    result = tool._execute({
        "network": "ethereum",
        "action": "read",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "method_name": "balanceOf",
        "args": [TEST_ADDRESS]
    })
    assert "error" in result
    
    # Test with missing method_name
    result = tool._execute({
        "network": "ethereum",
        "action": "read",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "contract_abi": [],
        "args": [TEST_ADDRESS]
    })
    assert "error" in result

@patch("anus.web3.tools.SmartContractTool._read_contract")
def test_smart_contract_tool_read_execute(mock_read_contract):
    """Test SmartContractTool execute method with read action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    mock_read_contract.return_value = {"result": 100}
    
    tool = SmartContractTool(connection_tool)
    tool._contracts = {}
    
    # Set up connection
    result = tool._execute({
        "network": "ethereum",
        "action": "read",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "contract_abi": [],
        "method_name": "balanceOf",
        "args": [TEST_ADDRESS]
    })
    
    assert "result" in result
    assert result["result"] == 100

@patch("anus.web3.tools.SmartContractTool._write_contract")
def test_smart_contract_tool_write_execute(mock_write_contract):
    """Test SmartContractTool execute method with write action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    mock_write_contract.return_value = {
        "transaction_hash": "0x123456789abcdef",
        "status": "pending"
    }
    
    tool = SmartContractTool(connection_tool)
    tool._contracts = {}
    
    # Test with missing from_address
    result = tool._execute({
        "network": "ethereum",
        "action": "write",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "contract_abi": [],
        "method_name": "transfer",
        "args": [TEST_ADDRESS, 100]
    })
    assert "error" in result
    
    # Test with valid params
    result = tool._execute({
        "network": "ethereum",
        "action": "write",
        "contract_address": TEST_CONTRACT_ADDRESS,
        "contract_abi": [],
        "method_name": "transfer",
        "args": [TEST_ADDRESS, 100],
        "from_address": TEST_ADDRESS,
        "private_key": "0x123456789abcdef"
    })
    
    assert "transaction_hash" in result
    assert result["status"] == "pending"

# =====================================
# TokenTool Tests
# =====================================

def test_token_tool_initialization():
    """Test TokenTool initialization."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    
    tool = TokenTool(connection_tool, contract_tool)
    
    assert tool.name == "token"
    assert tool.description is not None
    assert tool.connection_tool == connection_tool
    assert tool.contract_tool == contract_tool

def test_token_tool_missing_address():
    """Test TokenTool execute method with missing address parameter."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    
    tool = TokenTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "native_balance"
    })
    
    assert "error" in result
    assert "address" in result["error"]

@patch("anus.web3.tools.TokenTool._eth_native_balance")
def test_token_tool_native_balance(mock_native_balance):
    """Test TokenTool execute method with native_balance action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_native_balance.return_value = {
        "address": TEST_ADDRESS,
        "balance": 1.5,
        "balance_wei": "1500000000000000000",
        "symbol": "ETH"
    }
    
    tool = TokenTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "native_balance",
        "address": TEST_ADDRESS
    })
    
    assert "balance" in result
    assert result["symbol"] == "ETH"
    assert result["address"] == TEST_ADDRESS

@patch("anus.web3.tools.TokenTool._eth_token_balance")
def test_token_tool_token_balance(mock_token_balance):
    """Test TokenTool execute method with token_balance action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_token_balance.return_value = {
        "address": TEST_ADDRESS,
        "token_address": TEST_TOKEN_ADDRESS,
        "balance": 100.0,
        "balance_raw": "100000000",
        "symbol": "USDC",
        "decimals": 6
    }
    
    tool = TokenTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "token_balance",
        "address": TEST_ADDRESS,
        "token_address": TEST_TOKEN_ADDRESS
    })
    
    assert "balance" in result
    assert result["symbol"] == "USDC"
    assert result["token_address"] == TEST_TOKEN_ADDRESS

@patch("anus.web3.tools.TokenTool._eth_transfer")
def test_token_tool_transfer(mock_transfer):
    """Test TokenTool execute method with transfer action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_transfer.return_value = {
        "transaction_hash": "0x123456789abcdef",
        "status": "pending",
        "from": TEST_ADDRESS,
        "to": "0xRecipientAddress",
        "amount": "1.5",
        "symbol": "ETH"
    }
    
    tool = TokenTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "transfer",
        "address": TEST_ADDRESS,
        "to_address": "0xRecipientAddress",
        "amount": "1.5",
        "private_key": "0x123456789abcdef"
    })
    
    assert "transaction_hash" in result
    assert result["status"] == "pending"
    assert result["from"] == TEST_ADDRESS
    assert result["to"] == "0xRecipientAddress"

# =====================================
# NFTTool Tests
# =====================================

def test_nft_tool_initialization():
    """Test NFTTool initialization."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    
    tool = NFTTool(connection_tool, contract_tool)
    
    assert tool.name == "nft"
    assert tool.description is not None
    assert tool.connection_tool == connection_tool
    assert tool.contract_tool == contract_tool

def test_nft_tool_missing_address():
    """Test NFTTool execute method with missing address parameter."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    
    tool = NFTTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "get_owned"
    })
    
    assert "error" in result
    assert "address" in result["error"]

@patch("anus.web3.tools.NFTTool._eth_get_metadata")
def test_nft_tool_get_metadata(mock_get_metadata):
    """Test NFTTool execute method with get_metadata action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_get_metadata.return_value = {
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "token_uri": f"ipfs://{TEST_IPFS_CID}",
        "owner": TEST_ADDRESS,
        "metadata": {
            "name": "Test NFT",
            "description": "A test NFT",
            "image": f"ipfs://{TEST_IPFS_CID}/image.png"
        }
    }
    
    tool = NFTTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "get_metadata",
        "address": TEST_ADDRESS,
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID
    })
    
    assert "metadata" in result
    assert result["contract_address"] == TEST_NFT_CONTRACT
    assert result["token_id"] == TEST_NFT_ID
    assert result["owner"] == TEST_ADDRESS

@patch("anus.web3.tools.NFTTool._eth_get_owner")
def test_nft_tool_get_owner(mock_get_owner):
    """Test NFTTool execute method with get_owner action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_get_owner.return_value = {
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "owner": TEST_ADDRESS
    }
    
    tool = NFTTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "get_owner",
        "address": TEST_ADDRESS,
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID
    })
    
    assert "owner" in result
    assert result["owner"] == TEST_ADDRESS

@patch("anus.web3.tools.NFTTool._eth_transfer_nft")
def test_nft_tool_transfer(mock_transfer):
    """Test NFTTool execute method with transfer action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    
    mock_transfer.return_value = {
        "transaction_hash": "0x123456789abcdef",
        "status": "pending",
        "from": TEST_ADDRESS,
        "to": "0xRecipientAddress",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID
    }
    
    tool = NFTTool(connection_tool, contract_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "transfer",
        "address": TEST_ADDRESS,
        "to_address": "0xRecipientAddress",
        "contract_address": TEST_NFT_CONTRACT,
        "token_id": TEST_NFT_ID,
        "private_key": "0x123456789abcdef"
    })
    
    assert "transaction_hash" in result
    assert result["status"] == "pending"
    assert result["from"] == TEST_ADDRESS
    assert result["to"] == "0xRecipientAddress"

# =====================================
# DeFiTool Tests
# =====================================

def test_defi_tool_initialization():
    """Test DeFiTool initialization."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    token_tool = MagicMock()
    
    tool = DeFiTool(connection_tool, contract_tool, token_tool)
    
    assert tool.name == "defi"
    assert tool.description is not None
    assert tool.connection_tool == connection_tool
    assert tool.contract_tool == contract_tool
    assert tool.token_tool == token_tool

def test_defi_tool_missing_parameters():
    """Test DeFiTool execute method with missing parameters."""
    connection_tool = MagicMock()
    contract_tool = MagicMock()
    token_tool = MagicMock()
    
    tool = DeFiTool(connection_tool, contract_tool, token_tool)
    
    # Test missing action
    result = tool._execute({
        "network": "ethereum",
        "address": TEST_ADDRESS,
        "protocol": "uniswap"
    })
    assert "error" in result
    assert "action" in result["error"]
    
    # Test missing address
    result = tool._execute({
        "network": "ethereum",
        "action": "swap",
        "protocol": "uniswap"
    })
    assert "error" in result
    assert "address" in result["error"]

@patch("anus.web3.tools.DeFiTool._eth_uniswap_swap")
def test_defi_tool_swap(mock_swap):
    """Test DeFiTool execute method with swap action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    token_tool = MagicMock()
    
    mock_swap.return_value = {
        "transaction_hash": "0x123456789abcdef",
        "status": "pending",
        "from": TEST_ADDRESS,
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0",
        "expected_out": "1800.0",
        "slippage": 0.5
    }
    
    tool = DeFiTool(connection_tool, contract_tool, token_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "swap",
        "protocol": "uniswap_v2",
        "address": TEST_ADDRESS,
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0",
        "private_key": "0x123456789abcdef"
    })
    
    assert "transaction_hash" in result
    assert result["status"] == "pending"
    assert result["token_in"] == "ETH"
    assert result["token_out"] == "USDC"

@patch("anus.web3.tools.DeFiTool._eth_uniswap_quote")
def test_defi_tool_get_swap_quote(mock_quote):
    """Test DeFiTool execute method with get_swap_quote action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    contract_tool = MagicMock()
    token_tool = MagicMock()
    
    mock_quote.return_value = {
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": 1.0,
        "amount_out": 1800.0,
        "amount_out_units": 1800000000,
        "price_impact": "2.00%",
        "fee": "0.30%",
        "route": ["ETH", "USDC"]
    }
    
    tool = DeFiTool(connection_tool, contract_tool, token_tool)
    
    result = tool._execute({
        "network": "ethereum",
        "action": "get_swap_quote",
        "protocol": "uniswap_v2",
        "address": TEST_ADDRESS,
        "token_in": "ETH",
        "token_out": "USDC",
        "amount_in": "1.0"
    })
    
    assert "amount_out" in result
    assert result["token_in"] == "ETH"
    assert result["token_out"] == "USDC"
    assert result["amount_in"] == 1.0

# =====================================
# ENSTool Tests
# =====================================

def test_ens_tool_initialization():
    """Test ENSTool initialization."""
    connection_tool = MagicMock()
    
    tool = ENSTool(connection_tool)
    
    assert tool.name == "ens"
    assert tool.description is not None
    assert tool.connection_tool == connection_tool

def test_ens_tool_missing_parameters():
    """Test ENSTool execute method with missing parameters."""
    connection_tool = MagicMock()
    
    tool = ENSTool(connection_tool)
    
    # Test missing name for resolve action
    result = tool._execute({
        "action": "resolve"
    })
    assert "error" in result
    assert "name" in result["error"]
    
    # Test missing address for lookup action
    result = tool._execute({
        "action": "lookup"
    })
    assert "error" in result
    assert "address" in result["error"]

@patch("anus.web3.tools.ENSTool._resolve_name")
def test_ens_tool_resolve(mock_resolve):
    """Test ENSTool execute method with resolve action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    mock_resolve.return_value = {
        "name": TEST_ENS_NAME,
        "address": TEST_ADDRESS
    }
    
    tool = ENSTool(connection_tool)
    
    result = tool._execute({
        "action": "resolve",
        "name": TEST_ENS_NAME
    })
    
    assert "address" in result
    assert result["name"] == TEST_ENS_NAME
    assert result["address"] == TEST_ADDRESS

@patch("anus.web3.tools.ENSTool._lookup_address")
def test_ens_tool_lookup(mock_lookup):
    """Test ENSTool execute method with lookup action."""
    connection_tool = MagicMock()
    connection_tool._execute.return_value = {"status": "connected"}
    connection_tool._connections = {
        "ethereum": MagicMock()
    }
    
    mock_lookup.return_value = {
        "address": TEST_ADDRESS,
        "name": TEST_ENS_NAME
    }
    
    tool = ENSTool(connection_tool)
    
    result = tool._execute({
        "action": "lookup",
        "address": TEST_ADDRESS
    })
    
    assert "name" in result
    assert result["address"] == TEST_ADDRESS
    assert result["name"] == TEST_ENS_NAME

# =====================================
# IPFSTool Tests
# =====================================

def test_ipfs_tool_initialization():
    """Test IPFSTool initialization."""
    config = {"ipfs": {"gateway": "https://ipfs.io/ipfs/"}}
    
    tool = IPFSTool(config)
    
    assert tool.name == "ipfs"
    assert tool.description is not None
    assert tool.config == config

def test_ipfs_tool_missing_parameters():
    """Test IPFSTool execute method with missing parameters."""
    tool = IPFSTool()
    
    # Test missing cid for get action
    result = tool._execute({
        "action": "get"
    })
    assert "error" in result
    assert "cid" in result["error"]
    
    # Test missing data for add action
    result = tool._execute({
        "action": "add"
    })
    assert "error" in result
    assert "data" in result["error"]
    
    # Test missing cid for pin action
    result = tool._execute({
        "action": "pin"
    })
    assert "error" in result
    assert "cid" in result["error"]

@patch("anus.web3.tools.requests.get")
def test_ipfs_tool_get(mock_requests_get):
    """Test IPFSTool execute method with get action."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.return_value = {"name": "Test Content", "description": "Test Description"}
    mock_response.content = b'{"name":"Test Content","description":"Test Description"}'
    mock_requests_get.return_value = mock_response
    
    tool = IPFSTool()
    tool._client = "gateway"  # Use gateway mode
    
    result = tool._execute({
        "action": "get",
        "cid": TEST_IPFS_CID
    })
    
    assert "content" in result
    assert result["content_type"] == "application/json"
    assert result["content"]["name"] == "Test Content"
    assert result["content"]["description"] == "Test Description"

def test_ipfs_tool_get_client():
    """Test IPFSTool _get_client method."""
    tool = IPFSTool()
    
    # Test with no client
    client = tool._get_client()
    assert client == "gateway"  # Fallback to gateway
    
    # Test with existing client
    tool._client = "existing_client"
    client = tool._get_client()
    assert client == "existing_client"
