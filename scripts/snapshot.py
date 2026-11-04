"""Récupère les résultats civicAPI et écrit des instantanés légers dans data/.
Lancé par .github/workflows/snapshot.yml. La carte les affiche tout de suite,
puis passe en direct sur civicAPI dès qu'il répond."""
import json, time, urllib.request, os

API = "https://civicapi.org/api/v2/race/search?startDate=2026-11-03&endDate=2026-11-03&country=US&limit=50000&election_type="
KEEP = {"US Senate", "House of Representatives", "Governor"}
NOT_STATE = {"US", "PR", "GU", "VI", "AS", "MP", "DC"}

def slim(races):
    out = []
    for r in races:
        if r.get("type") not in KEEP or not r.get("province") or r["province"] in NOT_STATE:
            continue
        out.append({
            "type": r["type"], "province": r["province"], "district": r.get("district"),
            "percent_reporting": r.get("percent_reporting"),
            "candidates": [{"name": c.get("name"), "party": c.get("party"), "votes": c.get("votes"),
                            "percent": c.get("percent"), "winner": c.get("winner")}
                           for c in (r.get("candidates") or [])[:4]],
        })
    return out

def grab(kind):
    req = urllib.request.Request(API + kind, headers={"User-Agent": "midterms-2026-snapshot"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.load(resp).get("races", [])

os.makedirs("data", exist_ok=True)
for kind in ("General", "Statewide"):
    try:
        races = slim(grab(kind))
        if races:
            path = f"data/{kind.lower()}.json"
            body = {"races": races}
            body["at"] = int(time.time() * 1000)
            with open(path, "w") as f:
                json.dump(body, f, separators=(",", ":"), ensure_ascii=False)
            print(kind, "écrit", len(races))
    except Exception as e:
        print(kind, "erreur", e)
