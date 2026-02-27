# did:pqie Method Specification

**Specification Version:** 1.0.0  
**Status:** Draft — Pending W3C DID Method Registry Submission  
**Authors:** Aadhaar KYC System Team (PQIE Research Group)  
**Date:** 2026-02-26  
**Repository:** https://github.com/pqie/did-method-pqie  
**Context URL:** https://pqie.network/ns/did/v1

## Abstract
This paper introduces Post-Quantum Identity Encryption (PQIE), a fully lattice-based security layer for Decentralized Identifiers (DIDs) that encrypts entire DID Documents with Ring-Learning-With-Errors (Ring-LWE) and applies a built-in homomorphic noise filter. The framework is blockchain-agnostic: encrypted identities (or their hashes) can be stored on any key-value ledgers. PQIE is positioned at the intersection of post-quantum cryptography and self-sovereign identity. Where traditional DID methods focus on substituting elliptic-curve keys with lattice signatures, our approach re-thinks the entire trust pipeline—from key material to on-chain storage—by insisting that no part of the DID Document ever travels or rests in plaintext.

## 1. Introduction
Digital identity is rapidly shifting from centralized systems to distributed systems, where users control their own credentials. The W3C Decentralized Identifier (DID) specification decouples identifiers from centralized registries by anchoring them in distributed ledgers. Yet most DID methods still rely on elliptic-curve cryptography—susceptible to quantum attacks. Blockchain provides an immutable substrate for storing identity proofs, but quantum readiness remains an open gap.
Blockchains introduce an append-only ledger where every state transition is cryptographically attested. This immutability is attractive to identity systems because it eliminates single points of compromise. However, the transparency of public chains also magnifies privacy risk: metadata correlation attacks can reveal social graphs or user-credential relationships. 
Self-Sovereign Identity (SSI) combines DIDs and Verifiable Credentials (VCs) to give individuals agency over how their data are shared. Creating a quantum-resistant SSI stack requires post-quantum key generation, end-to-end encryption, and efficient noise management. PQIE addresses these needs while remaining ledger-independent.

## About
PQIE - is a common method for identities that rely on the implementation of the Post-Quantum Identity Encryption (PQIE) framework. The framework is compatible with any key-value ledger and focuses on ensuring maximum privacy and quantum-resistance using Ring-Learning-With-Errors (Ring-LWE) cryptography. The protocol enables users to generate encrypted DID documents with homomorphic noise filtering and lattice signatures.

## 2. PQIE Framework
PQIE’s strategy of encrypting the entire DID Document mitigates this leakage while retaining auditability via on-chain hash pointers. 
From an economic perspective the cost of on-chain bytes matters. Lattice ciphertexts can be bulky, but our homomorphic filtering keeps the encrypted DID payload below 2 kB, which costs low over blockchain operations.

Below each step link it directly to the modules defined in the PQIE architecture (Ring-LWE Engine, PQIE Encryption Layer, Noise-Filtering Layer, Ledger-Agnostic Interface). Each block implementation and functional perspective shown in below table.

| Block | What it does | Minimal implementation detail |
|---|---|---|
| **O:User Interface** | Captures identity data and initiates “Create DID”. | Web form / mobile app sends JSON to a back-end endpoint. |
| **A:Ring-LWE Key Generator** | Produces quantum-safe key pair (pk, sk). | • n = 512<br>• q ≈ 24 577<br>• σ ≈ 4.0<br>calling with keygen(). |
| **A:DID Derivation** | Converts pk into a standards-compliant DID string. | did:pqie: + base58( SHA-256(pk)[:16] ). |
| **A:DID Document Builder** | Assembles JSON-LD doc containing: DID, verification keys, services. | Embed pk under verificationMethod[0]. |
| **A:PQIE Encryptor** | Encrypts the entire DID Document with Ring-LWE KEM. | 1. Generate ephemeral lattice key<br>2. Derive shared secret SS = KEM(pk)<br>3. AES-GCM(SS, DID-JSON) ⇒ ciphertext C. |
| **B:Homomorphic Noise Filter** | Keeps lattice noise small over long sessions. | compute cᵢ’ = (cᵢ mod q/4); set new modulus q←q/4. |
| **B:Post-Quantum Signature** | Signs ciphertext so verifiers know it came from the controller. | Use PQIE Ring-LWE signature, Attach signature. |
| **E:Ledger Writer** | Stores ciphertext on any blockchain. | Either as transaction or as pointer |
| **F:Resolver Plug-in** | Retrieves, decrypts, and verifies. | Fetch on-chain payload P by calling Ledger-Agnostic Interface.<br>Decapsulate and Decrypt clear_doc.<br>Signature Verify.<br>Return plaintext DID. |

