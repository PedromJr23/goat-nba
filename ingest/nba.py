"""Wrapper fino do nba_api: grava a resposta crua na camada raw.

Os nomes de endpoint/parâmetros são passados por você (config/CLI) e DEVEM ser validados
na documentação do nba_api na Fase 3b; o NBA.com muda endpoints sem aviso.
"""
import importlib
import json


class NBAClient:
    def __init__(self, store, limiter, terms_ref, timeout=30, endpoints_module="nba_api.stats.endpoints"):
        self.store, self.limiter, self.terms_ref, self.timeout = store, limiter, terms_ref, timeout
        self._module = endpoints_module

    @staticmethod
    def pseudo_url(endpoint, params):
        return f"nba_api://{endpoint}?" + "&".join(f"{k}={params[k]}" for k in sorted(params))

    def fetch(self, endpoint, params, run_id, refresh=False):
        url = self.pseudo_url(endpoint, params)
        if not refresh:
            cached = self.store.lookup("nba", url)
            if cached:
                return cached["raw_id"], True
        cls = getattr(importlib.import_module(self._module), endpoint)
        self.limiter.wait()
        obj = cls(**params, timeout=self.timeout)
        payload = obj.get_json()
        payload = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode("utf-8")
        raw_id = self.store.save(source="nba", endpoint=f"nba_api:{endpoint}", url=url, params=params, status=200,
                                 payload=payload, ext="json", run_id=run_id, terms_ref=self.terms_ref)
        return raw_id, False
