import hashlib
import json

def sign_data(data, private_key):
    """
    Signs data with a private key.
    In a real implementation, this would use a proper cryptographic library.
    """
    if not isinstance(data, str):
        data = json.dumps(data, sort_keys=True)

    signer = hashlib.sha256()
    signer.update(private_key.encode('utf-8'))
    signer.update(data.encode('utf-8'))
    return signer.hexdigest()

def verify_signature(data, signature, public_key):
    """
    Verifies a signature with a public key.
    In a real implementation, this would use a proper cryptographic library.
    """
    expected_signature = sign_data(data, public_key) # Using public key as private key for simplicity
    return signature == expected_signature

if __name__ == "__main__":
    private_key = "my-secret-key"
    data_to_sign = {"message": "hello"}

    signature = sign_data(data_to_sign, private_key)
    print(f"Signature: {signature}")

    is_valid = verify_signature(data_to_sign, signature, private_key)
    print(f"Signature is valid: {is_valid}")