*Table 1 — Implementation aspects of each block in architecture*

### 2.1 End‑to‑End Flow
This diagram shows how a fully quantum-safe digital identity is created, stored, and verified using PQIE and Hyperledger Indy. When someone wants a new DID, they start with their personal details and use a special Ring-LWE algorithm to make a key pair. That DID string is then encrypted into a single blob (ciphertext) and noise is filtered out so the encrypted data stays small and fast. This encrypted DID is placed on a ledger. Later, if anyone needs to look up that DID, they fetch the encrypted blob, use the matching public key to decrypt it, and reveal the real DID. On the right side, a simple “Verification API” lets apps request the PQIE module to run those same steps—encrypting and filtering noise on the DID and writing it to an “Identity Ledger.” If extra identity checks are needed, that result goes into an “Application Ledger.” Finally, both ledgers feed into blockchain for governance and auditing.

### 2.2 Key Pair Generation
**E (Input Data)**: The plaintext data is first lifted into the polynomial ring.
**Quantum Security: Ring-LWE Trapdoor Hardness**: Recovering the secret polynomial s from a single “a·s + e” sample is as hard as the Shortest Vector Problem in a family of cyclotomic lattices.
**Apply Number-Theoretic Transform (NTT)**: Converts the polynomial coefficients into the “NTT domain.”
**Security: tanh Activation Applied to Coefficients**: Applies a pointwise tanh function to disrupt any linear patterns in NTT outputs.
**Apply Non-Linear Mapping**: A secondary nonlinear step (e.g., Rounding).
**Security: Ring-LWE Transformation**:
- Public parameter polynomial a(x)
- Secret trapdoor polynomial s(x)
- Error polynomial e(x)
The challenge: given (a(x), c(x) = a(x)·s(x) + e(x) mod q), recover s(x) is believed intractable for both classical and quantum computers.
**Compute LWE Transformation**: c(x)=a(x)⋅s(x) + e(x)
**Quantum Security:** LWE is Hard for Quantum Computers.
**Apply Error Distribution**: The small error polynomial e(x) is sampled from a zero-centered discrete Gaussian distribution (σ ≈ 4).
**Apply Inverse NTT**: Converts from NTT domain back to standard coefficient representation producing the final polynomial ciphertext.

### 2.3 DID & DID Document Construction
The process first converts a user’s personal attributes into a suitable polynomial form and adds a small Gaussian “noise” polynomial to mask the underlying data. It then performs the core Ring-LWE encryption and applies a Number-Theoretic Transform (NTT) to enable efficient polynomial operations and manage noise. A nonlinear tanh activation scrambles any remaining linear structure in the transformed coefficients before generating two cryptographic hash digests that together produce a unique token used as the DID suffix. Next, a JSON-LD DID Document is assembled—including the "id", the "verificationMethod", the "authentication" entry, and a "service" endpoint. Finally, this encrypted DID Document is written to a ledger-agnostic storage layer.

