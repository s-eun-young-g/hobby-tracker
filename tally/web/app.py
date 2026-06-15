"""tally web app: Today, per-hobby add/edit forms, Tracker, and Gallery."""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .. import hobbies as H
from ..config import settings
from ..db import DB
from ..stats import best_score, current_streak, heatmap, longest_streak

BASE = Path(__file__).parent
UPLOADS = settings.data_dir / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="tally")
templates = Jinja2Templates(directory=str(BASE / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS)), name="uploads")
db = DB(settings.db_path)

# make helpers available in templates
templates.env.globals["minsec"] = lambda s: (
    f"{int(s) // 60}:{int(s) % 60:02d}" if s not in (None, "") else "")


def _scorefmt(v) -> str:
    """Whole numbers without decimals, fractional scores to two places (e.g. 7.42)."""
    if v in (None, ""):
        return ""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.2f}"


templates.env.globals["scorefmt"] = _scorefmt


# -- parsing helpers ---------------------------------------------------------
def _num(value) -> Optional[float]:
    value = (str(value) if value is not None else "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _rating(value) -> Optional[int]:
    n = _num(value)
    return None if n is None else max(1, min(5, round(n)))


def _iso_date(value) -> str:
    value = (str(value) if value is not None else "").strip()
    if not value:
        return date.today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
        return date.today().isoformat()


async def _save_upload(upload) -> Optional[str]:
    if upload is None or not getattr(upload, "filename", ""):
        return None
    ext = os.path.splitext(upload.filename)[1].lower() or ".img"
    name = uuid4().hex + ext
    (UPLOADS / name).write_bytes(await upload.read())
    return name


async def _parse(form, hobby: H.Hobby) -> dict:
    """Turn a submitted form into save() kwargs, per the hobby's field schema."""
    out = {"hobby": hobby.key, "title": None, "date": date.today().isoformat(),
           "score": None, "rating": None, "link": None, "image_url": None,
           "image_path": None, "data": {}}
    for f in hobby.fields:
        if f.type == "time":
            mins = _num(form.get(f.key + "_min")) or 0
            secs = _num(form.get(f.key + "_sec")) or 0
            val = int(mins * 60 + secs) or None
        elif f.type == "image":
            path = await _save_upload(form.get(f.key))
            if path:
                out["image_path"] = path
            url = (form.get(f.key + "_url") or "").strip()
            if url:
                out["image_url"] = url
            continue
        else:
            val = (form.get(f.key) or "").strip() or None

        if f.col == "title":
            out["title"] = val
        elif f.col == "score":
            out["score"] = val if f.type == "time" else _num(val)
        elif f.col == "rating":
            out["rating"] = _rating(val)
        elif f.col == "link":
            out["link"] = val
        elif f.col == "date":
            out["date"] = _iso_date(val)
        elif f.col == "data" and val is not None:
            out["data"][f.key] = val
            if f.type == "category":
                db.add_category(val)
    if not out["title"]:
        out["title"] = hobby.label
    return out


def _values(entry: dict, hobby: H.Hobby) -> dict:
    v = {}
    data = entry.get("data") or {}
    for f in hobby.fields:
        if f.col == "title":
            v[f.key] = entry.get("title")
        elif f.col == "score":
            v[f.key] = entry.get("score")
        elif f.col == "rating":
            v[f.key] = entry.get("rating")
        elif f.col == "link":
            v[f.key] = entry.get("link")
        elif f.col == "date":
            v[f.key] = entry.get("date")
        elif f.col == "image":
            v[f.key] = entry.get("image_path") or entry.get("image_url")
        else:
            v[f.key] = data.get(f.key)
    return v


# -- pages -------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def today(request: Request):
    daily = [{"hobby": h, "streak": current_streak(db.dates_for(h.key), date.today())}
             for h in H.daily_hobbies()]
    return templates.TemplateResponse(request, "today.html", {
        "daily": daily, "hobbies": list(H.HOBBIES.values())})


@app.get("/add/{hobby}", response_class=HTMLResponse)
def add_form(request: Request, hobby: str):
    h = H.get(hobby)
    if not h:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "form.html", {
        "hobby": h, "values": {"date": date.today().isoformat()},
        "action": f"/add/{hobby}", "categories": db.categories(), "editing": False})


@app.post("/add/{hobby}")
async def add_submit(request: Request, hobby: str):
    h = H.get(hobby)
    if not h:
        return RedirectResponse("/", status_code=303)
    kw = await _parse(await request.form(), h)
    db.save(**kw)
    return RedirectResponse("/gallery", status_code=303)


@app.get("/edit/{entry_id}", response_class=HTMLResponse)
def edit_form(request: Request, entry_id: int):
    entry = db.get(entry_id)
    if not entry:
        return RedirectResponse("/gallery", status_code=303)
    h = H.get(entry["hobby"])
    return templates.TemplateResponse(request, "form.html", {
        "hobby": h, "values": _values(entry, h), "action": f"/edit/{entry_id}",
        "categories": db.categories(), "editing": True, "entry": entry})


@app.post("/edit/{entry_id}")
async def edit_submit(request: Request, entry_id: int):
    entry = db.get(entry_id)
    if not entry:
        return RedirectResponse("/gallery", status_code=303)
    h = H.get(entry["hobby"])
    kw = await _parse(await request.form(), h)
    db.save(entry_id=entry_id, **kw)
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
            "last": entries[0]["date"] if entries else None})
    hm = heatmap([e["date"] for e in db.entries()], date.today(), days=84)
    return templates.TemplateResponse(request, "tracker.html", {"cards": cards, "heatmap": hm})


@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request, hobby: str = ""):
    entries = db.entries(hobby or None, limit=400)
    return templates.TemplateResponse(request, "gallery.html", {
        "entries": entries, "hobbies": list(H.HOBBIES.values()),
        "active": hobby, "get": H.get})


def main():
    import uvicorn
    uvicorn.run("tally.web.app:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
