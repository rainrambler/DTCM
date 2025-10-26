import asyncio
import json
import time
from datetime import datetime, timedelta

import didkit
import fileoper


class Issuer:
    """Issuer representing an issuer who can manage users."""

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)
        self.allusers = {}

    def create_users_batch(self, usernum: int):
        REPEAT_LIMIT = 3
        for i in range(usernum):
            
            username = f"user{i}"
            fname = username + ".key"
            userjson = username + ".json"
            for j in range(REPEAT_LIMIT):
                keyx = didkit.generate_ed25519_key()
                if keyx:
                    fileoper.write_text_file(fname, keyx)
                    asyncio.run(self.sign_a_user(username, keyx, userjson))
                    time.sleep(2)
                    break
                print(f"WARN: Create Key for User {i} Failed. Repeat {j} times.")

        print(f"{usernum} users created.")

    def sign_user(self, username: str, userkey: str, outfile: str):
        asyncio.run(self.sign_a_user(username, userkey, outfile))

    async def sign_a_user(self, username: str, userkey: str, outfile: str):
        user_did = didkit.key_to_did("key", userkey)
        verification_method = await didkit.key_to_verification_method("key", self.key)
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=24)

        credential = {
            "id": "http://example.org/credentials/user",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiableCredential", "UserCredential"],
            "issuer": self.did,
            "issuanceDate": issuance_date.isoformat() + "Z",
            "expirationDate": expiration_date.isoformat() + "Z",
            "credentialSubject": {
                "@context": [
                    {"userName": "https://schema.org/Text"},
                    {"organization": "https://schema.org/Org"},
                ],
                "id": user_did,
                "userName": username,
                "organization": {"type": "No profit", "name": "Example.Org"},
            },
        }

        # add user
        self.allusers[username] = user_did

        didkit_options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod": verification_method,
        }

        signed_credential = await didkit.issue_credential(
            str(credential).replace("'", '"'),
            str(didkit_options).replace("'", '"'),
            self.key,
        )
        fileoper.write_text_file(outfile, signed_credential)

    def save_users(self, outfilename: str):
        """Convert and write JSON object to file"""
        with open(outfilename, "w", encoding="utf-8") as fobj:
            json.dump(self.allusers, fobj)

def create_issuer(key_file: str) -> bool:
    keyx = didkit.generate_ed25519_key()
    if not keyx:
        return False
    fileoper.write_text_file(key_file, keyx)
    return True

def main():
    issuer_file = "issuer.jwk"
    res = create_issuer(issuer_file)
    if not res:
        print(f"WARN: Cannot create key file: {issuer_file} for Issuer!")
        return

    time.sleep(1)

    if not fileoper.file_exists(issuer_file):
        print(f"WARN: Cannot find key file: {issuer_file} for Issuer!")
        return

    issuer = Issuer(issuer_file)
    issuer.create_users_batch(5)

    issuer.save_users("allusers.json")

if __name__ == "__main__":
    main()
