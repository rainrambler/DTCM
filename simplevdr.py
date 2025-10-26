import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from fileoper import file_exists, read_text_file
from datetime import datetime


@dataclass
class Organization:
    name: str
    type: str


@dataclass
class CredentialSubject:
    id: str
    context: List[Dict[str, str]]
    organization: Organization
    userName: str


@dataclass
class Proof:
    type: str
    proofPurpose: str
    verificationMethod: str
    created: str
    jws: str


@dataclass
class UserProps:
    context: List[str]
    id: str
    type: List[str]
    credentialSubject: CredentialSubject
    issuer: str
    issuanceDate: str
    proof: Proof
    expirationDate: str


def json_to_user(json_str: str) -> UserProps:
    data = json.loads(json_str)

    # prase credentialSubject
    cs_data = data["credentialSubject"]
    organization = Organization(
        name=cs_data["organization"]["name"], type=cs_data["organization"]["type"]
    )

    credential_subject = CredentialSubject(
        id=cs_data["id"],
        context=cs_data["@context"],
        organization=organization,
        userName=cs_data["userName"],
    )

    # prase proof
    proof_data = data["proof"]
    proof = Proof(
        type=proof_data["type"],
        proofPurpose=proof_data["proofPurpose"],
        verificationMethod=proof_data["verificationMethod"],
        created=proof_data["created"],
        jws=proof_data["jws"],
    )

    # create an UserProps object
    user = UserProps(
        context=data["@context"],
        id=data["id"],
        type=data["type"],
        credentialSubject=credential_subject,
        issuer=data["issuer"],
        issuanceDate=data["issuanceDate"],
        proof=proof,
        expirationDate=data["expirationDate"],
    )

    return user


def parse_iso_date_advanced(date_string):
    if date_string.endswith("Z"):
        date_string = date_string.replace("Z", "+00:00")
    return datetime.fromisoformat(date_string)


def datetime_valid(date_string: str) -> bool:
    date_object = parse_iso_date_advanced(date_string)
    return date_object.timestamp() > datetime.now().timestamp()


class SimpleVDR:
    def __init__(self, filename):
        self.user_prop = {}
        with open(filename, "r") as f:
            self.all_users = json.load(f)
            f.close()

        self.load_user_props()
        print(f"Total {len(self.all_users)} users loaded.")

    def find_user(self, userkey: str):
        if len(userkey) == 0:
            return ""
        if userkey in self.all_users:
            return self.all_users[userkey]
        return None

    def load_user_props(self):
        for one_user in self.all_users:
            prop_file = one_user + ".json"
            self.load_prop_file(one_user, prop_file)

    def load_prop_file(self, user: str, file_name: str):
        if not file_exists(file_name):
            print(f"WARN: Cannot find file {file_name}!")
            return

        content = read_text_file(file_name)
        prop = json_to_user(content)
        self.user_prop[user] = prop

    def is_user_valid(self, user: str) -> bool:
        prop = self.user_prop[user]
        if not prop:
            return False
        return datetime_valid(prop.expirationDate)


a_vdr = SimpleVDR("allusers.json")


def get_user_id(username: str) -> str:
    didval = a_vdr.find_user(username)
    if None is didval:
        return ""
    return didval


def user_valid(user: str) -> bool:
    return a_vdr.is_user_valid(user)
