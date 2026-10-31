"""CLI: python -m ingest.cli <init|fetch-bbr|fetch-nba|load-bronze> [opções]"""
import argparse
import json
import pathlib
import sys

import yaml

from .bbr import BBRClient, FetchError, RateLimited, load_bronze
from .nba import NBAClient
from .ratelimit import RateLimiter
from .raw_store import RawStore, new_run_id

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _cfg():
    return yaml.safe_load((ROOT / "config" / "sources.yml").read_text())


def _store(cfg):
    return RawStore(ROOT / cfg["paths"]["db"], ROOT / cfg["paths"]["raw_dir"])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ingest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    b = sub.add_parser("fetch-bbr")
    b.add_argument("--kind", default="advanced")
    b.add_argument("--from", dest="y0", type=int, default=1952)  # WS/48 existe desde 1951-52
    b.add_argument("--to", dest="y1", type=int, default=2026)
    b.add_argument("--refresh", action="store_true")
    n = sub.add_parser("fetch-nba")
    n.add_argument("--endpoint", required=True)
    n.add_argument("--params", default="{}", help="JSON com os parâmetros do endpoint")
    n.add_argument("--refresh", action="store_true")
    sub.add_parser("load-bronze")
    a = ap.parse_args(argv)

    cfg = _cfg()
    store = _store(cfg)
    store.init()
    if a.cmd == "init":
        print("raw/bronze inicializados em", store.db_path)
    elif a.cmd == "fetch-bbr":
        c = cfg["bbr"]
        if "<seu-email>" in c["user_agent"]:
            sys.exit("Edite bbr.user_agent em config/sources.yml com um contato real.")
        client = BBRClient(store, RateLimiter(c["max_per_minute"], c["jitter_s"]), c["user_agent"],
                           c["terms_ref"], c["pages"])
        run_id = new_run_id()
        try:
            for year in range(a.y0, a.y1 + 1):
                raw_id, cached = client.fetch_season_table(a.kind, year, run_id, refresh=a.refresh)
                print(f"{year} {a.kind}: {'cache' if cached else 'baixado'} raw_id={raw_id}")
        except RateLimited as e:
            sys.exit(f"PARADO: {e}")
        except FetchError as e:
            sys.exit(f"ERRO: {e}")
    elif a.cmd == "fetch-nba":
        c = cfg["nba"]
        client = NBAClient(store, RateLimiter(c["max_per_minute"], c["jitter_s"]), c["terms_ref"], c["timeout_s"])
        raw_id, cached = client.fetch(a.endpoint, json.loads(a.params), new_run_id(), refresh=a.refresh)
        print("cache" if cached else "baixado", raw_id)
    elif a.cmd == "load-bronze":
        print(load_bronze(store))


if __name__ == "__main__":
    main()
