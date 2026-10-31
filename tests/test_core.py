import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fixtures.make_html import row, season_html  # noqa: E402

from ingest.bbr import BBRClient, RateLimited, load_bronze, parse_season_table  # noqa: E402
from ingest.ratelimit import RateLimiter  # noqa: E402
from ingest.raw_store import RawStore  # noqa: E402


@pytest.fixture
def store(tmp_path):
    s = RawStore(tmp_path / "t.duckdb", tmp_path / "raw")
    s.init()
    return s


def test_rate_limiter_spacing():
    t = {"now": 0.0}
    sleeps = []

    def sleep(x):
        sleeps.append(x)
        t["now"] += x

    rl = RateLimiter(10, 0.0, clock=lambda: t["now"], sleep=sleep)
    for _ in range(4):
        rl.wait()
    assert sleeps == [6.0, 6.0, 6.0]  # 10/min = 6s entre requisições


def test_raw_store_idempotent(store):
    kw = dict(source="bbr", endpoint="e", url="u", params={"a": 1}, status=200, payload=b"abc",
              ext="html", run_id="r", terms_ref="t")
    a = store.save(**kw)
    b = store.save(**kw)
    assert a == b
    con = store.connect()
    assert con.execute("SELECT count(*) FROM raw.fetch_log").fetchone()[0] == 1
    con.close()
    assert store.lookup("bbr", "u")["raw_id"] == a
    assert len(list((store.raw_dir / "bbr").rglob("*.html"))) == 1


def test_parser_skips_league_row_and_reads_ids():
    html = season_html([("aaaaa01", row("Jogador A", "AAA", 80, 12.0)),
                        ("bbbbb01", row("Jogador B", "TOT", 70, 8.0))])
    rows = parse_season_table(html)
    assert [r["player_id"] for r in rows] == ["aaaaa01", "bbbbb01"]
    assert rows[0]["ws"] == "12.0" and rows[1]["team_id"] == "TOT"


def test_parser_alias_columns():
    html = season_html([("aaaaa01", row("Jogador A", "AAA", 80, 12.0))]).replace('data-stat="team_id"', 'data-stat="team_name_abbr"')
    assert parse_season_table(html)[0]["team_id"] == "AAA"


class FakeResp:
    def __init__(self, status, content=b""):
        self.status_code, self.content, self.headers = status, content, {}


class FakeSession:
    def __init__(self, responses):
        self.responses, self.headers, self.calls = list(responses), {}, 0

    def get(self, url, timeout=None):
        self.calls += 1
        return self.responses.pop(0)


def _client(store, session):
    return BBRClient(store, RateLimiter(600, 0.0, sleep=lambda x: None), "ua", "terms",
                     {"advanced": "/leagues/NBA_{year}_advanced.html"}, session=session, sleep=lambda x: None)


def test_client_cache_and_429(store):
    html = season_html([("aaaaa01", row("Jogador A", "AAA", 80, 12.0))]).encode()
    s = FakeSession([FakeResp(200, html)])
    c = _client(store, s)
    raw_id, cached = c.fetch_season_table("advanced", 1974, "r1")
    assert not cached
    raw_id2, cached2 = c.fetch_season_table("advanced", 1974, "r2")
    assert cached2 and raw_id2 == raw_id and s.calls == 1  # segundo acesso vem do cache
    c429 = _client(store, FakeSession([FakeResp(429)]))
    with pytest.raises(RateLimited):
        c429.fetch_season_table("advanced", 1975, "r3")


def test_load_bronze(store):
    c = _client(store, FakeSession([
        FakeResp(200, season_html([("aaaaa01", row("Jogador A", "AAA", 80, 12.0))]).encode()),
        FakeResp(200, season_html([("aaaaa01", row("Jogador A", "AAA", 82, 13.0))]).encode()),
    ]))
    c.fetch_season_table("advanced", 1974, "r")
    c.fetch_season_table("advanced", 1975, "r")
    assert load_bronze(store) == {"advanced": 2}
    con = store.connect()
    got = con.execute("SELECT season_end_year, ws FROM bronze.bbr_season_advanced ORDER BY 1").fetchall()
    con.close()
    assert got == [("1974", "12.0"), ("1975", "13.0")]
