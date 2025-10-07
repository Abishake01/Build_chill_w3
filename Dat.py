from alith.lazai import Client, ProofRequest
from alith.data import encrypt
from alith.data.storage import (
    PinataIPFS,
    UploadOptions,
    GetShareLinkOptions,
    StorageError,
)
from eth_account.messages import encode_defunct
from os import getenv
from dotenv import load_dotenv
load_dotenv()
import asyncio
import requests
import rsa
import aiohttp
from pydantic import BaseModel
from typing import Optional
import hashlib


class ActualPinataUploadResponse(BaseModel):
    id: str
    name: str
    cid: str
    size: int
    number_of_files: int
    mime_type: str
    created_at: str
    updated_at: str
    network: str
    streamable: bool
    # Optional fields that might not be present
    accept_duplicates: Optional[bool] = None
    is_duplicate: Optional[bool] = None
    group_id: Optional[str] = None


class CustomPinataIPFS(PinataIPFS):
    async def upload(self, opts: UploadOptions):
        url = "https://uploads.pinata.cloud/v3/files"

        form = aiohttp.FormData()
        form.add_field("file", opts.data, filename=opts.name, content_type="text/plain")
        form.add_field("network", "public")

        headers = {"Authorization": f"Bearer {opts.token}"}

        try:
            async with self.client.post(url, data=form, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise StorageError(f"Pinata IPFS API error: {error_text}")

                data = await response.json()
                # Use the actual response structure instead of the broken model
                pinata_response = ActualPinataUploadResponse(**data["data"])

                from alith.data.storage import FileMetadata
                return FileMetadata(
                    id=pinata_response.cid,
                    name=pinata_response.name,
                    size=pinata_response.size,
                    modified_time=pinata_response.updated_at,
                )
        except aiohttp.ClientError as e:
            raise StorageError(f"Network error: {str(e)}") from e


async def main():
    client = Client(private_key=getenv("PRIVATE_KEY"))
    ipfs = CustomPinataIPFS()  # Use our custom implementation
    try:
        # 1. Prepare your privacy data and encrypt it
        data_file_name = "my_personal_info.txt"
        
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

        file_hash = hashlib.sha256(privacy_data.encode()).hexdigest()
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
            tx_hash = client.add_file_with_hash(url, file_hash)
            print("Tx Hash:", tx_hash)
            file_id = client.get_file_id_by_url(url)
            print("File ID:", file_id)
        else:
            print(f"File ID: {file_id} (existing, no new transaction)")
        # 4. Request proof in the verified computing node
        client.request_proof(file_id, 100)
        job_id = client.file_job_ids(file_id)[-1]
        job = client.get_job(job_id)
        node_info = client.get_node(job[-1])
        node_url: str = node_info[1]
        pub_key = node_info[-1]
        encryption_key = rsa.encrypt(
            password.encode(),
            rsa.PublicKey.load_pkcs1(pub_key.strip().encode(), format="PEM"),
        ).hex()
        response = requests.post(
            f"{node_url}/proof",
            json=ProofRequest(
                job_id=job_id,
                file_id=file_id,
                file_url=url,
                encryption_key=encryption_key,
                encryption_seed=encryption_seed,
                proof_url=None,
            ).model_dump(),
        )
        if response.status_code == 200:
            print("Proof request sent successfully")
        else:
            print("Failed to send proof request:", response.json())
        # 5. Request DAT reward
        client.request_reward(file_id)
        print("Reward requested for file id", file_id)
    except StorageError as e:
        print(f"Error: {e}")
    except Exception as e:
        raise e
    finally:
        await ipfs.close()


if __name__ == "__main__":
    asyncio.run(main())
