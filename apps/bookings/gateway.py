"""Gateway de pagamentos do PassaMoz.

A implementação usa a API REST do gateway configurado no ambiente. As chaves
secretas ficam exclusivamente em variáveis de ambiente do servidor.
"""
import json
import os
import urllib.error
import urllib.request


class GatewayError(Exception):
    pass


class NetShopGateway:
    def __init__(self):
        self.base_url = os.getenv("NETSHOP_BASE_URL", "https://www.netshop.co.mz/api").rstrip("/")
        self.api_key = os.getenv("NETSHOP_API_KEY", "").strip()
        self.timeout = int(os.getenv("PAYMENT_GATEWAY_TIMEOUT", "20"))

    @property
    def configured(self):
        return bool(self.api_key)

    def create_charge(self, *, wallet_id, amount, method, msisdn, reference):
        if not self.configured:
            raise GatewayError("O gateway ainda não está configurado no servidor.")
        payload = json.dumps({
            "amount": float(amount),
            "currency": "MZN",
            "method": method,
            "msisdn": msisdn,
            "reference": reference,
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/v1/charges",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Wallet-ID": wallet_id,
                "Content-Type": "application/json",
                "Idempotency-Key": reference,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
            raise GatewayError("Não foi possível iniciar o pagamento no gateway.") from exc
        gateway_ref = data.get("id") or data.get("reference") or data.get("charge_id")
        status = str(data.get("status") or "pending").lower()
        if not gateway_ref:
            raise GatewayError("O gateway não devolveu uma referência de pagamento válida.")
        return {"reference": str(gateway_ref), "status": status, "raw": data}