### 2.4 Signature Generation and verification Technical flow
#### 2.4.1 Signature generation
When creating a PQIE signature, we compute a single hash value from the encrypted DID data along with the DID string itself. This hash becomes the “digest” that we will sign. To produce the signature, the signer’s secret key and a fresh small random polynomial “y” are used together. Finally, we compute the response z = y + c·s, where s is our secret key, and apply a lightweight noise-reduction step so that z stays within safe bounds. Anyone knowing the public key can later verify this signature quickly by recomputing A·z − c·pk and checking that its hash matches c.

#### 2.4.2 Verification
Resolvers retrieve the encrypted DID Document, decrypt it with the public key, and verify the signature before releasing attributes.
In the Ring-LWE KEM Decapsulation step, the resolver uses the DID’s stored public key pk to recover the shared secret SS = Decap(pk, kem). The Derive Key node applies an HMAC-based Key Derivation Function to SS, which is then used to decrypt the encrypted DID and retrieve the plaintext JSON-LD DID Document. Next, the resolver computes a digest over clear_doc || kem || ct ensuring the same data originally signed. In the Verify step, it verifies the lattice signature against that digest.

### 2.5 Signing, Encryption & Storage
Starting from a nonce or random seed N, the system first performs an LWE-based randomized signature over the newly generated DID string. Once the DID is signed, the process builds a full JSON-LD DID Document. After assembling the DID Document in JSON form, a ledger-write operation occurs—writing the DID and its encrypted document onto the chosen blockchain via the ledger-agnostic interface, ensuring immutability.

### 2.6 Overall technical flow of PQIE System
(Technical architectural design flow mapping inputs to verification steps via the PQIE module.)

## Method Specific Identifier
The namestring that shall identify this DID method is: `pqie`

A DID that uses this method MUST begin with the following prefix: `did:pqie`

Per the DID specification, this string MUST be in lowercase. The remainder of the DID, after the prefix, is as follows:

The method specific identifier is composed of a primary-hash, secondary-hash, and entropy-suffix according to the core pqie specification.

The identity identifier is deterministically calculated from the citizen attributes via the PQIE pipeline: Hash(Lattice Mapping).

```abnf
pqie-did = "did:pqie:" pqie-specific-idstring
pqie-specific-idstring = pqie-identifier
pqie-identifier = 8HEXDIG ":" 8HEXDIG ":" 8HEXDIG
```

### Example
A valid pqie DID:
```
did:pqie:5135e697:8b7ecf94:a3f21bc0
did:pqie:a1b2c3d4:e5f6g7h8:i9j0k1l2
did:pqie:12345678:90abcdef:1234abcd
```

## DID Document

Example of DID document of regular identity:
```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://pqie.network/ns/did/v1"
  ],
  "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0",
  "verificationMethod": [
    {
      "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0#key-1",
      "type": "PQIE-RingLWE2024",
      "controller": "did:pqie:5135e697:8b7ecf94:a3f21bc0",
      "publicKeyLattice": "AAAA...",
      "latticeParams": { "n": 512, "q": 24593 }
    }
  ],
  "authentication": ["did:pqie:5135e697:8b7ecf94:a3f21bc0#key-1"],
  "service": [{
    "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0#storage",
    "type": "EncryptedDIDService",
    "serviceEndpoint": "https://ipfs.io/ipfs/Qm..."
  }],
  "versionId": "1"
}
```

Example of DID document of on-chain (government controlled) identity:
```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://pqie.network/ns/did/v1",
    "https://w3id.org/security/suites/secp256k1recovery-2020/v2"
  ],
  "id": "did:pqie:11112222:33334444:55556666",
  "verificationMethod": [
    {
      "id": "did:pqie:11112222:33334444:55556666#key-1",
      "type": "PQIE-RingLWE2024",
      "controller": "did:pqie:11112222:33334444:55556666",
      "publicKeyLattice": "BBBB...",
      "latticeParams": { "n": 512, "q": 24593 }
    },
    {
      "id": "did:pqie:11112222:33334444:55556666#government-id",
      "type": "EcdsaSecp256k1RecoveryMethod2020",
      "controller": "did:pqie:11112222:33334444:55556666",
      "blockchainAccountId": "eip155:1:0x123..."
    }
  ],
  "authentication": ["did:pqie:11112222:33334444:55556666#key-1"]
}
```

