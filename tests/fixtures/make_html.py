"""Gera HTML sintético no formato (data-stat / data-append-csv) usado pelo parser. NÃO são dados reais."""

COLS = ["player", "age", "team_id", "pos", "g", "mp", "per", "ws", "ws_per_48", "bpm", "vorp"]


def season_html(rows):
    def td(stat, val, pid=None):
        extra = f' data-append-csv="{pid}"' if pid else ""
        return f'<td data-stat="{stat}"{extra}>{val}</td>'

    body = ['<tr class="thead"><th data-stat="player">Player</th></tr>']
    for pid, vals in rows:
        cells = [td("player", vals["player"], pid)] + [td(c, vals.get(c, "")) for c in COLS[1:]]
        body.append("<tr>" + "".join(cells) + "</tr>")
    body.append('<tr><td data-stat="player">League Average</td><td data-stat="g">70</td></tr>')
    return f'<html><body><table id="advanced"><thead></thead><tbody>{"".join(body)}</tbody></table></body></html>'


def row(player, team, g, ws, **kw):
    d = {"player": player, "age": "27", "team_id": team, "pos": "SF", "g": str(g), "mp": str(g * 30),
         "per": "20.0", "ws": str(ws), "ws_per_48": "0.150", "bpm": "4.0", "vorp": "3.0"}
    d.update(kw)
    return d
