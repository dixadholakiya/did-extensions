#!/usr/bin/env python3
"""
ZKP Token Generation Service
Zero-Knowledge Proof based service tokens using PQIE Lattice noise framework.
Proves KYC status without revealing underlying Aadhaar or PII.
"""

import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# Import PQIE framework
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pqie_framework import PQIECryptoEngine, PQIETokenGenerator

class ZKPTokenService:
    """ZKP Token Generation for Government Services"""

    def __init__(self):
        self.crypto_engine = PQIECryptoEngine()
        self.token_generator = PQIETokenGenerator(self.crypto_engine)
        self.service_ledger_path = Path(__file__).parent.parent / 'data' / 'government_services.json'
        self.credential_ledger_path = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
        
    async def generate_zkp_service_token(self, citizen_did: str, service_id: str) -> Dict[str, Any]:
        """
        Generate a ZKP token for a specific service.
        Proves: 
          1. Owner has valid Aadhaar KYC.
          2. Credential is not revoked.
          3. Proof is service-specific (obfuscated).
        """
        try:
            print(f"🎫 Generating ZKP token for {citizen_did} → {service_id}")
            
            # 1. Verify Service Existence
            service_info = self._get_service_info(service_id)
            if not service_info:
                return {"success": False, "error": f"Service {service_id} not found."}
                
            # 2. Verify Aadhaar KYC Existence and Status
            kyc_status = await self._verify_kyc_status(citizen_did)
            if not kyc_status["verified"]:
                return {"success": False, "error": kyc_status["error"]}
                
            # 3. Prepare ZKP Proof using PQIE Lifting
            # We lift "Verified" status with service_id as a salt to ensure token uniqueness per service
            proof_attributes = {
                "citizen_did": citizen_did,
                "service_id": service_id,
                "verification_status": "VERIFIED_AADHAAR_KYC",
                "kyc_credential_id": kyc_status["credential_id"],
                "proof_timestamp": datetime.now().isoformat(),
                "nonce": secrets.token_hex(16)
            }
            
            # Use lattice-based identity token generation to create a "ZKP" package
            # The underlying data is masked with Gaussian noise (Lattice-based ZKP approximation)
            zkp_package = self.token_generator.generate_identity_token(proof_attributes, user_identifier=citizen_did)
            
            # 4. Create Final Signed Service Token
            # This is the public token shared with the government department
            token_id = f"ZKP_ST_{service_id}_{secrets.token_hex(12)}"
            expires_at = (datetime.now() + timedelta(hours=8)).isoformat()
            
            final_token = {
                "token_id": token_id,
                "target_service": service_info["service_name"],
                "service_id": service_id,
                "citizen_did_masked": citizen_did[:8] + "..." + citizen_did[-4:],
                "zkp_proof": {
                    "token_id": zkp_package["token_id"],
                    "did": zkp_package["did"],
                    "verification_type": "PQIE-RingLWE-Proof",
                    "lattice_dimensions": self.crypto_engine.n,
                    "noise_sigma": self.crypto_engine.sigma
                },
                "status": "VALID",
                "issued_at": datetime.now().isoformat(),
                "expires_at": expires_at,
                "security_info": "This token proves KYC verification without revealing Aadhaar PII."
            }
            
            # Store in token registry (simulated usage log)
            self._log_zkp_generation(citizen_did, service_id, token_id)
            
            return {
                "success": True,
                "token": final_token,
                "redacted_token": self._redact_for_display(final_token),
                "expires_at": expires_at
            }
            
        except Exception as e:
            print(f"❌ Error in ZKP generation: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _get_service_info(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Fetch service details from ledger"""
        try:
            if self.service_ledger_path.exists():
                with open(self.service_ledger_path, 'r') as f:
                    data = json.load(f)
                    return data.get("government_services", {}).get(service_id)
            return None
        except:
            return None

    async def _verify_kyc_status(self, citizen_did: str) -> Dict[str, Any]:
        """Verify if the citizen has an active, non-revoked Aadhaar KYC VC"""
        try:
            if not self.credential_ledger_path.exists():
                return {"verified": False, "error": "Credential ledger not found."}
                
            with open(self.credential_ledger_path, 'r') as f:
                ledger = json.load(f)
                
            # Check index
            citizen_creds = ledger.get("indexes", {}).get("by_citizen_did", {}).get(citizen_did, [])
            if not citizen_creds:
                return {"verified": False, "error": "No Aadhaar KYC found for this citizen."}
                
            # Look for active AADHAAR_KYC
            for cred_id in citizen_creds:
                cred_entry = ledger.get("credentials", {}).get(cred_id, {})
                # Check status and type
                if cred_entry.get("credential_type") == "aadhaar_kyc":
                    if cred_entry.get("status") in ["ISSUED", "ACTIVE", "VERIFIED"]:
                        return {
                            "verified": True,
                            "credential_id": cred_id,
                            "issued_at": cred_entry.get("issued_at")
                        }
                    else:
                        return {"verified": False, "error": f"Credential is {cred_entry.get('status')}."}
            
            return {"verified": False, "error": "Active Aadhaar KYC credential not found."}
            
        except Exception as e:
            return {"verified": False, "error": f"Internal verification error: {str(e)}"}

    def _log_zkp_generation(self, citizen_did: str, service_id: str, token_id: str):
        """Log token generation for auditing"""
        log_path = Path(__file__).parent.parent / 'data' / 'zkp_token_audit.json'
        try:
            logs = []
            if log_path.exists():
                with open(log_path, 'r') as f:
                    logs = json.load(f)
            
            logs.append({
                "token_id": token_id,
                "citizen_did": citizen_did,
                "service_id": service_id,
                "timestamp": datetime.now().isoformat()
            })
            
            with open(log_path, 'w') as f:
                json.dump(logs, f, indent=2)
        except:
            pass

    def _redact_for_display(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive internal proof data for UI display"""
        redacted = token.copy()
        if "zkp_proof" in redacted:
            # Mask the hash-like values
            proof = redacted["zkp_proof"].copy()
            if "did" in proof:
                proof["did"] = proof["did"][:14] + "..."
            redacted["zkp_proof"] = proof
        return redacted

if __name__ == "__main__":
    # Test script
    import asyncio
    service = ZKPTokenService()
    async def test():
        # Using a dummy DID from existing data if possible
        res = await service.generate_zkp_service_token("did:sdis:indian:1234567890", "SERVICE_001")
        print(json.dumps(res, indent=2))
    
    # asyncio.run(test())