## JSON-LD Context
The pqie did method uses additional JSON-LD types.

The JSON-LD vocabulary is stored in:

https://pqie.network/ns/did/v1#
Context contains `publicKeyLattice` (Operational key) and `latticeParams` types.

https://schema.iden3.io/core/jsonld/iden3proofs.jsonld
Context contains lattice signature proofs types and some specific credential statuses types used with pqie based identities.


## Basic operations
Each identity has a unique DID that is determined by the initial identity state (derived from the base identity attributes). This identifier is called the Genesis ID, under which the initial claims and verification methods are bound.

### Create
The creation of the identity (`did:pqie`) begins by generating a base Kyber-1024 keypair ($n=512$, $q=24593$). For identity attribute binding, the user's underlying claims are lifted into a Ring-LWE polynomial with injected Gaussian noise ($\sigma=4.0$). 
The Genesis ID (`pqie-identifier`) is deterministically constructed by taking the `sha3_512` and `blake2b` hashes of the public key lattice and appending a 4-byte random entropy suffix to prevent collisions. 
The Genesis Claims, including the raw public key and metadata representation, are encrypted via a Ring-LWE Key Encapsulation Mechanism (KEM) and AES-GCM into a secure payload known as a Digital Envelope. This Envelope is pinned to decentralized storage (e.g., IPFS), and its resulting CID is anchored directly on the ledger (e.g., via an Indy NYM transaction or Ethereum smart contract).

### State transition (Update)
Adding new keys, rotating existing keys, or updating the encrypted claims requires governed state transitions. The state transition is executed by creating a new Digital Envelope reflecting the updated DID Document. 
To validate the transition without exposing the underlying private keys or plaintext documents, the controller generates a Post-Quantum Lattice Signature (e.g., using Dilithium) over the new Digital Envelope's IPFS CID and the previous state root. This signature is verified by the ledger node (or smart contract) before accepting the state update, ensuring only the exact mathematical owner can transition the identity state.

### Deactivate
When the identity owner explicitly revokes their operational Kyber-1024 keys or an assigned governing authority issues a revocation constraint (in the case of on-chain KYC identities), the identity is considered deactivated. A signed lattice transaction is submitted to the registry, appending a revocation flag. A deactivated identity can no longer generate valid Token structures, create proofs, or execute state transitions.

### Type of identity
- Regular - identity generated by the user or organization off-chain, leveraging IPFS and independent anchors for mapping state.
- On-chain identity - identity created and managed directly by a smart contract or authority. This type of identity can behave as an on-chain issuer, allowing any dAPP to issue credentials to its users in a trustless manner. It contains an additional verification method (`EcdsaSecp256k1RecoveryMethod2020`) that relies on the EVM address from which the identity was originally created.

### Resolve
Abstract algorithm for resolving (read operation).

Contract address for resolving the did (indy main/test networks): `0xPQIEREGISTRY000000000000000000`

PQIE did driver accepts DID in URI format. Currently, we support three URI formats:

- `did:pqie:5135e697:8b7ecf94:a3f21bc0`
- `did:pqie:5135e697:8b7ecf94:a3f21bc0?state=<hex_of_state>`
- `did:pqie:5135e697:8b7ecf94:a3f21bc0?gist=<hex_of_gist_state>`

Each of these formats has a different read algorithm. But they all have a certain common logic of presentation.

Common steps for all formats of DID:
1.1 Get a method from DID (pqie).
1.2 Get a blockchain name from DID if applicable.
1.3 Get chain ID from DID.
1.4 Verify data that was encoded on the identification.
1.5 Find resolver by pair of chain name and blockchain id.

