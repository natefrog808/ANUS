"""
IPFS Utility Functions for Anus AI Web3 Module

This module provides utility functions for working with the InterPlanetary
File System (IPFS), including URI handling, gateway selection, and content 
management.
"""

import re
import time
import json
import requests
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlparse
import concurrent.futures

from anus.utils.logging import get_logger

# Setup logging
logger = get_logger("anus.web3.utils.ipfs")

# =========================
# IPFS URI Utilities
# =========================

def is_ipfs_uri(uri: str) -> bool:
    """Check if a URI is an IPFS URI.
    
    Args:
        uri: The URI to check
        
    Returns:
        True if the URI is an IPFS URI, False otherwise
    """
    if not uri:
        return False
    
    # Common IPFS URI formats
    ipfs_patterns = [
        r'^ipfs://.+$',               # ipfs://CID
        r'^ipfs://ipfs/.+$',          # ipfs://ipfs/CID
        r'^ipfs:/bafybe.+$',          # ipfs:/CID (no double slash)
        r'^/ipfs/.+$',                # /ipfs/CID
        r'^dweb:/ipfs/.+$',           # dweb:/ipfs/CID
        r'^ipns://.+$',               # ipns://name
        r'^ipns:/[^/]+$',             # ipns:/name
        r'^/ipns/.+$',                # /ipns/name
        r'^dweb:/ipns/.+$',           # dweb:/ipns/name
        r'^https?://ipfs.io/ipfs/.+$', # https://ipfs.io/ipfs/CID
        r'^https?://gateway.ipfs.io/ipfs/.+$', # https://gateway.ipfs.io/ipfs/CID
        r'^https?://[^/]+\.mypinata\.cloud/ipfs/.+$',  # https://gateway.pinata.cloud/ipfs/CID
        r'^https?://[^/]+\.infura-ipfs\.io/ipfs/.+$',  # https://ipfs.infura.io/ipfs/CID
        r'^https?://[^/]+/ipfs/.+$',   # https://any-gateway.com/ipfs/CID
    ]
    
    for pattern in ipfs_patterns:
        if re.match(pattern, uri):
            return True
    
    return False

def normalize_ipfs_uri(uri: str) -> Optional[str]:
    """Normalize an IPFS URI to the ipfs://CID format.
    
    Args:
        uri: The URI to normalize
        
    Returns:
        Normalized URI or None if invalid
    """
    if not uri:
        return None
    
    # Extract CID and determine if it's IPFS or IPNS
    is_ipns = False
    cid_match = None
    
    # Pattern matching for common IPFS URI formats
    if uri.startswith('ipfs://'):
        # ipfs://CID or ipfs://ipfs/CID
        if uri.startswith('ipfs://ipfs/'):
            cid_match = uri[12:]
        else:
            cid_match = uri[7:]
    elif uri.startswith('ipfs:/'):
        # ipfs:/CID (no double slash)
        cid_match = uri[6:]
    elif uri.startswith('/ipfs/'):
        # /ipfs/CID
        cid_match = uri[6:]
    elif uri.startswith('dweb:/ipfs/'):
        # dweb:/ipfs/CID
        cid_match = uri[11:]
    elif uri.startswith('ipns://') or uri.startswith('ipns:/') or uri.startswith('/ipns/') or uri.startswith('dweb:/ipns/'):
        # IPNS formats
        is_ipns = True
        if uri.startswith('ipns://'):
            cid_match = uri[7:]
        elif uri.startswith('ipns:/'):
            cid_match = uri[6:]
        elif uri.startswith('/ipns/'):
            cid_match = uri[6:]
        else:  # dweb:/ipns/
            cid_match = uri[11:]
    elif 'ipfs.io/ipfs/' in uri or '/ipfs/' in uri:
        # Gateway URLs: https://ipfs.io/ipfs/CID or any gateway
        parts = uri.split('/ipfs/')
        if len(parts) > 1:
            cid_match = parts[1].split('?')[0].split('#')[0]  # Remove query params and fragments
    elif 'ipfs.io/ipns/' in uri or '/ipns/' in uri:
        # Gateway URLs with IPNS: https://ipfs.io/ipns/name
        is_ipns = True
        parts = uri.split('/ipns/')
        if len(parts) > 1:
            cid_match = parts[1].split('?')[0].split('#')[0]  # Remove query params and fragments
    
    if not cid_match:
        return None
    
    # Clean up CID/name
    cid = cid_match.strip()
    
    # Validate CID for IPFS (simple check - could be more thorough)
    if not is_ipns and not re.match(r'^[a-zA-Z0-9]{46,}$', cid) and not re.match(r'^Qm[a-zA-Z0-9]{44}$', cid) and not re.match(r'^bafy[a-zA-Z0-9]{52}$', cid):
        logger.warning(f"Invalid IPFS CID format: {cid}")
        return None
    
    # Construct normalized URI
    if is_ipns:
        return f"ipns://{cid}"
    else:
        return f"ipfs://{cid}"

