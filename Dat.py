import asyncio
from os import getenv
from dotenv import load_dotenv

import rsa
import hashlib
from eth_account.messages import encode_defunct

from alith.data import encrypt
from alith.data.storage import (
    GetShareLinkOptions,
    PinataIPFS,
    StorageError,
    UploadOptions,
)
from alith.lazai import Client
load_dotenv()

privacy_data = """
Hey! I’m Abishake, but everyone calls me Abi 👋. 
I’m super passionate about AI, Web3, and Python — especially when it comes to building projects that mix creativity with tech. 
I love working on AI agents, Web3 integrations, and smart apps using Django, React, and Tailwind CSS. 
I mostly build everything solo — from the backend logic to the frontend UI — because I enjoy seeing an idea come alive end to end. 
Apart from coding, I love teaching; every week, I take Python full-stack classes at my college to help juniors learn programming in a simple and fun way. 
I always get excited exploring new tech, whether it’s smart contracts, AI model integration, or voice-based AI systems. 
I like keeping my projects clean, modern, and interactive — with smooth animations and a touch of my own style 😎. 
For me, tech isn’t just about code; it’s about creating something people can actually feel and enjoy using.
"""


async def main():
    private_key = getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable is required")
    client = Client(private_key=private_key)
    ipfs = PinataIPFS()
    try:
        # 1. Prepare your privacy data and encrypt it
        data_file_name = "encrypted_dat3.txt"
        privacy_data_sha256 = hashlib.sha256(privacy_data.encode()).hexdigest()
        encryption_seed = "Sign to retrieve your encryption key"
        message = encode_defunct(text=encryption_seed)
        password = client.wallet.sign_message(message).signature.hex()
        encrypted_data = encrypt(privacy_data.encode(), password)
        # 2. Upload the privacy data to IPFS and get the shared url
        token = getenv("IPFS_JWT", "")
        file_meta = await ipfs.upload(
            UploadOptions(name=data_file_name, data=encrypted_data, token=token)
        )
        url = await ipfs.get_share_link(
            GetShareLinkOptions(token=token, id=file_meta.id)
        )
        # 3. Upload the privacy url to LazAI
        file_id = client.get_file_id_by_url(url)
        if file_id == 0:
            file_id = client.add_file_with_hash(url, privacy_data_sha256)
        print("File ID:", file_id)
        pub_key = client.get_public_key()
        encryption_key = rsa.encrypt(
            password.encode(),
            rsa.PublicKey.load_pkcs1(pub_key.strip().encode(), format="PEM"),
        ).hex()
        client.add_permission_for_file(
            file_id, client.contract_config.data_registry_address, encryption_key
        )
    except StorageError as e:
        print(f"Error: {e}")
    except Exception as e:
        raise e
    finally:
        await ipfs.close()


if __name__ == "__main__":
    asyncio.run(main())