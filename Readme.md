# DTCM: Data Trans-Border Compliance Management Framework

![License](https://img.shields.io/badge/License-Research-blue.svg)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-orange)

This repository contains the reference implementation for the research paper:

**"A Framework for Data Trans-Border Compliance Management Based on Customized Verifiable Credentials"**

## 🚀 Overview

DTCM is a novel framework that applies W3C Decentralized Identifiers (DIDs) and Verifiable Credentials (VCs) to address data trans-border compliance challenges. The project demonstrates how blockchain-based identity standards can be adapted for managing cross-border data transfers in regulatory environments.

## ✨ Key Innovations

- **Customized Verifiable Credentials**: Extends W3C VC standard with domain-specific attributes for data compliance
- **DID-based Trust Framework**: Implements decentralized identity for compliance authorities and data processors
- **Cross-Border Compliance Automation**: Streamlines compliance verification through verifiable credentials
- **Privacy-Preserving Verification**: Enables selective disclosure of compliance information

## 🛠️ Installation & Usage

```bash
# Clone the repository
git clone https://github.com/your-username/dtcm.git
cd dtcm

# Install dependencies (install uv first)
uv sync

# Create demo admin (The Issuer)
didkit generate-ed25519-key key.jwk

# Create Demo Users
uv run ./users.py

# Start demo transfers
uv run ./user.py

```

## ⚠️ Important Notice

This implementation is provided as reference code for academic research purposes only:

- 🎓 Research Focus: Intended to demonstrate concepts from the accompanying paper

- 🔬 Proof of Concept: Not production-ready or security-audited

- 📝 Academic Use: Suitable for research, experimentation, and educational purposes

- 🚫 Not for Production: NOT recommended for commercial use or production environments

## 📚 Related Publication

For theoretical foundations, technical details, and experimental results, please refer to our research paper:

"A Framework for Data Trans-Border Compliance Management Based on Customized Verifiable Credentials"
Authors: Mudi Xu, Zhizhong Tan, Anyu Wang, Yan Liu, Weiping Deng, Xingxing Yang, Sai Zou, Wenyong Wang

## 🤝 Contributing

As this is a research reference implementation, we welcome:

- Bug reports and fixes

- Documentation improvements

- Research collaborations and discussions

Please open an issue first to discuss substantial changes.

## 📄 License

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE - see the LICENSE file for details.

## 📞 Contact

For research-related inquiries:

Email: wanganyu@outlook.com

Project Link: https://github.com/rainrambler/dtcm
