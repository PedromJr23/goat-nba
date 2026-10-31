"""Cliente e parser da Basketball-Reference (tabelas de temporada).

ATENCAO: o parser foi validado apenas contra um fixture sintético (tests/fixtures).
Antes da carga completa, rode com 1-2 temporadas reais e confira (Fase 3b).
"""
import json
import time

# Usamos curl_cffi em vez do requests puro para evitar bloqueios Cloudflare (HTTP 403)
from curl_cffi import requests
from bs4 import BeautifulSoup, Comment

BASE = "https://www.basketball-reference.com"

# Nomes de colunas já mudaram no site; normalizamos para um conjunto canônico.
ALIASES = {"name_display": "player", "team_name_abbr": "team_id", "pos": "pos", "team": "team_id"}


class RateLimited(Exception):
    """HTTP 429: a execução inteira deve parar (bloqueio pode durar até 1 dia)."""


class FetchError(Exception):
    pass


class BBRClient:
    def __init__(self, store, limiter, user_agent=None, terms_ref=None, pages=None, session=None, timeout=30, sleep=time.sleep):
        self.store, self.limiter, self.terms_ref = store, limiter, terms_ref
        self.pages, self.timeout, self._sleep = pages or {}, timeout, sleep
        
        # Cria a sessão impersonando o Chrome real para passar pelo Cloudflare
        self.session = session or requests.Session(impersonate="chrome")

    def url_for(self, kind, year):
        return BASE + self.pages[kind].format(year=year)

    def fetch_season_table(self, kind, year, run_id, refresh=False):
        url = self.url_for(kind, year)
        if not refresh:
            cached = self.store.lookup("bbr", url)
            if cached and cached.get("http_status") == 200:
                return cached["raw_id"], True

        resp = None
        for attempt in range(3):
            if self.limiter:
                self.limiter.wait()
            
            resp = self.session.get(url, timeout=self.timeout)
            
            if resp.status_code == 429:
                self.store.save(
                    source="bbr", endpoint=f"season_{kind}", url=url,
                    params={"kind": kind, "year": year}, status=429,
                    payload=None, ext="html", run_id=run_id, terms_ref=self.terms_ref,
                    note=f"Retry-After={resp.headers.get('Retry-After')}"
                )
                raise RateLimited(f"429 em {url}; interrompa a execução e aguarde.")

            if resp.status_code == 403:
                self._sleep(5)

            if resp.status_code >= 500 and attempt < 2:
                self._sleep(30 * (attempt + 1))
                continue
                
            break

        raw_id = self.store.save(
            source="bbr", endpoint=f"season_{kind}", url=url,
            params={"kind": kind, "year": year}, status=resp.status_code,
            payload=resp.content if resp.status_code == 200 else None, ext="html",
            run_id=run_id, terms_ref=self.terms_ref
        )

        if resp.status_code != 200:
            raise FetchError(f"HTTP {resp.status_code} em {url}")

        return raw_id, False


def _tables(soup):
    for t in soup.find_all("table"):
        yield t
    # BBR coloca algumas tabelas dentro de comentários HTML
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        if "<table" in c:
            yield from BeautifulSoup(c, "lxml").find_all("table")


def parse_season_table(html):
    """Retorna lista de dicts (uma linha por jogador/time) usando os atributos data-stat."""
    soup = BeautifulSoup(html, "lxml")
    best, best_n = None, 0
    for t in _tables(soup):
        n = len(t.select("tbody tr td[data-stat]"))
        if n > best_n:
            best, best_n = t, n
    if best is None:
        return []
    rows = []
    for tr in best.select("tbody tr"):
        if "thead" in (tr.get("class") or []):
            continue
        rec, pid = {}, None
        for cell in tr.find_all(["th", "td"]):
            stat = cell.get("data-stat")
            if not stat:
                continue
            rec[ALIASES.get(stat, stat)] = cell.get_text(strip=True) or None
            pid = pid or cell.get("data-append-csv")
            if not pid:
                a = cell.find("a", href=True)
                if a and "/players/" in a["href"]:
                    pid = a["href"].rsplit("/", 1)[-1].replace(".html", "")
        if pid:  # descarta linhas de média da liga / separadores
            rec["player_id"] = pid
            rows.append(rec)
    return rows


def load_bronze(store):
    """Reconstrói bronze.bbr_season_<kind> a partir do raw (tudo VARCHAR; idempotente)."""
    import pandas as pd
    con = store.connect()
    try:
        meta = con.execute(
            "SELECT raw_id, params_json, payload_path, fetched_at FROM raw.fetch_log "
            "WHERE source='bbr' AND http_status=200 AND endpoint LIKE 'season_%' ORDER BY fetched_at"
        ).fetchall()
        latest = {}
        for raw_id, pj, path, fetched in meta:  # mantém o fetch mais recente por (kind, year)
            p = json.loads(pj)
            latest[(p["kind"], p["year"])] = (raw_id, path)
        frames = {}
        for (kind, year), (raw_id, path) in sorted(latest.items()):
            rows = parse_season_table(open(path, "rb").read().decode("utf-8", "replace"))
            if not rows:
                continue
            df = pd.DataFrame(rows).astype("string")
            df.insert(0, "raw_id", raw_id)
            df.insert(1, "season_end_year", str(year))
            frames.setdefault(kind, []).append(df)
        counts = {}
        for kind, dfs in frames.items():
            full = pd.concat(dfs, ignore_index=True)
            con.register("df_in", full)
            con.execute(f"CREATE OR REPLACE TABLE bronze.bbr_season_{kind} AS "
                        "SELECT *, current_timestamp AS _loaded_at FROM df_in")
            con.unregister("df_in")
            counts[kind] = len(full)
        return counts
    finally:
        con.close()