def ipfs_uri_to_http(uri: str, gateway: str = "https://ipfs.io/ipfs/") -> Optional[str]:
    """Convert an IPFS URI to an HTTP URL using a gateway.
    
    Args:
        uri: The IPFS URI to convert
        gateway: The IPFS gateway URL to use
        
    Returns:
        HTTP URL or None if invalid
    """
    if not uri:
        return None
    
    # Normalize gateway URL
    if not gateway.endswith('/'):
        gateway = gateway + '/'
    
    # Check if it's already an HTTP URL
    if uri.startswith('http://') or uri.startswith('https://'):
        # Check if it's already using a gateway
        if '/ipfs/' in uri or '/ipns/' in uri:
            return uri
    
    # Try to extract CID and determine if it's IPFS or IPNS
    is_ipns = False
    cid = None
    
    # Normalize URI first
    normalized = normalize_ipfs_uri(uri)
    if not normalized:
        logger.warning(f"Failed to normalize IPFS URI: {uri}")
        return None
    
    # Extract CID from normalized URI
    if normalized.startswith('ipfs://'):
        cid = normalized[7:]
    elif normalized.startswith('ipns://'):
        is_ipns = True
        cid = normalized[7:]
    else:
        return None
    
    # Construct HTTP URL
    if is_ipns:
        # Replace 'ipfs' with 'ipns' in the gateway URL
        gateway_parts = gateway.split('/ipfs/')
        if len(gateway_parts) > 1:
            gateway_base = gateway_parts[0]
            http_url = f"{gateway_base}/ipns/{cid}"
        else:
            # If gateway doesn't have /ipfs/ in the URL, just append /ipns/
            http_url = f"{gateway}ipns/{cid}"
    else:
        http_url = f"{gateway}{cid}"
    
    return http_url

def extract_ipfs_cid(uri: str) -> Optional[str]:
    """Extract the CID from an IPFS URI.
    
    Args:
        uri: The IPFS URI
        
    Returns:
        CID or None if invalid
    """
    # Normalize URI first
    normalized = normalize_ipfs_uri(uri)
    if not normalized:
        return None
    
    # Extract CID from normalized URI
    if normalized.startswith('ipfs://'):
        return normalized[7:]
    elif normalized.startswith('ipns://'):
        return normalized[7:]
    
    return None

# =========================
# IPFS Gateway Utilities
# =========================

def get_gateway_list() -> List[str]:
    """Get a list of public IPFS gateways.
    
    Returns:
        List of gateway URLs
    """
    # List of reliable public gateways
    return [
        "https://ipfs.io/ipfs/",
        "https://dweb.link/ipfs/",
        "https://gateway.pinata.cloud/ipfs/",
        "https://cloudflare-ipfs.com/ipfs/",
        "https://gateway.ipfs.io/ipfs/",
        "https://ipfs.fleek.co/ipfs/",
        "https://ipfs.infura.io/ipfs/",
        "https://ipfs.best-practice.se/ipfs/",
        "https://ipfs.eth.aragon.network/ipfs/",
        "https://ipfs.cf-ipfs.com/ipfs/"
    ]

