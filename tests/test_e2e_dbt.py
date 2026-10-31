"""E2E: fixture -> raw -> bronze -> dbt build (silver/gold). Pula se o dbt não estiver instalado."""
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fixtures.make_html import row, season_html  # noqa: E402

from ingest.bbr import load_bronze  # noqa: E402
from ingest.raw_store import RawStore  # noqa: E402

DBT = shutil.which("dbt")
ROOT = pathlib.Path(__file__).resolve().parent.parent


def _save(store, year, rows):
    store.save(source="bbr", endpoint="season_advanced", url=f"https://x/NBA_{year}_advanced.html",
               params={"kind": "advanced", "year": year}, status=200, payload=season_html(rows).encode(),
               ext="html", run_id="r", terms_ref="t")


@pytest.mark.skipif(DBT is None, reason="dbt não instalado")
def test_pipeline(tmp_path):
    store = RawStore(tmp_path / "e2e.duckdb", tmp_path / "raw")
    store.init()
    _save(store, 1973, [("p1", row("P1", "AAA", 80, 10.0))])  # pré-corte: P1 é "truncado"
    _save(store, 1974, [("p1", row("P1", "AAA", 80, 12.0)), ("p2", row("P2", "AAA", 80, 9.0)),
                        ("p3", row("P3", "AAA", 80, 5.0)), ("p4", row("P4", "AAA", 20, 8.0))])
    _save(store, 1975, [("p1", row("P1", "AAA", 80, 11.0)),
                        ("p2", row("P2", "TOT", 80, 8.0)),   # linha-resumo (troca de time)
                        ("p2", row("P2", "AAA", 40, 4.0)),
                        ("p2", row("P2", "BBB", 40, 4.0)),
                        ("p3", row("P3", "AAA", 80, 6.0))])
    load_bronze(store)

    env = dict(os.environ, GOAT_DB=str(tmp_path / "e2e.duckdb"))
    vars_ = json.dumps({"pool_top_n_career": 2, "pool_top_n_peak": 2, "pool_peak_window": 2, "pool_min_career_games": 100})
    r = subprocess.run([DBT, "build", "--profiles-dir", ".", "--vars", vars_], cwd=ROOT / "dbt",
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]

    con = store.connect()
    # silver: 8 linhas (1+4+3); P2/1975 usa a linha TOT (ws=8.0, g=80)
    assert con.execute("SELECT count(*) FROM silver.silver_bbr_player_season_advanced").fetchone()[0] == 8
    assert con.execute("SELECT ws, g FROM silver.silver_bbr_player_season_advanced "
                       "WHERE player_id='p2' AND season_end_year=1975").fetchall() == [(8.0, 80)]
    # gold: P4 cai pelo piso de jogos; P1 é sinalizado como truncado (1 temporada pré-corte)
    pool = {r[0]: r for r in con.execute(
        "SELECT player_id, career_ws, pre_cutoff_seasons FROM gold.gold_pool_candidates").fetchall()}
    assert "p4" not in pool
    assert pool["p1"][1] == 23.0 and pool["p1"][2] == 1  # 12+11 (1973 fica fora da soma)
    con.close()
