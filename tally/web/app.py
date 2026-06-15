"""tally web app: Today (quick-add), Tracker, and Gallery."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .. import hobbies as H
from ..config import settings
from ..db import DB
from ..stats import best_score, current_streak, heatmap, longest_streak

BASE = Path(__file__).parent
app = FastAPI(title="tally")
templates = Jinja2Templates(directory=str(BASE / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
db = DB(settings.db_path)


def _today_ctx() -> dict:
    today = date.today().isoformat()
    rows = []
    for h in H.daily_hobbies():
        rows.append({"hobby": h, "streak": current_streak(db.dates_for(h.key), date.today()),
                     "logged": db.logged_on(h.key, today)})
    return {"daily": rows, "hobbies": list(H.HOBBIES.values()), "today": today}


@app.get("/", response_class=HTMLResponse)
def today(request: Request):
    return templates.TemplateResponse(request, "today.html", _today_ctx())


@app.post("/log", response_class=HTMLResponse)
def log_daily(request: Request, hobby: str = Form(...), score: Optional[float] = Form(None)):
    h = H.get(hobby)
    if h:
        db.add(hobby, date.today().isoformat(), title=h.label, score=score)
    return templates.TemplateResponse(request, "_daily.html", _today_ctx())


@app.post("/entry")
def add_entry(hobby: str = Form(...), title: str = Form(""), date_str: str = Form(""),
              score: Optional[float] = Form(None), rating: Optional[int] = Form(None),
              result: str = Form(""), image_url: str = Form(""), link: str = Form(""),
              notes: str = Form("")):
    when = date_str or date.today().isoformat()
    db.add(hobby, when, title=title or (H.get(hobby).label if H.get(hobby) else hobby),
           score=score, rating=rating or None, result=result or None,
           image_url=image_url or None, link=link or None, notes=notes or None)
    return RedirectResponse("/gallery", status_code=303)


@app.post("/entry/{entry_id}/delete")
def delete_entry(entry_id: int):
    db.delete(entry_id)
    return RedirectResponse("/gallery", status_code=303)


@app.get("/tracker", response_class=HTMLResponse)
def tracker(request: Request):
    cards = []
    for h in H.HOBBIES.values():
        entries = db.entries(h.key)
        dates = [e["date"] for e in entries]
        cards.append({
            "hobby": h, "total": len(entries),
            "streak": current_streak(dates, date.today()) if h.daily else None,
            "longest": longest_streak(dates) if h.daily else None,
            "best": best_score([e["score"] for e in entries], h.score_better),
            "last": entries[0]["date"] if entries else None,
        })
    hm = heatmap([e["date"] for e in db.entries()], date.today(), days=84)
    return templates.TemplateResponse(request, "tracker.html", {"cards": cards, "heatmap": hm})


@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request, hobby: str = ""):
    entries = db.entries(hobby or None, limit=300)
    return templates.TemplateResponse(request, "gallery.html", {
        "entries": entries, "hobbies": list(H.HOBBIES.values()),
        "active": hobby, "get": H.get})


def main():
    import uvicorn
    uvicorn.run("tally.web.app:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
