import asyncio
import json
import os
from datetime import datetime

import didkit

import fileoper
from transettings import TranSettings, create_demo_setting, create_setting, random_region, random_datatype, random_reason

from simplevdr import get_user_id


class Provider:
    """Sign user's transborder VC"""

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)
        self.is_valid = False

    def create_requests_for_verify(
        self, sender: str, receiver: str, approver1: str, outpath: str
    ):
        """Pre-defined Verification Set"""
        # Five Allow VCs
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "privacy data",
            "MB",
            "100",
            "Germany",
            "Belgium",
            "business analysis",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "allw1.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "privacy data",
            "person",
            "100,000",
            "Denmark",
            "New Zealand",
            "business analysis",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "allw2.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "privacy data",
            "MB",
            "100",
            "France",
            "South Africa",
            "BCRS ID: XXX",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "allw3.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "personal data",
            "person",
            "500",
            "Vietnam",
            "Belgium",
            "Has local storage on XXX",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "allw4.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "privacy data",
            "person",
            "10,000",
            "Japan",
            "Philippines",
            "business analysis",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "allw5.json"))

        # Three Risk VCs
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "personal data",
            "MB",
            "100",
            "Canada",
            "Russia",
            "business analysis",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "rsk1.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "personal data",
            "person",
            "1000",
            "USA",
            "Russia",
            "user consent",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "rsk2.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "important data",
            "person",
            "7000",
            "China",
            "USA",
            "security assessment No. 35",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "rsk3.json"))

        # Two Deny VCs
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "financial data",
            "persons",
            "1000",
            "India",
            "UK",
            "business analysis",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "rj1.json"))
        settings = create_setting(
            sender,
            receiver,
            approver1,
            "important data",
            "MB",
            "100",
            "China",
            "France",
            "business cooperation with CII",
        )
        self.fill_trans_req(settings, os.path.join(outpath, "rj2.json"))

    def generate_operation_vcs(self, number: int, opath: str):
        """Generate random VCs of specified number."""
        i = 0
        while i < number:
            from_region = random_region()
            to_region = random_region()
            while to_region == from_region:
                to_region = random_region()

            settings = create_setting(
                "user3",
                "user1",
                "user4",
                random_datatype(),
                "MB",
                "500",
                from_region,
                to_region,
                random_reason(),
            )
            self.fill_trans_req(
                settings, os.path.join(opath, "rnd" + str(i + 10) + ".json")
            )
            i = i + 1

    def create_trans_request_demo(self, receiver: str, approver1: str, outfile: str):
        """create a transfer request json file. outfile: transfer json."""

        # sender: str, receiver: str, approver1: str
        send_did = get_user_id(receiver)
        receiver_did = self.did
        approv_did = get_user_id(approver1)
        settings = create_demo_setting(send_did, receiver_did, approv_did)

        self.fill_trans_req(settings, outfile)
        print(f"VC File {outfile} generated.")

    def create_trans_request(self, transets: TranSettings,
                             outfile: str):
        """create a transfer request json file. outfile: transfer json."""

        self.fill_trans_req(transets, outfile)
        print(f"VC File {outfile} generated.")

    def fill_trans_req(self, trans: TranSettings, outfile: str):
        """Fill a verification credential. outfile: transfer VC."""

        issuance_date = datetime.now().replace(microsecond=0)

        credential = {
            "id": "http://example.org/credentials/transborder",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiableCredential", "OperCredential"],
            "issuer": trans.approver,
            "issuanceDate": issuance_date.isoformat() + "Z",
            "expirationDate": trans.expirationTime,
            "credentialSubject": {
                "@context": [
                    {"userName": "https://schema.org/Text"},
                    {"transferTime": "https://schema.org/Text"},
                    {"origArea": "https://schema.org/Text"},
                    {"destArea": "https://schema.org/Text"},
                    {"dataType": "https://schema.org/Text"},
                    {"dataVolume": "https://schema.org/Text"},
                    {"dataUnit": "https://schema.org/Text"},
                    {"dataHash": "https://schema.org/Text"},
                    {"reason": "https://schema.org/Text"},
                    {"approverInfo": "https://schema.org/Text"},
                    {"receiver": "https://schema.org/Text"},
                    {"receiverKey": "https://schema.org/Text"},
                    {"transferId": "https://schema.org/Text"},
                ],
                "id": self.did,
                "userName": trans.senderId,
                "transferTime": trans.expectTime,
                "origArea": trans.origArea,
                "destArea": trans.destArea,
                "dataType": trans.dataType,
                "dataVolume": trans.dataVolume,
                "dataUnit": trans.dataUnit,
                "dataHash": trans.dataHash,
                "reason": trans.reason,
                "approverInfo": trans.approver,
                "receiver": trans.receiverId,
                "receiverKey": trans.receiverKey,
                "transferId": trans.ticketId,
            },
        }

        credstr = json.dumps(credential)
        fileoper.write_text_file(outfile, credstr)

    def verify_vp_file(self, filename) -> bool:
        """Verify a credential presentation. If no error, start a transfer operation."""
        print(f"Verifing {filename}...")

        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()

        jostr = json.dumps(jo)
        asyncio.run(self.verify_vp_content(jostr))

        return self.is_valid

    async def verify_vp_content(self, content: str):
        """Using didkit method to verify VP"""

        result = await didkit.verify_presentation(content, json.dumps({}))

        resobj = json.loads(result)
        if len(resobj["errors"]) == 0:
            self.is_valid = True
        else:
            print("Verification failed!")
            self.is_valid = False