Step 5:
5.1 Read operation for the simple format of DID. This format means that the resolver should read the latest information about ID and GIST from the contract. If ID is the genesis one or doesn't exist on the contract, resolver will return only GIST info.
5.1.1 Call getGISTRoot from the contract to get the latest GIST state.
5.1.2 Call getGISTRootInfo with GIST from the step above to get the latest information about GIST.
5.1.3 Call getStateInfoById with the user ID to get the latest information about the user’s state. If it does not exist return an empty object:
```json
"info": {
    "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0#state-info",
    "state": "7a1a45d22b...",
    "replacedByState": "000000000...",
    "createdAtTimestamp": "1716909689"
},
"global": {
    "root": "09473a63...",
    "replacedByRoot": "0000000...",
    "createdAtTimestamp": "1720600400"
}
```
5.2 `did...#state=<state>` Resolve DID document by committed state. In some cases, we should get historical DID to validate the information that was replaced at the current time. Since we can’t get GIST by the user’s ID, global info will not exist in the resolution document.
5.2.1 Call getStateInfoByState from the contract to get information about the user’s state by state.
5.2.2 Verify that this state is the user’s state.
5.3 `did...#gist=<state>` Resolve state by gist state. Identities can exist under a global state for increased security and anonymity. In some cases, we should understand that it may exist or not exist for some user cases under the global target state.
5.3.1 Call getGISTProofByRoot with GIST root (key) and users ID (value), for get exist or not exist proof.
5.3.2 Call getGISTRootInfo with root from the step above to get GIST information.
5.3.3 If the proof has exists = true, execute the next state. If exists = false return information only about GIST state.
5.3.4 Call getStateInfoByState with the value from proof to return information about the user’s state.

JSON result description: https://pqie.network/ns/did/v1#state-info

Build representation document: After fetching the gist and the user’s state it is possible to build a representation document.
6.1 Create PQIEStateInfo2024 verification method : 
6.1.1 struct { id type stateContractAddress published latest global } 
6.1.2 In the latest field, put information about the user’s state. In the global field, put information about the GIST state.
6.1.3 Fill id filed in the following format <did>#state=<requested_state|latest_state>. requested_state - use the state from the request if the request had #state=... latest_state - use the state from the resolver response.
6.1.4 Add PQIEStateInfo2024 type to type field.
6.1.5 Fill stateContractAddress in the following format <chain_id>:<resolver_contract>.
6.1.6 Set true in published if the user’s state was been published to the smart contract.
6.1.7 Create an array authentication and put the struct from step 6.1 in this array.
6.1.8 Put the array authentication to didDocument. Also, add `@context: ["https://www.w3.org/ns/did/v1", "https://pqie.network/ns/did/v1"]` to this didDocument, add object to this array
6.2 Add optional EcdsaSecp256k1RecoveryMethod2020 for ethereum controlled identities.
6.2.1 Check if identity is ethereum based.
6.2.2 If it is an ethereum controlled identity add EcdsaSecp256k1RecoveryMethod2020 following the corresponding specification

6.9 Build representation:

```json
{
	"@context": ["https://w3id.org/did-resolution/v1"],
	"didDocument": {},
	"didResolutionMetadata": {},
	"didDocumentMetadata": {}
}
```
## Security and Privacy Considerations
There are several security and privacy considerations that implementers recommended to take into consideration when implementing this specification:

### Data Forgery Prevention
Our DID method prevents forgery and falsification through the usage of Post-Quantum Lattice Signatures (Dilithium) and Ring-LWE Digital Envelopes, such that only the exact mathematical identity owner can issue or present DID-linked credentials. The identity owner can choose to A) Only issue verifiable claims locked under their lattice public key or; B) Issue access tokens utilizing the homomorphic properties of Ring-LWE where specific metadata evaluations (e.g., KYC valid) are computed directly over the ciphertexts without leaking the raw data. The controller securely signs the data transitions, protecting against forgery even against cryptanalytically relevant quantum computers (CRQCs).