def get_ipfs_gateway_url(config: Optional[Dict[str, Any]] = None) -> str:
    """Get the IPFS gateway URL from configuration or use default.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Gateway URL
    """
    default_gateway = "https://ipfs.io/ipfs/"
    
    if not config:
        return default_gateway
    
    # Try to get gateway from config
    gateway = config.get("ipfs", {}).get("gateway", default_gateway)
    
    # Ensure gateway URL ends with /ipfs/
    if not gateway.endswith('/ipfs/'):
        if gateway.endswith('/'):
            gateway = gateway + 'ipfs/'
        else:
            gateway = gateway + '/ipfs/'
    
    return gateway

def test_gateway_speed(gateway: str, test_cid: str = "QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D") -> Optional[float]:
    """Test the speed of an IPFS gateway.
    
    Args:
        gateway: Gateway URL to test
        test_cid: CID to use for testing
        
    Returns:
        Response time in seconds or None if failed
    """
    try:
        # Ensure gateway URL ends with /ipfs/
        if not gateway.endswith('/ipfs/'):
            if gateway.endswith('/'):
                gateway = gateway + 'ipfs/'
            else:
                gateway = gateway + '/ipfs/'
        
        # Test small file retrieval speed
        url = f"{gateway}{test_cid}/readme"
        
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()
        
        if response.status_code == 200:
            return end_time - start_time
        else:
            logger.debug(f"Gateway test failed: {gateway} returned status {response.status_code}")
            return None
    except Exception as e:
        logger.debug(f"Gateway test failed: {gateway} - {str(e)}")
        return None

def select_fastest_gateway(gateways: Optional[List[str]] = None, timeout: int = 10) -> str:
    """Select the fastest IPFS gateway from a list.
    
    Args:
        gateways: List of gateway URLs to test
        timeout: Maximum time to wait for responses
        
    Returns:
        URL of the fastest gateway
    """
    if not gateways:
        gateways = get_gateway_list()
    
    if not gateways:
        return "https://ipfs.io/ipfs/"
    
    # Test gateway speed in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(gateways)) as executor:
        future_to_gateway = {executor.submit(test_gateway_speed, gateway): gateway for gateway in gateways}
        
        # Collect results
        gateway_speeds = {}
        for future in concurrent.futures.as_completed(future_to_gateway, timeout=timeout):
            gateway = future_to_gateway[future]
            try:
                speed = future.result()
                if speed is not None:
                    gateway_speeds[gateway] = speed
            except Exception as e:
                logger.debug(f"Gateway test failed: {gateway} - {str(e)}")
    
    # Select fastest gateway
    if gateway_speeds:
        fastest_gateway = min(gateway_speeds.items(), key=lambda x: x[1])[0]
        logger.info(f"Selected fastest gateway: {fastest_gateway} ({gateway_speeds[fastest_gateway]:.3f}s)")
        return fastest_gateway
    
    # Fallback to default if all tests failed
    logger.warning("All gateway tests failed, using default gateway")
    return "https://ipfs.io/ipfs/"

# =========================
# IPFS Content Utilities
# =========================

def fetch_ipfs_content(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """Fetch content from IPFS.
    
    Args:
        uri: IPFS URI or HTTP URL
        gateway: Optional gateway URL to use
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with content and metadata
    """
    try:
        # Get CID and path
        normalized = normalize_ipfs_uri(uri)
        if not normalized:
            return {
                "error": f"Invalid IPFS URI: {uri}",
                "uri": uri
            }
        
        # Select gateway
        if not gateway:
            gateway = get_ipfs_gateway_url()
        
        # Convert to HTTP URL
        http_url = ipfs_uri_to_http(normalized, gateway)
        if not http_url:
            return {
                "error": f"Failed to convert IPFS URI to HTTP URL: {uri}",
                "uri": uri
            }
        
        # Fetch content
        response = requests.get(http_url, timeout=timeout)
        
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch content: HTTP {response.status_code}",
                "uri": uri,
                "http_url": http_url
            }
        
        # Get content type
        content_type = response.headers.get("content-type", "application/octet-stream")
        
        # Process content based on type
        content = None
        if "application/json" in content_type:
            try:
                content = response.json()
            except ValueError:
                content = response.text
                content_type = "text/plain"
        elif content_type.startswith("text/"):
            content = response.text
        else:
            # Binary content - just return info
            content = f"[Binary data: {len(response.content)} bytes]"
        
        return {
            "uri": uri,
            "http_url": http_url,
            "content_type": content_type,
            "content": content,
            "size": len(response.content),
            "headers": dict(response.headers)
        }
    except requests.exceptions.Timeout:
        return {
            "error": f"Request timed out after {timeout} seconds",
            "uri": uri
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch content: {str(e)}",
            "uri": uri
        }

