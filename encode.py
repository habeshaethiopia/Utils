from cryptography.fernet import Fernet

# Generate a key only once, and store it securely
# Use Fernet.generate_key() to create one
# In a secure environment, this key should be securely stored and retrieved
# For demonstration, we're generating a new key each time

def generate_key():
    return Fernet.generate_key()

def encode_data(data, key):
    """
    Encrypts the data using the provided key.

    Args:
    - data (str): The data (API endpoint or secret key) to encode.
    - key (bytes): The symmetric key used for encryption.

    Returns:
    - str: The encrypted data in URL-safe base64 encoding.
    """
    fernet = Fernet(key)
    encoded_data = fernet.encrypt(data.encode())
    return encoded_data.decode()  # return as a string for easy storage

def decode_data(encoded_data, key):
    """
    Decrypts the encoded data using the provided key.

    Args:
    - encoded_data (str): The encrypted data to decode.
    - key (bytes): The symmetric key used for decryption.

    Returns:
    - str: The original, decoded data.
    """
    fernet = Fernet(key)
    decoded_data = fernet.decrypt(encoded_data.encode())
    return decoded_data.decode()  # return as a string

# Example usage
if __name__ == "__main__":
    # Generate a key (only once) and store it securely
    key = generate_key()
    print(f"Encryption Key (Keep it safe!): {key.decode()}")

    # Encrypt sensitive data
    api_endpoint = "https://api.example.com"
    secret_key = "super_secret_key"
    
    encoded_endpoint = encode_data(api_endpoint, key)
    encoded_secret = encode_data(secret_key, key)
    print("Encoded API Endpoint:", encoded_endpoint)
    print("Encoded Secret Key:", encoded_secret)

    # Decrypt sensitive data
    decoded_endpoint = decode_data(encoded_endpoint, key)
    decoded_secret = decode_data(encoded_secret, key)
    print("Decoded API Endpoint:", decoded_endpoint)
    print("Decoded Secret Key:", decoded_secret)
