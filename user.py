import asyncio
import json
import os
import timeit

from datetime import datetime, timedelta

import didkit

from reviewer import Reviewer
from transferor import Transferor
from provider import Provider
from ruleset import Decision

from fileoper import file_exists, write_text_file, get_signed_name, get_signed_vp
from simplevdr import user_valid


class User:
    """User representing an user who has an unique DID and can init Transfer Request."""

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)

    def sign_self_vp(self, vcfile: str, outvpfile: str):
        asyncio.run(self.do_sign_self_vp(vcfile, outvpfile))

    async def do_sign_self_vp(self, vcfile: str, outfile: str):
        """Sign a verification presentation. vcfile: user VC. transfile: transfer VC."""
        # verifiableCredential
        with open(vcfile, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()

        verification_method = await didkit.key_to_verification_method("key", self.key)
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=2)

        # didkit-python-main\tests\test_main.py
        presentation1 = {
            "id": "http://example.org/credentials/req",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiablePresentation"],
            "holder": self.did,
            "verifiableCredential": [jo],
        }

        didkit_options = {
            "proofPurpose": "authentication",
            "verificationMethod": verification_method,
        }

        purified = str(presentation1).replace("'", '"')

        signed_presentation = await didkit.issue_presentation(
            purified, str(didkit_options).replace("'", '"'), self.key
        )
        write_text_file(outfile, signed_presentation)


def do_transfer(content: str):
    runner = Transferor()
    runner.run(content)


def authorize_user(user_name: str) -> bool:
    """User authorization:
    1. A user signs a VP about his VC
    2. The user ask provider to check the VP
    """
    key_file = user_name + ".key"
    if not file_exists(key_file):
        print(f"Key for {user_name} not found!")
        return False
    actor = User(key_file)
    print("User: " + actor.did)

    trans_vc_signed_vp = user_name + "_signed_vp.json"
    actor.sign_self_vp(user_name + ".json", trans_vc_signed_vp)
    return True


class CaseGroup:
    """Count the number of each decision."""

    group_id: int

    def __init__(self, id: int):
        self.group_id = id
        self.decisions = []

    def add_decision(self, dec: Decision):
        self.decisions.append(dec)

    def print_result(self):
        allow = 0
        reject = 0
        tbd = 0
        risk = 0
        unknown = 0
        for dec in self.decisions:
            match dec:
                case Decision.GO:
                    allow = allow + 1
                case Decision.REJECT:
                    reject = reject + 1
                case Decision.RISK:
                    risk = risk + 1
                case Decision.TBD:
                    tbd = tbd + 1
                case _:
                    unknown = unknown + 1

        print(
            f"Group {self.group_id}: GO: {allow}, Reject: {reject}, TBD: {tbd}, Risk: {risk}, Unknown: {unknown}"
        )


class CaseGroups:
    def __init__(self):
        self.groups = []
        for i in range(1, 5):
            self.groups.append(CaseGroup(i))  # 1,2,3,4
        print(f"INFO: Total {len(self.groups)} groups.")

    def add_decision(self, case_id: int, dec: Decision):
        md = int(case_id / 10)
        # print(f"DBG: Group {md} for ID: {case_id}")
        if (md >= 1) and (md <= 4):
            self.groups[md - 1].add_decision(dec)
        else:
            print(f"WARN: Unknown id: {case_id} for {dec}!")

    def print_result(self):
        for g in self.groups:
            g.print_result()


OUT_PATH = "./VCs"


def check_all_files():
    revw = Reviewer("user4.key")

    directory_path = OUT_PATH
    files = os.listdir(directory_path)
    for a_file in files:
        combined = os.path.join(directory_path, a_file)
        if os.path.isfile(combined):
            should_allow = revw.check_rules(combined)
            print(f"Result {should_allow} for {a_file}")
        else:
            print(f"INFO: {combined} is not exist!")


def transborder_multi():
    """A demo transfer:
    1. A user signs a VP about his VC
    2. The user ask provider to check the VP
    3. Provider checks the user's VP;
    4. If valid, starts the transborder request;
    """
    authorize_user("user1")

    prov = Provider("user3.key")

    # Check user
    is_valid = prov.verify_vp_file("user1_signed_vp.json")
    if is_valid is False:
        return

    t0 = timeit.default_timer()
    # Pre-defined requests (10 reqs)
    prov.create_requests_for_verify(
        "user3", "user1", approver1="user4", outpath=OUT_PATH
    )
    t1 = timeit.default_timer()
    elapsed_time = round((t1 - t0) * 10**6, 3)
    print(f"Elapsed time of VC creation: {elapsed_time} µs")

    # Random generated requests
    prov.generate_operation_vcs(40, OUT_PATH)

    revw = Reviewer("user4.key")
    cg = CaseGroups()

    t2 = timeit.default_timer()
    for i in range(10, 50):
        cur_path = os.path.join(OUT_PATH, "rnd" + str(i) + ".json")
        if os.path.isfile(cur_path):
            should_allow = revw.check_rules(cur_path)
            cg.add_decision(i, should_allow)
            print(f"Result {should_allow} for {cur_path}")
        else:
            print(f"INFO: {cur_path} is not exist!")

    t3 = timeit.default_timer()
    # calculate elapsed time and print
    elapsed_time = round((t3 - t2) * 10**6, 3)
    print(f"Elapsed time of Rules check: {elapsed_time} µs")

    cg.print_result()


def tranborder_usecase(trans_vc: str):
    cur_user = "user1"
    if not authorize_user(cur_user):
        return

    if not user_valid(cur_user):
        print(f"WARN: User {cur_user} is expired!")
        return

    prov = Provider("user3.key")

    # Check user
    is_valid = prov.verify_vp_file(cur_user + "_signed_vp.json")
    if not is_valid:
        print(f"WARN: User {cur_user} is invalid!")
        return

    trans_vc_file = trans_vc
    trans_vc_signed = get_signed_name(trans_vc_file)  # "trans1024signed.json"
    trans_vc_signed_vp = get_signed_vp(trans_vc_signed)  # "trans1024signed_vp.json"

    revw = Reviewer("user4.key")

    should_allow = revw.check_rules(trans_vc_file)
    if should_allow != Decision.GO:
        return

    revw.sign_file(trans_vc_file, trans_vc_signed)
    print(f"Signed VC file: {trans_vc_signed}")
    revw.sign_transborder_vp("user4.json", trans_vc_signed, trans_vc_signed_vp)
    print(f"Signed VP file: {trans_vc_signed_vp}")

    it_person = Transferor()
    it_person.do_transfer(trans_vc_signed_vp)


def main():
    """Entrance"""
    tranborder_usecase("trans_eu_demo.json")
    tranborder_usecase("trans_eu_demo2.json")


if __name__ == "__main__":
    main()