def is_ipfs_directory(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> bool:
    """Check if an IPFS URI points to a directory.
    
    Args:
        uri: IPFS URI
        gateway: Optional gateway URL to use
        timeout: Request timeout in seconds
        
    Returns:
        True if the URI points to a directory, False otherwise
    """
    try:
        # Convert to HTTP URL
        http_url = ipfs_uri_to_http(uri, gateway or get_ipfs_gateway_url())
        if not http_url:
            return False
        
        # Check for directory listing
        response = requests.head(http_url, timeout=timeout)
        
        # If it returns a 200 status but no content type or a directory listing content type
        content_type = response.headers.get("content-type", "")
        return response.status_code == 200 and (
            "text/html" in content_type or
            "application/json" in content_type or
            "directory" in content_type
        )
    except Exception as e:
        logger.debug(f"Failed to check if IPFS URI is directory: {str(e)}")
        return False

def list_ipfs_directory(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """List contents of an IPFS directory.
    
    Args:
        uri: IPFS URI
        gateway: Optional gateway URL to use
        timeout: Request timeout in seconds
        
    Returns:
        Directory listing
    """
    try:
        # Convert to HTTP URL
        http_url = ipfs_uri_to_http(uri, gateway or get_ipfs_gateway_url())
        if not http_url:
            return {
                "error": f"Invalid IPFS URI: {uri}",
                "uri": uri
            }
        
        # Fetch directory listing (add ?format=json to get JSON response)
        json_url = f"{http_url}?format=json"
        response = requests.get(json_url, timeout=timeout)
        
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch directory listing: HTTP {response.status_code}",
                "uri": uri,
                "http_url": http_url
            }
        
        # Parse response
        try:
            data = response.json()
            
            # Extract entries
            entries = []
            if "Entries" in data:
                for entry in data["Entries"]:
                    entries.append({
                        "name": entry.get("Name", ""),
                        "size": entry.get("Size", 0),
                        "type": "directory" if entry.get("Type", 0) == 1 else "file",
                        "hash": entry.get("Hash", "")
                    })
            
            return {
                "uri": uri,
                "http_url": http_url,
                "entries": entries,
                "name": data.get("Name", ""),
                "size": data.get("Size", 0),
                "type": "directory"
            }
        except ValueError:
            # Not a JSON response, might be HTML directory listing
            return {
                "error": "Failed to parse directory listing - not in JSON format",
                "uri": uri,
                "http_url": http_url,
                "raw_content": response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            }
    except Exception as e:
        return {
            "error": f"Failed to list directory: {str(e)}",
            "uri": uri
        }

# =========================
# IPFS Metadata Utilities
# =========================

def get_nft_metadata_from_ipfs(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """Get NFT metadata from IPFS.
    
    Args:
        uri: IPFS URI to NFT metadata
        gateway: Optional gateway URL to use
        timeout: Request timeout in seconds
        
    Returns:
        NFT metadata
    """
    # Fetch metadata
    result = fetch_ipfs_content(uri, gateway, timeout)
    
    if "error" in result:
        return result
    
    # Extract and process metadata
    metadata = result.get("content")
    
    if not metadata or not isinstance(metadata, dict):
        return {
            "error": "Invalid NFT metadata format",
            "uri": uri,
            "content": metadata
        }
    
    # Process image URI if present
    if "image" in metadata and isinstance(metadata["image"], str) and is_ipfs_uri(metadata["image"]):
        # Convert image URI to HTTP URL
        metadata["image_url"] = ipfs_uri_to_http(
            metadata["image"], 
            gateway or get_ipfs_gateway_url()
        )
    
    # Process animation URI if present
    if "animation_url" in metadata and isinstance(metadata["animation_url"], str) and is_ipfs_uri(metadata["animation_url"]):
        # Convert animation URI to HTTP URL
        metadata["animation_url_http"] = ipfs_uri_to_http(
            metadata["animation_url"],
            gateway or get_ipfs_gateway_url()
        )
    
    return {
        "uri": uri,
        "http_url": result.get("http_url"),
        "metadata": metadata
    }

def get_image_url_from_metadata(metadata: Dict[str, Any], gateway: Optional[str] = None) -> Optional[str]:
    """Extract image URL from NFT metadata.
    
    Args:
        metadata: NFT metadata
        gateway: Optional gateway URL to use
        
    Returns:
        Image URL or None if not found
    """
    # Check if metadata contains image field
    if not metadata or not isinstance(metadata, dict) or "image" not in metadata:
        return None
    
    image_uri = metadata["image"]
    
    # Check if image is already a HTTP URL
    if isinstance(image_uri, str) and (image_uri.startswith("http://") or image_uri.startswith("https://")):
        return image_uri
    
    # Check if image is an IPFS URI
    if isinstance(image_uri, str) and is_ipfs_uri(image_uri):
        return ipfs_uri_to_http(image_uri, gateway or get_ipfs_gateway_url())
    
    return None

# =========================
# IPFS CID Utilities
# =========================

def is_valid_ipfs_cid(cid: str) -> bool:
    """Check if a string is a valid IPFS CID.
    
    Args:
        cid: The CID to check
        
    Returns:
        True if valid, False otherwise
    """
    if not cid or not isinstance(cid, str):
        return False
    
    # Basic format checks for CIDv0 and CIDv1
    if re.match(r'^Qm[1-9A-HJ-NP-Za-km-z]{44}, cid):  # CIDv0 (base58btc multihash)
        return True
    elif re.match(r'^bafy[a-zA-Z0-9]{52}, cid):  # CIDv1 (base32 - most common prefix)
        return True
    elif re.match(r'^[a-zA-Z0-9]{46,}, cid):  # Other potential CID formats
        # This is a very permissive check, could be improved
        return True
    
    return False

def convert_cid_version(cid: str, target_version: int = 1, target_base: str = 'base32') -> Optional[str]:
    """Convert between CID versions.
    
    Args:
        cid: The CID to convert
        target_version: Target CID version (0 or 1)
        target_base: Target base encoding for CIDv1 ('base32', 'base58btc', etc.)
        
    Returns:
        Converted CID or None if conversion failed
    """
    try:
        # Try to import cid module from multicodec if available
        try:
            from multicodec import CID
            
            # Parse CID
            cid_obj = CID.decode(cid)
            
            if target_version == 0:
                if cid_obj.version == 0:
                    return cid  # Already CIDv0
                elif cid_obj.codec == 'dag-pb':  # Only dag-pb can be represented as CIDv0
                    return cid_obj.to_v0().encode('base58btc')
                else:
                    logger.warning(f"Cannot convert to CIDv0: codec {cid_obj.codec} not supported")
                    return None
            else:  # target_version == 1
                if cid_obj.version == 1 and cid_obj.encoding == target_base:
                    return cid  # Already CIDv1 with target base
                else:
                    return cid_obj.to_v1().encode(target_base)
        except ImportError:
            # Fall back to simpler approach without multicodec
            if target_version == 1 and cid.startswith('Qm'):
                # Basic CIDv0 to CIDv1 conversion (limited functionality)
                # In a real implementation, use proper libraries
                logger.warning("Using fallback CID conversion - limited functionality")
                return f"bafybeih{cid[2:].lower()}"
            elif target_version == 0 and cid.startswith('bafy'):
                # Basic CIDv1 to CIDv0 conversion (limited functionality)
                # In a real implementation, use proper libraries
                logger.warning("Using fallback CID conversion - limited functionality")
                return f"Qm{cid[4:].upper()}"
            else:
                return cid  # Return as-is if conversion not supported
    except Exception as e:
        logger.error(f"CID conversion failed: {str(e)}")
        return None

def get_cid_prefix(cid: str) -> Optional[str]:
    """Get the codec prefix from a CID.
    
    Args:
        cid: The CID
        
    Returns:
        Codec prefix or None if invalid
    """
    if not is_valid_ipfs_cid(cid):
        return None
    
    # Extract prefix based on CID version
    if cid.startswith('Qm'):
        return 'dag-pb'  # CIDv0 is always dag-pb
    elif cid.startswith('bafy'):
        return 'dag-pb'  # Most common, but this is a simplification
    elif cid.startswith('bafk'):
        return 'raw'
    elif cid.startswith('bafyb'):
        return 'identity'
    else:
        return None  # Unknown prefix

# =========================
# IPFS Pinning Service Utilities
# =========================

def pin_to_pinata(api_key: str, api_secret: str, cid: str) -> Dict[str, Any]:
    """Pin content to Pinata pinning service.
    
    Args:
        api_key: Pinata API key
        api_secret: Pinata API secret
        cid: Content ID to pin
        
    Returns:
        Pinning result
    """
    try:
        # Pinata API endpoint
        url = "https://api.pinata.cloud/pinning/pinByHash"
        
        # Request headers
        headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": api_secret,
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "hashToPin": cid,
            "pinataMetadata": {
                "name": f"AnusAI-Pinned-{cid[:10]}"
            }
        }
        
        # Make request
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return {
                "success": True,
                "cid": cid,
                "provider": "pinata",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "cid": cid,
                "provider": "pinata",
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        logger.error(f"Pinata pinning failed: {str(e)}")
        return {
            "success": False,
            "cid": cid,
            "provider": "pinata",
            "error": str(e)
        }

def pin_to_web3_storage(api_token: str, cid: str) -> Dict[str, Any]:
    """Pin content to Web3.Storage pinning service.
    
    Args:
        api_token: Web3.Storage API token
        cid: Content ID to pin
        
    Returns:
        Pinning result
    """
    try:
        # Web3.Storage API endpoint for pinning
        url = f"https://api.web3.storage/pins/{cid}"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "name": f"AnusAI-Pinned-{cid[:10]}"
        }
        
        # Make request (PUT to create a new pin)
        response = requests.put(url, json=payload, headers=headers)
        
        if response.status_code in (200, 201, 202):
            return {
                "success": True,
                "cid": cid,
                "provider": "web3.storage",
                "response": response.json() if response.text else {}
            }
        else:
            return {
                "success": False,
                "cid": cid,
                "provider": "web3.storage",
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        logger.error(f"Web3.Storage pinning failed: {str(e)}")
        return {
            "success": False,
            "cid": cid,
            "provider": "web3.storage",
            "error": str(e)
        }

def check_pin_status(cid: str, provider: str, api_key: str) -> Dict[str, Any]:
    """Check pinning status for a CID.
    
    Args:
        cid: Content ID to check
        provider: Pinning service provider ("pinata", "web3.storage", etc.)
        api_key: API key for the pinning service
        
    Returns:
        Pin status
    """
    try:
        if provider.lower() == "pinata":
            # Pinata API endpoint
            url = "https://api.pinata.cloud/pinning/pinJobs"
            
            # Request headers
            headers = {
                "pinata_api_key": api_key,
                # Assuming api_key is a composite "key:secret" string
                "pinata_secret_api_key": api_key.split(":")[1] if ":" in api_key else "",
            }
            
            # Make request
            response = requests.get(
                url,
                headers=headers,
                params={"hashToPin": cid}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Find matching pin job
                for job in data.get("rows", []):
                    if job.get("ipfs_pin_hash") == cid:
                        return {
                            "cid": cid,
                            "provider": "pinata",
                            "status": job.get("status"),
                            "created": job.get("created_at")
                        }
                
                return {
                    "cid": cid,
                    "provider": "pinata",
                    "status": "not_found"
                }
            else:
                return {
                    "cid": cid,
                    "provider": "pinata",
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        elif provider.lower() == "web3.storage":
            # Web3.Storage API endpoint
            url = f"https://api.web3.storage/pins/{cid}"
            
            # Request headers
            headers = {
                "Authorization": f"Bearer {api_key}",
            }
            
            # Make request
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "cid": cid,
                    "provider": "web3.storage",
                    "status": data.get("status"),
                    "created": data.get("created")
                }
            elif response.status_code == 404:
                return {
                    "cid": cid,
                    "provider": "web3.storage",
                    "status": "not_found"
                }
            else:
                return {
                    "cid": cid,
                    "provider": "web3.storage",
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        else:
            return {
                "cid": cid,
                "provider": provider,
                "status": "error",
                "error": f"Unsupported provider: {provider}"
            }
    except Exception as e:
        logger.error(f"Pin status check failed: {str(e)}")
        return {
            "cid": cid,
            "provider": provider,
            "status": "error",
            "error": str(e)
        }

# =========================
# IPFS File Utilities
# =========================

def calculate_ipfs_file_cid(file_content: bytes) -> Optional[str]:
    """Calculate the IPFS CID for a file.
    
    Args:
        file_content: File content as bytes
        
    Returns:
        CID or None if calculation failed
    """
    try:
        # Try to import the necessary libraries
        try:
            import multihash
            import multibase
            
            # Calculate SHA-256 hash of the content
            import hashlib
            digest = hashlib.sha256(file_content).digest()
            
            # Create multihash (SHA-256 function code = 0x12)
            mh = multihash.encode(digest, 0x12)
            
            # Encode as multibase (base32)
            mb = multibase.encode('base32', mh)
            
            # Convert to CIDv1
            return f"bafybie{mb[1:].decode('utf-8')}"
        except ImportError:
            # Fallback using IPFS HTTP API if available
            try:
                import requests
                import tempfile
                
                # Create temporary file
                with tempfile.NamedTemporaryFile() as tmp:
                    tmp.write(file_content)
                    tmp.flush()
                    
                    # Use IPFS HTTP API to add file
                    response = requests.post(
                        'http://127.0.0.1:5001/api/v0/add',
                        files={'file': open(tmp.name, 'rb')}
                    )
                    
                    if response.status_code == 200:
                        return response.json()['Hash']
                    else:
                        logger.error(f"IPFS HTTP API error: {response.text}")
                        return None
            except Exception as e:
                logger.error(f"IPFS HTTP API failed: {str(e)}")
                return None
    except Exception as e:
        logger.error(f"CID calculation failed: {str(e)}")
        return None

def split_ipfs_path(path: str) -> Tuple[str, str]:
    """Split an IPFS path into CID and subpath.
    
    Args:
        path: IPFS path
        
    Returns:
        Tuple of (cid, subpath)
    """
    # Normalize path
    if path.startswith('ipfs://'):
        path = path[7:]
    elif path.startswith('/ipfs/'):
        path = path[6:]
    
    # Split into CID and subpath
    parts = path.split('/', 1)
    cid = parts[0]
    subpath = parts[1] if len(parts) > 1 else ''
    
    return (cid, subpath)

def join_ipfs_path(cid: str, subpath: str) -> str:
    """Join a CID and subpath into an IPFS path.
    
    Args:
        cid: CID
        subpath: Subpath
        
    Returns:
        IPFS path
    """
    # Clean up inputs
    cid = cid.strip()
    subpath = subpath.strip().lstrip('/')
    
    # Join parts
    if subpath:
        return f"ipfs://{cid}/{subpath}"
    else:
        return f"ipfs://{cid}"