### Eavesdropping attacks
Eavesdropping attacks need to be mitigated by the usage of a secure communication channel (secured with TLS or similar means), since we use a message-based communication protocol that is not natively encrypted in transit layers. However, PQIE's "Encrypted-by-Default" architecture wraps the initial and updated DID Document structures in a Digital Envelope (AES-GCM locked by Ring-LWE KEM). As a result, network listeners and passive ledger observers only ever intercept an encrypted IPFS CID payload, providing a secondary robust defense-in-depth against data scraping.

### Cryptographic Agility
The `did:pqie` method leverages modern Ring-LWE lattice cryptography. The initial standard uses Kyber-1024 parameters ($n=512$, $q=24593$) for key encapsulation/encryption, mapping variables closely to NIST’s FIPS 203. For signature authentication, parameter sets corresponding to Dilithium (FIPS 204) are required to sign the Digital Envelope states. In the future, other post-quantum parameter sets can be dynamically encoded using the `latticeParams` object within the DID Document’s verification method, providing immediate forward compatibility as post-quantum standardized extensions evolve.

### Keep DID Keys safe
The DID method inherently includes support for comprehensive key rotation semantics; however, if the core Kyber lattice secret key ($s$) is compromised, an attacker may generate valid post-quantum signatures to rotate operational keys and thereby hijack the identity state mappings. Controllers SHOULD rigorously store their lattice private keys in hardware-backed security modules (HSM) or mathematically robust Trusted Execution Environments (TEE) designed with adequate post-quantum memory limits.

### Keep personal data safe
The syntax and construction of the `did:pqie` DID and its universally distributed Document helps to ensure that no Personally Identifiable Information (PII) or personal data is exposed over the public network layer:
- **Zero On-Chain PII**: Raw PII is NEVER stored directly on the ledger architecture. All persistent data is stored off-chain on IPFS strictly encapsulated within a Ring-LWE Digital Envelope.
- **Resistant Identifiers**: The `pqie-identifier` utilizes sequential dual-hashing (`sha3_512` followed by `blake2b`), fundamentally preventing any algorithmic reverse-engineering of the underlying attributes that seed the genesis ID.
- **Homomorphic Noise Injection**: When lifting citizen attributes (e.g., Aadhaar parameters) to the polynomial mapping prior to encryption, discrete Gaussian noise (&sigma;=4.0) is inherently added. This guarantees the derived cyphertexts are computationally indistinguishable from uniform random polynomial coefficients, satisfying the Learning With Errors cryptographic assumption.

Additional Privacy and Security Recommendations:
Implementers are strongly encouraged to review the following:
- The Privacy Considerations section of the DID Implementation Guide: https://w3c.github.io/did-imp-guide/#privacy-considerations.
- The Privacy Considerations section of the Decentralized Identifiers (DIDs) (DID-CORE) specification: https://www.w3.org/TR/did-core/#privacy-considerations.

### 2.7 The Ledger-Agnostic Property
A core innovation of the PQIE framework is its natively **ledger-agnostic** architecture. Because the entirety of the DID Document is encapsulated within a Ring-LWE KEM Digital Envelope *before* transmission, the resulting cryptographic payload (or its hash pointer) can be securely written to **any** underlying distributed ledger technology (DLT) or key-value store. 

This means `did:pqie` is not locked to a specific blockchain. The method natively abstracts the storage layer via a Ledger-Agnostic Interface (Layer E), allowing implementations to anchor identities on:
- **Permissioned identity ledgers** (e.g., Hyperledger Indy)
- **Public smart contracts** (e.g., Ethereum, Polygon via EVM mappings)
- **Decentralized file configurations** (e.g., IPFS + Filecoin combinations)

Verifiers and resolvers simply fetch the on-chain payload $P$ via the respective ledger adapter and proceed with standard decapsulation and signature verification, entirely decoupled from the consensus mechanism or tokenomics of the underlying host chain.

