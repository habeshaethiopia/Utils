from cryptography.fernet import Fernet
import logging
from typing import Union
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CryptoError(Exception):
    """Custom exception for cryptography-related errors"""
    pass

def generate_key() -> bytes:
    """
    Generates a new Fernet encryption key.
    
    Returns:
        bytes: A new encryption key
    
    Raises:
        CryptoError: If key generation fails
    """
    try:
        return Fernet.generate_key()
    except Exception as e:
        logger.error(f"Failed to generate key: {str(e)}")
        raise CryptoError(f"Key generation failed: {str(e)}")

def encode_data(data: str, key: Union[str, bytes]) -> str:
    """
    Encrypts the data using the provided key.

    Args:
        data: The data to encode
        key: The symmetric key used for encryption (bytes or base64 string)

    Returns:
        str: The encrypted data in URL-safe base64 encoding

    Raises:
        CryptoError: If encryption fails
        ValueError: If input validation fails
    """
    if not data or not key:
        raise ValueError("Data and key must not be empty")

    try:
        # Convert key to bytes if it's a string
        key_bytes = key if isinstance(key, bytes) else key.encode()
        
        # Validate key format
        try:
            base64.b64decode(key_bytes)
        except Exception:
            raise ValueError("Invalid key format")

        fernet = Fernet(key_bytes)
        encoded_data = fernet.encrypt(data.encode())
        return encoded_data.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise CryptoError(f"Encryption failed: {str(e)}")

def decode_data(encoded_data: str, key: Union[str, bytes]) -> str:
    """
    Decrypts the encoded data using the provided key.

    Args:
        encoded_data: The encrypted data to decode
        key: The symmetric key used for decryption (bytes or base64 string)

    Returns:
        str: The original, decoded data

    Raises:
        CryptoError: If decryption fails
        ValueError: If input validation fails
    """
    if not encoded_data or not key:
        raise ValueError("Encoded data and key must not be empty")

    try:
        # Convert key to bytes if it's a string
        key_bytes = key if isinstance(key, bytes) else key.encode()
        
        # Validate key format
        try:
            base64.b64decode(key_bytes)
        except Exception:
            raise ValueError("Invalid key format")

        fernet = Fernet(key_bytes)
        decoded_data = fernet.decrypt(encoded_data.encode())
        return decoded_data.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise CryptoError(f"Decryption failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Generate a key (only once) and store it securely
        key = generate_key()
        logger.info(f"Generated new encryption key: {key.decode()}")

        # Encrypt sensitive data
        api_endpoint = "https://api.example.com"
        secret_key = "super_secret_key"
        
        encoded_endpoint = encode_data(api_endpoint, key)
        encoded_secret = encode_data(secret_key, key)
        logger.info("Successfully encoded sensitive data")
        
        # Decrypt sensitive data
        decoded_endpoint = decode_data(encoded_endpoint, key)
        decoded_secret = decode_data(encoded_secret, key)
        logger.info("Successfully decoded sensitive data")
        
        # Verify results
        assert decoded_endpoint == api_endpoint
        assert decoded_secret == secret_key
        logger.info("Encryption/decryption verification successful")
        
    except (CryptoError, ValueError) as e:
        logger.error(f"Error during encryption/decryption: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