## 3. Future Scope: PQIE in Web 3.0
Because PQIE is ledger-agnostic, it can plug into diverse Web 3.0 runtimes. DeFi platforms can embed quantum-safe KYC proofs, healthcare networks can share encrypted patient IDs across hospitals, supply-chain consortia can bind tamper-proof product DIDs to digital twins, and metaverse environments can issue long-lived, privacy-preserving avatar credentials.
In enterprise settings, PQIE can underpin cross-jurisdictional e-KYC: banks anchor encrypted customer DIDs on a consortium chain and regulators decrypt only when a court order is provided, achieving privacy by default.

## 4. Ring-LWE Security Analysis
Ring-LWE hardness is reducible to the worst-case Shortest Vector Problem (SVP) in ideal lattices. We adopt the Kyber-1024 core parameters for encryption compatibility, with modulus $q = 3329$ and polynomial degree $n = 256$, but expand to $n = 512$ for signature tightness. The ciphertext modulus is selected as a product of two 14-bit primes, enabling RNS decomposition that aligns with AVX2 vector lanes. Table 2 compares our security margins with Dilithium-III and Falcon-512.

| Scheme | n | q | Quantum Bit-Security |
|---|---|---|---|
| **PQIE-Enc** | 512 | 24577 | 256 |
| **Dilithium-III** | 256 | 8380417 | 192 |
| **Falcon-512** | 512 | 12289 | 128 |

*Table 2 — Quantitative comparison with quantum schemes.*

### 4.1 Trapdoor Hardness & Post-Quantum Resilience
The core security assumption underpinning PQIE is the **Ring Learning With Errors (Ring-LWE)** problem over cyclotomic rings $\mathbb{Z}_p[x]/(x^n + 1)$. Recovering the exact secret polynomial $s$ from a generated public sample $b = a \cdot s + e \pmod q$ is mathematically reducible to the Shortest Vector Problem (SVP) in a family of ideal lattices. 

This specific construction withstands not only the best known classical lattice reduction attacks (e.g., BKZ algorithm parameters), but is definitively immune to **Quantum Fourier-Sampling Attacks** (such as Shor's algorithm, which easily factors RSA and solves Discrete Logarithms for Elliptic Curves).

### 4.2 Non-Linear Operations & Side-Channel Mitigation
To prevent side-channel leakage across consecutive protocol sessions, PQIE injects specific non-linear distortions during polynomial mapping:

1. **Number-Theoretic Transform (NTT)**: Coefficients undergo high-speed $O(n \log n)$ conversion to the NTT domain to enable constant-time convolution ($NTT(a) \otimes NTT(s)$), mitigating timing-based side channels.
2. **tanh Activation Scrambling**: Before noise addition, a pointwise $\tanh$ function is deterministically applied to each coefficient. This disrupts linear interpolation patterns in NTT outputs that may otherwise leak the geometry of $s$ or $e$ over multiple signature nonces. 

### 4.3 Error Generation and Homomorphic Filtering
The error polynomial $e(x)$ is meticulously sampled from a zero-centered discrete Gaussian distribution ($\sigma \approx 4.0$). Each individual coefficient $e_i$ is bound heavily between $(-5 \dots +5)$, mathematically ensuring that the initial cryptographic noise remains minimal.

However, during active sessions (especially regarding Verifiable Credentials that rely heavily on zero-knowledge evaluation over ciphertexts), noise inherently grows. PQIE applies an aggressive **Homomorphic Noise Filter**:
- After roughly 128 cryptographic operations, for every polynomial coefficient $c_i$, we compute $c_i' = (c_i \pmod{q/4})$ and set the new operating modulus $q \leftarrow q/4$. 
- This step acts as a refreshing mechanism, aggressively keeping the encrypted DID payload size statically beneath 2 kB, minimizing overall ledger storage costs without ever exposing underlying data or weakening the lattice bound.

## References
- https://w3c-ccg.github.io/did-spec/
- https://www.w3.org/TR/did-core/
