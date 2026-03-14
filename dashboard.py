"""
NeuroFocus Dashboard v4.5
=========================
Changes in v4.5:
  • Inline report generation — no dependency on report_generator.py
  • "Build Report" button in sidebar builds the full HTML report from live data
  • st.download_button streams the HTML file directly to the browser
  • Report uses the same clean light-theme HTML as report_generator.py
  • All existing v4.4 functionality preserved unchanged
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json, os, math, re
from datetime import datetime

st.set_page_config(
    page_title="NeuroFocus Attention Intelligence",
    page_icon="🧠", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800;900&display=swap');
:root{
  --bg:#08080f;--bg2:#0f0f1a;--bg3:#16162a;
  --txt:#f0ece4;--txt2:#a89880;--txt3:#5a4a38;
  --amber:#f5a623;--orange:#e8650a;--red:#d42b1e;
  --gold:#f0c040;--green:#4caf50;--cyan:#00e5ff;--purple:#9c6fff;
  --r:10px;--rl:16px;--rxl:20px;
  --fb:'Sora','Segoe UI',Arial,system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0}
html,body,[class*="css"],.stApp{font-family:var(--fb)!important;background:var(--bg)!important;color:var(--txt)!important}
#MainMenu,footer,header{visibility:hidden!important}
.block-container{padding:1.8rem 2.2rem 4rem!important;max-width:1640px!important}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-thumb{background:rgba(245,166,35,.35);border-radius:99px}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid rgba(245,166,35,.12)!important}
section[data-testid="stSidebar"] *{color:var(--txt2)!important;font-family:var(--fb)!important}
.sb-logo{background:linear-gradient(160deg,rgba(245,166,35,.08),rgba(212,43,30,.04));border-bottom:1px solid rgba(245,166,35,.12);padding:1.7rem 1.5rem 1.3rem}
.sb-mark{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;background:linear-gradient(135deg,#f5a623,#d42b1e);border-radius:10px;font-size:1.3rem;margin-bottom:.7rem}
.sb-name{font-size:1.3rem!important;font-weight:800!important;color:var(--txt)!important}
.sb-sub{font-size:12px!important;color:var(--txt3)!important;text-transform:uppercase;letter-spacing:.14em;font-weight:600!important}
.sb-chip{display:inline-block;background:rgba(245,166,35,.1);border:1px solid rgba(245,166,35,.28);color:var(--amber)!important;font-size:12px!important;font-weight:700!important;padding:.12rem .5rem;border-radius:99px;margin-top:.6rem;text-transform:uppercase}
.stRadio>div{gap:1px!important;padding:0 .5rem!important}
.stRadio label{border-radius:var(--r)!important;padding:.5rem .8rem!important;transition:all .15s!important;border:1px solid transparent!important;width:100%}
.stRadio label:hover{background:rgba(255,140,0,.07)!important;border-color:rgba(245,166,35,.2)!important}
.stRadio p{font-size:15px!important;font-weight:600!important}
.stButton>button{background:rgba(245,166,35,.07)!important;border:1px solid rgba(245,166,35,.25)!important;color:var(--amber)!important;border-radius:var(--r)!important;font-size:12px!important;font-weight:700!important;padding:.45rem 1rem!important;width:100%!important;transition:all .2s!important;text-transform:uppercase}
.sb-footer{padding:1.1rem 1.5rem 1.6rem;border-top:1px solid rgba(245,166,35,.1)}
.sb-dot{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;animation:beat 2.4s ease infinite;vertical-align:middle;margin-right:6px}
@keyframes beat{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
.sb-footer p{font-size:12px!important;color:var(--txt3)!important;line-height:1.6!important;font-weight:500!important}
.pg-hdr{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:2rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(245,166,35,.15)}
.pg-eye{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.2em;color:var(--amber);margin-bottom:.4rem}
.pg-title{font-size:30px!important;font-weight:900!important;letter-spacing:-.04em;color:var(--txt)!important;line-height:1.1}
.pg-sub{font-size:15px;color:var(--txt2);margin-top:.3rem;font-weight:500}
.pg-ts{font-size:12px;color:var(--txt3);text-align:right;font-weight:600}
.kg8{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}
.kg3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin-bottom:1.5rem}
.kpi{background:linear-gradient(145deg,var(--bg3),var(--bg2));border:1px solid rgba(255,255,255,.07);border-radius:var(--rxl);padding:1.4rem 1.5rem 1.2rem;position:relative;overflow:hidden;transition:transform .2s;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px))}
.kpi:hover{transform:translateY(-4px);box-shadow:0 8px 32px rgba(245,166,35,.18)}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.kpi::after{content:'';position:absolute;top:0;right:0;width:14px;height:14px;background:var(--bg);clip-path:polygon(0 0,100% 100%,100% 0);z-index:2}
.kb::before{background:linear-gradient(90deg,#f5a623,#e8650a)}.kp::before{background:linear-gradient(90deg,#9c6fff,#d42b1e)}
.kg_::before{background:linear-gradient(90deg,#4caf50,#00e5ff)}.kr::before{background:linear-gradient(90deg,#d42b1e,#8b0000)}
.ka::before{background:linear-gradient(90deg,#f0c040,#f5a623)}.kk::before{background:linear-gradient(90deg,#00e5ff,#9c6fff)}
.kpi-icon{font-size:1.1rem;display:block;margin-bottom:.8rem}
.kpi-lbl{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.15em;color:var(--txt3);margin-bottom:.5rem}
.kpi-val{font-size:36px!important;font-weight:900!important;letter-spacing:-.04em;line-height:1}
.kb .kpi-val{color:#f5a623}.kp .kpi-val{color:#c084fc}.kg_ .kpi-val{color:#4caf50}
.kr .kpi-val{color:#ef5350}.ka .kpi-val{color:#f0c040}.kk .kpi-val{color:#00e5ff}
.kpi-unit{font-size:15px;font-weight:600;color:var(--txt2);margin-left:.25rem}
.kpi-foot{font-size:12px;color:var(--txt3);margin-top:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em}
.sdiv{display:flex;align-items:center;gap:.9rem;margin:2rem 0 1.2rem}
.sdiv-l{flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(245,166,35,.2),transparent)}
.sdiv-t{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.2em;color:var(--txt3);white-space:nowrap;padding:0 .5rem}
.ins{background:linear-gradient(135deg,var(--bg3),var(--bg2));border:1px solid rgba(245,166,35,.12);border-left:3px solid var(--amber);border-radius:0 var(--r) var(--r) 0;padding:.9rem 1.1rem;margin-bottom:.7rem;font-size:15px;color:var(--txt2);line-height:1.6;font-weight:500}
.ins.g{border-left-color:var(--green)}.ins.r{border-left-color:var(--red)}.ins.a{border-left-color:var(--gold)}
.ins strong{color:var(--txt);font-weight:800}
.stat-row{display:flex;gap:.85rem;flex-wrap:wrap;margin-bottom:1.3rem}
.stat-box{flex:1;min-width:120px;background:linear-gradient(145deg,var(--bg3),var(--bg2));border:1px solid rgba(245,166,35,.12);border-radius:var(--rl);padding:1rem 1.1rem}
.stat-box-lbl{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.13em;color:var(--txt3);margin-bottom:.35rem}
.stat-box-val{font-size:24px;font-weight:900;color:var(--amber);line-height:1;letter-spacing:-.03em}
.stat-box-sub{font-size:12px;color:var(--txt3);margin-top:.3rem;font-weight:600}
[data-testid="stDataFrame"]{border-radius:var(--rl)!important;overflow:hidden!important;border:1px solid rgba(245,166,35,.14)!important}
[data-testid="stDataFrame"] thead th{background:var(--bg3)!important;color:var(--amber)!important;font-size:12px!important;font-weight:800!important;text-transform:uppercase!important;letter-spacing:.12em!important}
[data-testid="stDataFrame"] tbody td{font-size:13px!important;color:var(--txt)!important;border-bottom:1px solid rgba(245,166,35,.07)!important;font-weight:500!important}
.nodata{background:var(--bg2);border:1px dashed rgba(245,166,35,.2);border-radius:var(--rl);padding:3.5rem 2rem;text-align:center}
.nodata-ico{font-size:3.2rem;margin-bottom:1.1rem}
.nodata h3{font-size:22px!important;color:var(--txt2)!important;margin-bottom:.5rem!important;font-weight:800!important}
.nodata p{font-size:15px;color:var(--txt3);line-height:1.7;font-weight:500}
.nodata code{background:var(--bg3);border:1px solid rgba(245,166,35,.2);border-radius:5px;padding:.12rem .4rem;font-size:12px;color:var(--amber);font-weight:700}
/* Download button — styled to pop */
[data-testid="stDownloadButton"]>button{
  background:linear-gradient(135deg,rgba(245,166,35,.18),rgba(232,101,10,.12))!important;
  border:1px solid rgba(245,166,35,.55)!important;
  color:#f5a623!important;font-weight:800!important;font-size:13px!important;
  padding:.6rem 1.1rem!important;border-radius:var(--r)!important;
  width:100%!important;letter-spacing:.04em!important;transition:all .2s!important;text-transform:uppercase!important;
}
[data-testid="stDownloadButton"]>button:hover{
  background:linear-gradient(135deg,rgba(245,166,35,.3),rgba(232,101,10,.22))!important;
  box-shadow:0 0 20px rgba(245,166,35,.3)!important;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────
_AX = dict(gridcolor="rgba(245,166,35,.06)", linecolor="rgba(245,166,35,.08)",
           tickfont=dict(size=12, color="#5a4a38", family="Sora,sans-serif"),
           title_font=dict(size=13, color="#a89880", family="Sora,sans-serif"), zeroline=False)
_PT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(family="Sora,sans-serif", color="#a89880", size=12),
           xaxis=_AX, yaxis=_AX, margin=dict(l=44, r=22, t=38, b=44),
           hoverlabel=dict(bgcolor="#1a1a2e", bordercolor="rgba(245,166,35,.4)",
                           font=dict(size=13, color="#f0ece4", family="Sora,sans-serif")))
C_G = "#4caf50"; C_R = "#d42b1e"

def pt(fig, h=360, **kw):
    fig.update_layout(**{**_PT, "height": h, **kw}); return fig

def hex_rgba(h, a):
    h = h.lstrip("#"); r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

# ── App classification ────────────────────────────────────────────────────
_DEEP = ["code","cursor","vscode","visual studio","sublime","pycharm","intellij",
         "notepad++","notepad","vim","emacs","word","excel","powerpoint","docs",
         "sheets","slides","notion","obsidian","figma","photoshop","illustrator",
         "terminal","cmd","powershell","bash","zsh","git","github","gitlab","jira",
         "confluence","linear","claude","chatgpt","copilot","stackoverflow",
         "postman","docker","kubernetes","insomnia","datagrip","rider","clion"]
_DIST = ["youtube","netflix","twitch","tiktok","instagram","facebook","twitter",
         "x.com","reddit","9gag","imgur","tumblr","discord","telegram","whatsapp",
         "messenger","snapchat","steam","epic games","battle.net","spotify",
         "soundcloud","tidal","deezer","buzzfeed","entertainment"]

def classify_app(name: str) -> str:
    low = name.lower()
    for k in _DEEP:
        if k in low: return "deep_work"
    for k in _DIST:
        if k in low: return "distraction"
    return "neutral"

# ── Helpers ───────────────────────────────────────────────────────────────
def fmt_min(m):
    try: m = float(m or 0)
    except: return "0m"
    h = int(m // 60); mn = int(m % 60)
    return f"{h}h {mn}m" if h else f"{mn}m"

def grade(s):
    try: s = float(s)
    except: s = 0
    if s >= 75: return "#4caf50", "EXCELLENT"
    if s >= 55: return "#f5a623", "GOOD"
    if s >= 35: return "#e8650a", "FAIR"
    return "#d42b1e", "NEEDS WORK"

def kpi(icon, lbl, val, unit, foot, cls):
    return (f'<div class="kpi {cls}"><span class="kpi-icon">{icon}</span>'
            f'<div class="kpi-lbl">{lbl}</div>'
            f'<div class="kpi-val">{val}<span class="kpi-unit">{unit}</span></div>'
            f'<div class="kpi-foot">{foot}</div></div>')

def sec(lbl):
    st.markdown(f'<div class="sdiv"><div class="sdiv-l"></div><div class="sdiv-t">{lbl}</div>'
                f'<div class="sdiv-l"></div></div>', unsafe_allow_html=True)

def stat_box(lbl, val, sub):
    return (f'<div class="stat-box"><div class="stat-box-lbl">{lbl}</div>'
            f'<div class="stat-box-val">{val}</div><div class="stat-box-sub">{sub}</div></div>')

def clean_app(name: str) -> str:
    for s in [" - Google Chrome"," - Microsoft Edge"," - Mozilla Firefox"," - Opera"," - Brave"," - Safari"]:
        if name.endswith(s): name = name[:-len(s)]
    for s in [" - Visual Studio Code"," - Sublime Text"," - PyCharm"," - IntelliJ IDEA"," - Notepad++"]:
        if s in name: name = name[:name.index(s)]
    name = re.sub(r"^\(\d+\)\s*", "", name)
    return name.strip(" -·") or name

def xticks(v):
    try: m = re.search(r"ticks:(\d+)", str(v)); return int(m.group(1)) if m else 1
    except: return 1

def xburst(v):
    try: m = re.search(r"burst:(\d+)", str(v)); return int(m.group(1)) if m else 1
    except: return 1

def xnav(v):
    try: m = re.search(r"count:(\d+)", str(v)); return int(m.group(1)) if m else 1
    except: return 1

def xdest(v):
    try:
        s = str(v).strip()
        if "→" in s: return s.split("→", 1)[1].strip()
        return s.lstrip(">").strip()
    except: return str(v)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATA LOADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data(ttl=30)
def load():
    d = {}
    if not os.path.exists("events.csv"):
        return d

    ev = pd.read_csv("events.csv", dtype=str, nrows=100000)
    ev["timestamp"] = pd.to_datetime(ev["timestamp"], errors="coerce")
    ev = ev.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    ev["extra"] = ev["extra"].fillna("")
    ev["event_type"] = ev["event_type"].fillna("unknown")
    ev["application"] = ev["application"].fillna("Unknown").str.strip()
    ev.loc[ev["application"] == "", "application"] = "Unknown"

    kb = ev["event_type"] == "keyboard"
    sw = ev["event_type"] == "scroll"
    wm = ev["event_type"] == "window_switch"
    nv = ev["event_type"] == "navigation"

    ev["key_burst"]    = ev["extra"].where(kb, "0").apply(lambda v: xburst(v) if v != "0" else 0)
    ev["scroll_ticks"] = ev["extra"].where(sw, "0").apply(lambda v: xticks(v) if v != "0" else 0)
    ev["nav_count"]    = ev["extra"].where(nv, "0").apply(lambda v: xnav(v)   if v != "0" else 0)
    ev["switch_dest"]  = ev["extra"].where(wm, "").apply(lambda v: xdest(v) if v != "" else "")

    for col in ["key_burst", "scroll_ticks", "nav_count"]:
        ev[col] = pd.to_numeric(ev[col], errors="coerce").fillna(0).astype(int)
    ev["switch_dest"] = ev["switch_dest"].fillna("")
    d["events"] = ev

    ts0 = ev["timestamp"].iloc[0]; ts1 = ev["timestamp"].iloc[-1]
    wall_min  = round((ts1 - ts0).total_seconds() / 60, 1)
    sess_min  = round(ev["timestamp"].diff().dt.total_seconds().fillna(0).clip(upper=60).sum() / 60, 1)

    total_keys   = int(ev["key_burst"].sum())
    total_scroll = int(ev["scroll_ticks"].sum())
    total_clicks = int((ev["event_type"] == "mouse_click").sum())
    total_sw     = int((ev["event_type"] == "window_switch").sum())
    total_nav    = int(ev["nav_count"].sum())
    total_ev     = len(ev)
    sw_per_hr    = round(total_sw / max(sess_min / 60, 0.01), 1)

    app_time = {}; app_keys = {}; app_scroll = {}; app_clicks = {}; app_sw_out = {}; app_evs = {}
    evr = ev.to_dict("records")
    for i, row in enumerate(evr):
        a = row["application"]; e = row["event_type"]
        app_evs[a] = app_evs.get(a, 0) + 1
        if e == "keyboard":     app_keys[a]   = app_keys.get(a, 0)   + row["key_burst"]
        elif e == "scroll":     app_scroll[a] = app_scroll.get(a, 0) + row["scroll_ticks"]
        elif e == "mouse_click": app_clicks[a] = app_clicks.get(a, 0) + 1
        elif e == "window_switch": app_sw_out[a] = app_sw_out.get(a, 0) + 1
        if i > 0:
            pa  = evr[i - 1]["application"]
            gap = min((row["timestamp"] - evr[i - 1]["timestamp"]).total_seconds(), 60.0)
            app_time[pa] = app_time.get(pa, 0) + gap

    total_active_sec = max(sess_min * 60, 1)
    all_apps = set(app_time) | set(app_evs)
    app_rows = []
    for a in all_apps:
        if a in ("", "Unknown") and app_time.get(a, 0) < 5: continue
        t = app_time.get(a, 0); tm = t / 60; tp = t / total_active_sec * 100
        atype = classify_app(a)
        ks = app_keys.get(a, 0); sc = app_scroll.get(a, 0); cl = app_clicks.get(a, 0)
        sw_o = app_sw_out.get(a, 0); ec = app_evs.get(a, 0); epm = ec / max(tm, 0.01)
        k_s = min(ks / 10, 30); s_s = min(sc / 20, 20); t_s = min(tp * 0.5, 30)
        bon = 20 if atype == "deep_work" else (-10 if atype == "distraction" else 0)
        att = round(max(0, min(100, k_s + s_s + t_s + bon)), 1)
        app_rows.append({"application": clean_app(a), "type": atype,
                         "focus_minutes": round(tm, 2), "focus_pct": round(tp, 2),
                         "events_per_min": round(epm, 2), "keystrokes": ks,
                         "clicks": cl, "scroll_ticks": sc,
                         "context_switches_out": sw_o, "attention_score": att})
    app_rows.sort(key=lambda r: r["focus_minutes"], reverse=True)
    d["app_summary"] = app_rows

    dw_sec   = sum(app_time.get(a, 0) for a in all_apps if classify_app(a) == "deep_work")
    dist_sec = sum(app_time.get(a, 0) for a in all_apps if classify_app(a) == "distraction")
    idle_sec = sum(app_time.get(a, 0) for a in all_apps if "idle" in a.lower() or "screensaver" in a.lower())
    dw_min = dw_sec / 60; dist_min = dist_sec / 60; idle_min = idle_sec / 60
    dw_pct = dw_sec / total_active_sec * 100; dist_pct = dist_sec / total_active_sec * 100
    idle_pct = idle_sec / total_active_sec * 100

    sw_pen = min(sw_per_hr * 0.4, 25)
    score  = round(max(0, min(100, dw_pct * 0.6 - dist_pct * 0.3 - sw_pen + 35)), 1)

    ev["hour_slot"] = ev["timestamp"].dt.strftime("%H:00")
    h_grp = ev.groupby("hour_slot")
    hourly = pd.DataFrame({
        "hour_slot": sorted(ev["hour_slot"].unique()),
        "events":    [int(h_grp.get_group(h)["event_type"].count()) for h in sorted(ev["hour_slot"].unique())],
        "keystrokes":[int(h_grp.get_group(h)["key_burst"].sum())    for h in sorted(ev["hour_slot"].unique())],
        "scroll":    [int(h_grp.get_group(h)["scroll_ticks"].sum()) for h in sorted(ev["hour_slot"].unique())],
        "switches":  [int((h_grp.get_group(h)["event_type"] == "window_switch").sum()) for h in sorted(ev["hour_slot"].unique())],
    })
    d["hourly"] = hourly

    d["report"] = {
        "session_start": ts0.isoformat(), "session_end": ts1.isoformat(),
        "session_minutes": sess_min, "wall_clock_minutes": wall_min,
        "total_events": total_ev, "total_apps_used": len(app_rows),
        "deep_work_minutes": round(dw_min, 1), "distraction_minutes": round(dist_min, 1),
        "idle_minutes": round(idle_min, 1),
        "context_switches": total_sw, "switches_per_hour": sw_per_hr,
        "overall_focus_score": score,
        "focus_breakdown": {"deep_work_pct": round(dw_pct, 1), "distraction_pct": round(dist_pct, 1), "idle_pct": round(idle_pct, 1)},
        "interaction_totals": {"keystrokes": total_keys, "clicks": total_clicks, "scroll_ticks": total_scroll, "nav": total_nav},
    }
    return d


data = load()
he = "events"      in data
hr = "report"      in data
ha = "app_summary" in data
hh = "hourly"      in data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INLINE REPORT BUILDER
#  Builds the same clean light-theme HTML as report_generator.py,
#  using the live data already computed by load() above.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_R_AX = dict(gridcolor="#e8edf5", linecolor="#d0d8e8", zeroline=False,
             tickfont=dict(size=12, color="#6b7a99"),
             title_font=dict(size=13, color="#344563"))
_R_BASE = dict(
    paper_bgcolor="white", plot_bgcolor="#f8f9fa",
    font=dict(family="'Segoe UI',system-ui,sans-serif", color="#344563", size=12),
    hoverlabel=dict(bgcolor="#1a2035", bordercolor="rgba(79,156,249,.4)",
                    font=dict(size=13, color="#e8edf5")),
    margin=dict(l=50, r=30, t=50, b=50),
)

def _rlt(fig, h=300, **kw):
    fig.update_layout(**{**_R_BASE, "height": h, **kw}); return fig

def _bar_h(n, px=52, mn=240, mx=900):
    return max(mn, min(n * px + 120, mx))

def _fig_html(fig, first=True):
    try:
        return fig.to_html(full_html=False,
                           include_plotlyjs="cdn" if first else False,
                           config={"displayModeBar": True, "responsive": True})
    except Exception:
        return "<p><em>Chart unavailable</em></p>"

def _r_grade(s):
    try: s = float(s)
    except: s = 0
    if s >= 75: return "#16a34a", "Excellent"
    if s >= 55: return "#2563eb", "Good"
    if s >= 35: return "#d97706", "Fair"
    return "#dc2626", "Needs Work"

def _timeline_bar(r):
    total = float(r.get("session_minutes", 1) or 1)
    dw   = float(r.get("deep_work_minutes", 0) or 0)
    dist = float(r.get("distraction_minutes", 0) or 0)
    idle = float(r.get("idle_minutes", 0) or 0)
    neut = max(total - dw - dist - idle, 0)
    def pct(v): return round(v / total * 100, 1)
    segs = [(pct(dw),"#16a34a","Deep Work"),(pct(neut),"#4f9cf9","Neutral"),
            (pct(dist),"#dc2626","Distraction"),(pct(idle),"#cbd5e1","Idle")]
    s_html = "".join(f'<div class="tl-seg" style="width:{p}%;background:{c}" title="{l}: {p}%"></div>'
                     for p, c, l in segs if p > 0)
    l_html = "".join(f'<span><span class="tl-dot" style="background:{c}"></span>{l}: {p}%</span>'
                     for p, c, l in segs if p > 0)
    return f'<div class="tl-legend">{l_html}</div><div class="timeline">{s_html}</div>'


def build_report_html(d: dict, title: str = "NeuroFocus Attention Report") -> str:
    """Build the full downloadable HTML report from the live dashboard data dict."""
    r   = d.get("report", {})
    it  = r.get("interaction_totals", {})
    sc  = r.get("overall_focus_score", 0)
    clr, gl = _r_grade(sc)
    fb  = r.get("focus_breakdown", {})
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    ss  = str(r.get("session_start", ""))[:19]
    se  = str(r.get("session_end",   ""))[:19]
    dw_pct   = fb.get("deep_work_pct", 0)
    dist_pct = fb.get("distraction_pct", 0)
    sw_hr    = r.get("switches_per_hour", 0)
    dw_cls   = "green" if dw_pct >= 60 else "amber" if dw_pct >= 35 else "red"
    dist_cls = "red" if dist_pct > 25 else "green"
    sw_cls   = "red" if sw_hr > 30 else "green"
    sw_msg   = ("⚠️ High fragmentation — consider time-blocking." if sw_hr > 30
                else "✅ Good continuity. Healthy context management.")

    # ── Charts ────────────────────────────────────────────────────────────
    charts_html = ""; chart_first = True

    def add(fig):
        nonlocal chart_first, charts_html
        if fig and fig.data:
            charts_html += f'<div class="chart-box">{_fig_html(fig, first=chart_first)}</div>\n'
            chart_first = False

    if "events" in d:
        ev = d["events"]
        # Activity density
        ea = ev[ev["event_type"] != "idle"].copy()
        ea["bucket"] = ea["timestamp"].dt.floor("5min")
        dens = ea.groupby("bucket").size().reset_index(name="count")
        f1 = go.Figure(go.Scatter(x=dens["bucket"], y=dens["count"], mode="lines", fill="tozeroy",
            line=dict(color="#4f9cf9", width=2.5, shape="spline", smoothing=0.7),
            fillcolor="rgba(79,156,249,0.12)",
            hovertemplate="<b>%{x|%H:%M}</b><br>Events: %{y}<extra></extra>"))
        _rlt(f1, h=300, title=dict(text="Activity Density Over Time", font=dict(size=15, color="#1a2035")),
             xaxis={**_R_AX, "title":"Time"}, yaxis={**_R_AX, "title":"Events / 5 min"})
        add(f1)

        # Interaction distribution
        cnts = {"Keystrokes": int(ev["key_burst"].sum()),
                "Mouse Clicks": int((ev["event_type"]=="mouse_click").sum()),
                "Scroll Ticks": int(ev["scroll_ticks"].sum()),
                "Arrow Nav": int(ev["nav_count"].sum()),
                "Window Switch": int((ev["event_type"]=="window_switch").sum()),
                "Idle Events": int((ev["event_type"]=="idle").sum())}
        cnts = {k: v for k, v in cnts.items() if v > 0}
        sc_d = dict(sorted(cnts.items(), key=lambda x: x[1]))
        cmap = {"Keystrokes":"#4f9cf9","Mouse Clicks":"#e8650a","Scroll Ticks":"#3dd68c",
                "Arrow Nav":"#f0c040","Window Switch":"#9b8ef4","Idle Events":"#94a3b8"}
        f2 = go.Figure(go.Bar(x=list(sc_d.values()), y=list(sc_d.keys()), orientation="h",
            marker=dict(color=[cmap.get(k,"#8a9bb8") for k in sc_d], line=dict(width=0)),
            hovertemplate="<b>%{y}</b>: %{x:,}<extra></extra>"))
        _rlt(f2, h=_bar_h(len(sc_d), 46),
             title=dict(text="Interaction Type Distribution", font=dict(size=15, color="#1a2035")),
             xaxis={**_R_AX,"title":"Count"}, yaxis={**_R_AX,"autorange":"reversed"},
             bargap=0.4, margin=dict(l=110, r=60, t=50, b=50))
        add(f2)

        if "app_summary" in d:
            # Keystrokes by app
            ks_rows = sorted(d["app_summary"], key=lambda x: x["keystrokes"], reverse=True)[:12]
            ks_rows = [x for x in ks_rows if x["keystrokes"] > 0]
            if ks_rows:
                apps = [x["application"] for x in ks_rows][::-1]
                vals = [x["keystrokes"]  for x in ks_rows][::-1]
                lm   = min(max(int(max(len(a) for a in apps)*7+20), 160), 480)
                f3 = go.Figure(go.Bar(x=vals, y=apps, orientation="h",
                    marker=dict(color=vals, colorscale=[[0,"#2a0e00"],[0.35,"#e8650a"],[1,"#f5a623"]], line=dict(width=0)),
                    text=[f"  {v:,}" for v in vals], textposition="outside",
                    textfont=dict(size=13, color="#e8650a"),
                    hovertemplate="<b>%{y}</b><br>%{x:,} keystrokes<extra></extra>"))
                _rlt(f3, h=_bar_h(len(apps)),
                     title=dict(text="Keystrokes by App", font=dict(size=15, color="#1a2035")),
                     xaxis={**_R_AX,"title":"Keystrokes"}, yaxis=_R_AX,
                     bargap=0.4, margin=dict(l=lm, r=100, t=50, b=50), showlegend=False)
                add(f3)

            # Scroll by app
            sc_rows2 = sorted(d["app_summary"], key=lambda x: x["scroll_ticks"], reverse=True)[:12]
            sc_rows2 = [x for x in sc_rows2 if x["scroll_ticks"] > 0]
            if sc_rows2:
                apps = [x["application"]  for x in sc_rows2][::-1]
                vals = [x["scroll_ticks"] for x in sc_rows2][::-1]
                lm   = min(max(int(max(len(a) for a in apps)*7+20), 160), 480)
                f4 = go.Figure(go.Bar(x=vals, y=apps, orientation="h",
                    marker=dict(color=vals, colorscale=[[0,"#1a0830"],[0.45,"#6a2fbf"],[1,"#9b8ef4"]], line=dict(width=0)),
                    hovertemplate="<b>%{y}</b><br>Ticks: %{x:,}<extra></extra>"))
                _rlt(f4, h=_bar_h(len(apps)),
                     title=dict(text="Scroll Volume by App", font=dict(size=15, color="#1a2035")),
                     xaxis={**_R_AX,"title":"Scroll Ticks"}, yaxis=_R_AX,
                     bargap=0.4, margin=dict(l=lm, r=80, t=50, b=50), showlegend=False)
                add(f4)

            # Clicks by app
            cl_rows = sorted(d["app_summary"], key=lambda x: x["clicks"], reverse=True)[:12]
            cl_rows = [x for x in cl_rows if x["clicks"] > 0]
            if cl_rows:
                apps = [x["application"] for x in cl_rows][::-1]
                vals = [x["clicks"]       for x in cl_rows][::-1]
                lm   = min(max(int(max(len(a) for a in apps)*7+20), 160), 480)
                f5 = go.Figure(go.Bar(x=vals, y=apps, orientation="h",
                    marker=dict(color=vals, colorscale=[[0,"#052a1a"],[0.35,"#1e8a50"],[1,"#3dd68c"]], line=dict(width=0)),
                    text=[f"  {v:,}" for v in vals], textposition="outside",
                    textfont=dict(size=13, color="#16a34a"),
                    hovertemplate="<b>%{y}</b><br>%{x:,} clicks<extra></extra>"))
                _rlt(f5, h=_bar_h(len(apps)),
                     title=dict(text="Mouse Clicks by App", font=dict(size=15, color="#1a2035")),
                     xaxis={**_R_AX,"title":"Clicks"}, yaxis=_R_AX,
                     bargap=0.4, margin=dict(l=lm, r=100, t=50, b=50), showlegend=False)
                add(f5)

        # Context switch timeline
        sw_ev = ev[ev["event_type"] == "window_switch"].copy()
        if not sw_ev.empty:
            sw_ev["bucket"] = sw_ev["timestamp"].dt.floor("5min")
            sw_b = sw_ev.groupby("bucket").size().reset_index(name="switches")
            f6 = go.Figure(go.Bar(x=sw_b["bucket"], y=sw_b["switches"],
                marker=dict(color=sw_b["switches"],
                    colorscale=[[0,"#fff7ed"],[0.5,"#fb923c"],[1,"#dc2626"]], line=dict(width=0)),
                hovertemplate="<b>%{x|%H:%M}</b><br>%{y} switches<extra></extra>"))
            _rlt(f6, h=260,
                 title=dict(text="Context Switch Frequency (5-min buckets)", font=dict(size=15, color="#1a2035")),
                 xaxis={**_R_AX,"title":"Time"}, yaxis={**_R_AX,"title":"Switches"})
            add(f6)

    # ── Hourly section ────────────────────────────────────────────────────
    hourly_section = ""
    if "hourly" in d:
        hdf = d["hourly"]
        if not hdf.empty:
            hf = go.Figure(go.Bar(x=hdf["hour_slot"], y=hdf["events"],
                marker=dict(color=hdf["events"],
                    colorscale=[[0,"#e8f4fd"],[0.5,"#4f9cf9"],[1,"#1d4ed8"]], line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>Events: %{y:,}<extra></extra>"))
            _rlt(hf, h=260,
                 title=dict(text="Activity by Hour of Day", font=dict(size=15, color="#1a2035")),
                 xaxis={**_R_AX,"title":"Hour"}, yaxis={**_R_AX,"title":"Total Events"})
            hourly_section = f"""
            <div class="section">
              <div class="section-header"><span class="section-icon">🕐</span>
                <div class="section-title">Hourly Activity Patterns</div></div>
              <div class="chart-box">{_fig_html(hf, first=chart_first)}</div>
            </div>"""
            chart_first = False

    # ── App table ─────────────────────────────────────────────────────────
    focus_table_html = ""
    if "app_summary" in d:
        rows_html = ""
        for row in d["app_summary"]:
            atype     = row.get("type", "neutral")
            badge_cls = {"deep_work":"badge-green","distraction":"badge-red"}.get(atype, "badge-blue")
            label     = atype.replace("_", " ").title()
            score     = float(row.get("attention_score", 0))
            bar_w     = int(min(score, 100))
            bar_clr   = "#16a34a" if score >= 60 else "#d97706" if score >= 35 else "#dc2626"
            rows_html += (f"<tr><td>{row.get('application','')}</td>"
                          f"<td><span class='badge {badge_cls}'>{label}</span></td>"
                          f"<td>{float(row.get('focus_minutes',0)):.1f} min</td>"
                          f"<td>{float(row.get('focus_pct',0)):.1f}%</td>"
                          f"<td>{int(row.get('clicks',0)):,}</td>"
                          f"<td>{int(row.get('keystrokes',0)):,}</td>"
                          f"<td>{int(row.get('scroll_ticks',0)):,}</td>"
                          f"<td><div class='score-bar-wrap'>"
                          f"<div class='score-bar' style='width:{bar_w}%;background:{bar_clr}'></div>"
                          f"<span class='score-bar-lbl'>{score:.0f}</span></div></td></tr>")
        focus_table_html = (
            "<table class='data-table'><thead><tr>"
            "<th>Application</th><th>Type</th><th>Time</th><th>Share</th>"
            "<th>Clicks</th><th>Keys</th><th>Scrolls</th><th>Score /100</th>"
            f"</tr></thead><tbody>{rows_html}</tbody></table>")

    # ── Context switch table ──────────────────────────────────────────────
    sw_table_html = "<p class='no-data'>No window switch events recorded.</p>"
    if "events" in d:
        sw2 = d["events"][d["events"]["event_type"] == "window_switch"].copy()
        if not sw2.empty:
            sw2["from_a"] = sw2["application"].apply(clean_app)
            sw2["to_a"]   = sw2["switch_dest"].apply(clean_app)
            pairs = (sw2.groupby(["from_a","to_a"]).size()
                       .reset_index(name="count")
                       .sort_values("count", ascending=False)
                       .head(25))
            pairs = pairs[(pairs["from_a"] != pairs["to_a"]) & (pairs["to_a"] != "")]
            if not pairs.empty:
                rh = "".join(f"<tr><td>{row['from_a']}</td><td>→</td><td>{row['to_a']}</td>"
                             f"<td style='text-align:center;font-weight:700;color:#4f9cf9'>{row['count']}</td></tr>"
                             for _, row in pairs.iterrows())
                sw_table_html = (
                    "<table class='data-table'><thead><tr>"
                    "<th>From</th><th></th><th>To</th><th>Count</th>"
                    f"</tr></thead><tbody>{rh}</tbody></table>")

    # ── Raw event log ─────────────────────────────────────────────────────
    raw_html = "<p class='no-data'>No event data available.</p>"
    if "events" in d:
        ev_s = d["events"][["timestamp","event_type","application"]].tail(150).copy()
        ev_s["timestamp"] = ev_s["timestamp"].dt.strftime("%H:%M:%S")
        tbadge = {"keyboard":"badge-blue","mouse_click":"badge-green","scroll":"badge-purple",
                  "window_switch":"badge-orange","idle":"badge-gray","navigation":"badge-teal"}
        rh3 = "".join(
            f"<tr><td class='mono'>{row['timestamp']}</td>"
            f"<td><span class='badge {tbadge.get(row['event_type'],'badge-gray')}'>{row['event_type']}</span></td>"
            f"<td>{clean_app(str(row['application']))}</td></tr>"
            for _, row in ev_s.iterrows())
        raw_html = (
            "<table class='data-table'><thead><tr>"
            "<th>Timestamp</th><th>Event Type</th><th>Application</th>"
            f"</tr></thead><tbody>{rh3}</tbody></table>")

    # ── Assemble ──────────────────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;background:#f0f4f8;color:#1a2035;line-height:1.6}}
.header{{background:linear-gradient(135deg,#03050a 0%,#0d1425 55%,#1a2540 100%);color:#e8edf5;padding:3rem 4rem 2.5rem;position:relative;overflow:hidden}}
.header::before{{content:'';position:absolute;top:-60px;right:-60px;width:350px;height:350px;background:radial-gradient(circle,rgba(79,156,249,.12) 0%,transparent 70%)}}
.header-badge{{display:inline-block;background:rgba(79,156,249,.15);border:1px solid rgba(79,156,249,.35);color:#7ab8fb;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.2em;padding:.25rem .9rem;border-radius:99px;margin-bottom:.9rem}}
.header-title{{font-size:2.6rem;font-weight:800;letter-spacing:-.04em;line-height:1.1;margin-bottom:.7rem;background:linear-gradient(135deg,#e8edf5 30%,#8a9bb8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.header-meta{{font-size:.88rem;color:#8a9bb8;display:flex;flex-wrap:wrap;gap:1.2rem;align-items:center}}
.header-meta strong{{color:#c8d4e8}}
.score-pill{{display:inline-flex;align-items:center;gap:.4rem;background:{clr}22;border:1px solid {clr}55;color:{clr};font-size:.82rem;font-weight:700;padding:.22rem .8rem;border-radius:99px}}
.score-dot{{width:8px;height:8px;background:{clr};border-radius:50%}}
.container{{max-width:1140px;margin:0 auto;padding:2.5rem}}
.section{{margin-bottom:2.8rem}}
.section-header{{display:flex;align-items:center;gap:.8rem;margin-bottom:1.4rem;padding-bottom:.65rem;border-bottom:2px solid #e2e8f0}}
.section-icon{{font-size:1.25rem}}.section-title{{font-size:.82rem;font-weight:800;text-transform:uppercase;letter-spacing:.14em;color:#64748b}}
.kpi-grid-8{{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin-bottom:1.4rem}}
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin-bottom:1.4rem}}
.kpi-card{{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:1.25rem 1.3rem;position:relative;overflow:hidden}}
.kpi-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#4f9cf9,#9b8ef4);border-radius:16px 16px 0 0}}
.kpi-card.green::before{{background:linear-gradient(90deg,#16a34a,#4ade80)}}
.kpi-card.red::before{{background:linear-gradient(90deg,#dc2626,#f87171)}}
.kpi-card.purple::before{{background:linear-gradient(90deg,#7c3aed,#a78bfa)}}
.kpi-card.amber::before{{background:linear-gradient(90deg,#d97706,#fbbf24)}}
.kpi-card.cyan::before{{background:linear-gradient(90deg,#0891b2,#22d3ee)}}
.kpi-label{{font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:.4rem}}
.kpi-value{{font-size:2rem;font-weight:800;color:#1a2035;letter-spacing:-.03em;line-height:1.1}}
.kpi-card.green .kpi-value{{color:#16a34a}}.kpi-card.red .kpi-value{{color:#dc2626}}
.kpi-card.purple .kpi-value{{color:#7c3aed}}.kpi-card.amber .kpi-value{{color:#d97706}}.kpi-card.cyan .kpi-value{{color:#0891b2}}
.kpi-foot{{font-size:.7rem;color:#94a3b8;margin-top:.35rem;font-weight:500}}
.insight{{background:#eff6ff;border-left:3px solid #3b82f6;border-radius:0 10px 10px 0;padding:.85rem 1.1rem;margin-bottom:.7rem;font-size:.88rem;color:#1e3a5f;font-weight:500}}
.insight.green{{background:#f0fdf4;border-left-color:#16a34a;color:#14532d}}
.insight.red{{background:#fef2f2;border-left-color:#dc2626;color:#7f1d1d}}
.insight.amber{{background:#fffbeb;border-left-color:#d97706;color:#78350f}}
.insight strong{{font-weight:800}}
.chart-box{{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:1rem;margin-bottom:1.2rem;overflow:hidden}}
.table-wrap{{background:white;border:1px solid #e2e8f0;border-radius:14px;overflow:hidden}}
.data-table{{width:100%;border-collapse:collapse;font-size:.84rem}}
.data-table thead th{{background:#1a2035;color:#e8edf5;padding:.75rem 1rem;text-align:left;font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;font-weight:700}}
.data-table tbody td{{padding:.6rem 1rem;border-bottom:1px solid #f1f5f9;color:#334155;vertical-align:middle}}
.data-table tbody tr:last-child td{{border-bottom:none}}
.data-table tbody tr:hover td{{background:#f8fafc}}
.badge{{display:inline-block;padding:.18rem .62rem;border-radius:99px;font-size:.7rem;font-weight:700}}
.badge-green{{background:#dcfce7;color:#16a34a}}.badge-red{{background:#fee2e2;color:#dc2626}}
.badge-blue{{background:#dbeafe;color:#2563eb}}.badge-purple{{background:#ede9fe;color:#7c3aed}}
.badge-orange{{background:#ffedd5;color:#c2410c}}.badge-gray{{background:#f1f5f9;color:#64748b}}.badge-teal{{background:#ccfbf1;color:#0f766e}}
.score-bar-wrap{{display:flex;align-items:center;gap:.5rem}}
.score-bar{{height:6px;border-radius:99px;flex:1;max-width:80px}}
.score-bar-lbl{{font-size:.78rem;font-weight:700;color:#64748b;min-width:24px}}
.mono{{font-family:'Consolas','Courier New',monospace;font-size:.82rem}}
.no-data{{color:#94a3b8;font-size:.88rem;padding:1rem 0;font-style:italic}}
.timeline{{display:flex;height:36px;background:white;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;margin-bottom:1.4rem}}
.tl-seg{{height:100%;min-width:4px}}
.tl-legend{{display:flex;gap:1.2rem;flex-wrap:wrap;font-size:.78rem;color:#64748b;margin-bottom:1rem}}
.tl-dot{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:.35rem;vertical-align:middle}}
.footer{{background:#1a2035;color:#64748b;padding:1.5rem 3rem;text-align:center;font-size:.78rem;margin-top:.5rem}}
.footer strong{{color:#94a3b8}}
@media(max-width:900px){{.kpi-grid,.kpi-grid-8{{grid-template-columns:repeat(2,1fr)}}.header{{padding:2rem 1.5rem}}.container{{padding:1.5rem}}}}
</style>
</head>
<body>
<div class="header">
  <div class="header-badge">🧠 NeuroFocus · Attention Intelligence</div>
  <div class="header-title">{title}</div>
  <div class="header-meta">
    <span><strong>Date:</strong> {ss[:10]}</span>
    <span><strong>Start:</strong> {ss[11:]}</span>
    <span><strong>End:</strong> {se[11:]}</span>
    <span><strong>Active:</strong> {fmt_min(r.get("session_minutes",0))}</span>
    <span><strong>Wall-clock:</strong> {fmt_min(r.get("wall_clock_minutes",0))}</span>
    <span><strong>Generated:</strong> {now}</span>
    <span><div class="score-pill"><div class="score-dot"></div>Focus Score: {sc:.0f}/100 — {gl}</div></span>
  </div>
</div>
<div class="container">
  <div class="section">
    <div class="section-header"><span class="section-icon">📊</span><div class="section-title">Session Overview</div></div>
    {_timeline_bar(r)}
    <div class="kpi-grid-8">
      <div class="kpi-card"><div class="kpi-label">Active Time</div><div class="kpi-value">{fmt_min(r.get("session_minutes",0))}</div><div class="kpi-foot">Idle gaps excluded</div></div>
      <div class="kpi-card"><div class="kpi-label">Wall-Clock</div><div class="kpi-value">{fmt_min(r.get("wall_clock_minutes",0))}</div><div class="kpi-foot">Total elapsed</div></div>
      <div class="kpi-card green"><div class="kpi-label">Deep Work</div><div class="kpi-value">{fmt_min(r.get("deep_work_minutes",0))}</div><div class="kpi-foot">{dw_pct:.1f}% of session</div></div>
      <div class="kpi-card red"><div class="kpi-label">Distraction</div><div class="kpi-value">{fmt_min(r.get("distraction_minutes",0))}</div><div class="kpi-foot">{dist_pct:.1f}% of session</div></div>
      <div class="kpi-card purple"><div class="kpi-label">Focus Score</div><div class="kpi-value">{sc:.0f}<span style="font-size:1rem;color:#94a3b8">/100</span></div><div class="kpi-foot">{gl}</div></div>
      <div class="kpi-card cyan"><div class="kpi-label">Context Switches</div><div class="kpi-value">{r.get("context_switches",0)}</div><div class="kpi-foot">{sw_hr:.1f} per hour</div></div>
      <div class="kpi-card amber"><div class="kpi-label">Total Events</div><div class="kpi-value">{r.get("total_events",0):,}</div><div class="kpi-foot">Recorded interactions</div></div>
      <div class="kpi-card"><div class="kpi-label">Apps Used</div><div class="kpi-value">{r.get("total_apps_used",0)}</div><div class="kpi-foot">Unique applications</div></div>
    </div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">⌨️</span><div class="section-title">Input Totals</div></div>
    <div class="kpi-grid">
      <div class="kpi-card amber"><div class="kpi-label">Keystrokes</div><div class="kpi-value">{it.get("keystrokes",0):,}</div><div class="kpi-foot">Burst-decoded</div></div>
      <div class="kpi-card green"><div class="kpi-label">Mouse Clicks</div><div class="kpi-value">{it.get("clicks",0):,}</div><div class="kpi-foot">Individual clicks</div></div>
      <div class="kpi-card purple"><div class="kpi-label">Scroll Ticks</div><div class="kpi-value">{it.get("scroll_ticks",0):,}</div><div class="kpi-foot">Real scroll distance</div></div>
      <div class="kpi-card cyan"><div class="kpi-label">Idle Minutes</div><div class="kpi-value">{fmt_min(r.get("idle_minutes",0))}</div><div class="kpi-foot">{fb.get("idle_pct",0):.1f}% of wall-clock</div></div>
    </div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">🎯</span><div class="section-title">Focus Analysis & Insights</div></div>
    <div class="insight {dw_cls}"><strong>Deep Work Ratio:</strong> {dw_pct:.1f}% of session — {fmt_min(r.get("deep_work_minutes",0))} of focused work.</div>
    <div class="insight {dist_cls}"><strong>Distraction Level:</strong> {dist_pct:.1f}% off-task — {fmt_min(r.get("distraction_minutes",0))} total. {"Consider blocking distracting sites." if dist_pct>25 else "Great job keeping distractions low."}</div>
    <div class="insight"><strong>Idle Time:</strong> {fb.get("idle_pct",0):.1f}% of wall-clock — {fmt_min(r.get("idle_minutes",0))} in idle periods.</div>
    <div class="insight {sw_cls}"><strong>Context Switching:</strong> {sw_hr:.1f} switches/hr — {sw_msg}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">📈</span><div class="section-title">Interaction Charts</div></div>
    {charts_html if charts_html else "<p class='no-data'>No event data for charts.</p>"}
  </div>
  {hourly_section}
  <div class="section">
    <div class="section-header"><span class="section-icon">🖥</span><div class="section-title">Application Breakdown</div></div>
    <div class="table-wrap">{focus_table_html or "<p class='no-data' style='padding:1rem'>No app data.</p>"}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">🔀</span><div class="section-title">Context Switching — Top Transitions</div></div>
    <div class="insight {sw_cls}"><strong>Switch Rate:</strong> {sw_hr:.1f} switches/hr across {r.get("context_switches",0)} total in {fmt_min(r.get("session_minutes",0))}.</div>
    <div class="table-wrap">{sw_table_html}</div>
  </div>
  <div class="section">
    <div class="section-header"><span class="section-icon">🗂</span><div class="section-title">Raw Event Log (last 150)</div></div>
    <div class="table-wrap">{raw_html}</div>
  </div>
</div>
<div class="footer">
  <strong>NeuroFocus v4.5</strong> &nbsp;·&nbsp; 100% Offline &nbsp;·&nbsp; No cloud &nbsp;·&nbsp; No telemetry &nbsp;·&nbsp; Generated {now}
</div>
</body>
</html>"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("""<div class="sb-logo">
      <div class="sb-mark">🧠</div>
      <div class="sb-name">NeuroFocus</div>
      <div class="sb-sub">Attention Intelligence</div>
      <div class="sb-chip">Offline</div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("nav", ["📊  Overview","🎯  Focus Analysis","🖱  Scroll & Input",
                             "🔀  Context Switching","🖥  Raw Data"], label_visibility="collapsed")

    st.markdown("<div style='height:1px;background:rgba(245,166,35,.1);margin:.9rem 1.2rem'></div>",
                unsafe_allow_html=True)
    show_idle = st.checkbox("Include idle apps", value=False)
    if st.button("↺  Refresh Data"):
        st.cache_data.clear(); st.rerun()

    # ── Export Report ─────────────────────────────────────────────────────
    st.markdown("<div style='height:1px;background:rgba(245,166,35,.1);margin:.9rem 1.2rem'></div>",
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:11px;font-weight:800;text-transform:uppercase;"
        "letter-spacing:.18em;color:#5a4a38;padding:0 .3rem .6rem'>📄 Export Report</div>",
        unsafe_allow_html=True)

    if data:
        report_title = st.text_input(
            "title", value="NeuroFocus Attention Report",
            label_visibility="collapsed", placeholder="Report title…")

        # Invalidate cached HTML when title changes
        if st.session_state.get("_report_title") != report_title:
            st.session_state["_report_html"]  = None
            st.session_state["_report_title"] = report_title

        if st.button("🔨  Build Report"):
            with st.spinner("Building report with all charts…"):
                st.session_state["_report_html"] = build_report_html(data, title=report_title)
            st.success("✅ Report ready — download below!")

        if st.session_state.get("_report_html"):
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥  Download HTML Report",
                data=st.session_state["_report_html"].encode("utf-8"),
                file_name=f"neurofocus_report_{ts_str}.html",
                mime="text/html",
            )
            st.markdown(
                "<div style='font-size:11px;color:#5a4a38;padding:.4rem .2rem;line-height:1.6'>"
                "💡 Open in browser → File → Print → Save as PDF</div>",
                unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='font-size:12px;color:#5a4a38;padding:.3rem'>No session data loaded yet.</div>",
            unsafe_allow_html=True)

    st.markdown("""<div class="sb-footer">
      <p><span class="sb-dot"></span> All data stays on your device</p>
      <p>No cloud · No telemetry · 100% private</p>
    </div>""", unsafe_allow_html=True)

if not data:
    st.markdown("""<div class="nodata">
      <div class="nodata-ico">🧠</div>
      <h3>No session data yet</h3>
      <p>Run <code>python monitor.py</code> · work normally · press CTRL+C<br>
      Then run <code>python analysis.py</code> and refresh.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE 1 — OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if page == "📊  Overview":
    ts = datetime.now().strftime("%A %d %B %Y  ·  %H:%M")
    st.markdown(f"""<div class="pg-hdr"><div>
      <div class="pg-title">Overview Scoreboard</div>
    </div><div class="pg-ts">{ts}</div></div>""", unsafe_allow_html=True)

    r = data["report"]; it = r["interaction_totals"]; sc = r["overall_focus_score"]; _, gl = grade(sc)
    st.markdown(f"""<div class="kg8">
      {kpi("⏳","Total Monitoring",   fmt_min(r["session_minutes"]),    "","Active (capped) time","kb")}
      {kpi("🎯","Focused Productive", fmt_min(r["deep_work_minutes"]),   "","Deep work time","kg_")}
      {kpi("📵","Off-Task Apps",      fmt_min(r["distraction_minutes"]), "","Distraction time","kr")}
      {kpi("⚡","Total Events",       f'{r["total_events"]:,}',          "","Interaction events","ka")}
      {kpi("🏆","Focus Score",        f'{sc:.0f}',                       "/100", gl,"kp")}
      {kpi("📜","Scroll Distance",    f'{it["scroll_ticks"]:,}',         " ticks","Real scroll distance","kk")}
      {kpi("⌨️","Keystrokes",        f'{it["keystrokes"]:,}',           "","Actual keys recorded","kb")}
      {kpi("🔀","Window Switches",    f'{r["context_switches"]}',        "",f'{r["switches_per_hour"]}/hr',"kp")}
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.3, 1.15])
    with c1:
        fc, gl2 = grade(sc)
        def arc(pct, ri=0.54, ro=0.71):
            a0 = math.pi; a1 = math.pi + max(0, min(100, pct)) / 100 * math.pi
            po = [(ro*math.cos(a0+i*(a1-a0)/60)+0.5, ro*math.sin(a0+i*(a1-a0)/60)+0.47) for i in range(61)]
            pi_ = [(ri*math.cos(a1-i*(a1-a0)/60)+0.5, ri*math.sin(a1-i*(a1-a0)/60)+0.47) for i in range(61)]
            return [p[0] for p in po+pi_], [p[1] for p in po+pi_]
        ang = [math.pi + i*math.pi/120 for i in range(121)]
        bgp = ("M " + " L ".join(f"{0.71*math.cos(a)+0.5:.4f},{0.71*math.sin(a)+0.47:.4f}" for a in ang)
               + " L " + " L ".join(f"{0.54*math.cos(a)+0.5:.4f},{0.54*math.sin(a)+0.47:.4f}" for a in reversed(ang)) + " Z")
        xs, ys = arc(sc); ap = "M " + " L ".join(f"{x:.4f},{y:.4f}" for x,y in zip(xs,ys)) + " Z"
        fig_g = go.Figure()
        fig_g.add_shape(type="path", path=bgp, fillcolor="rgba(255,255,255,0.05)", line=dict(width=0), xref="paper", yref="paper")
        fig_g.add_shape(type="path", path=ap,  fillcolor=fc, line=dict(width=0), xref="paper", yref="paper")
        fig_g.add_annotation(text=f"<span style='font-size:40px;font-weight:900;color:#f0ece4;font-family:Sora,sans-serif'>{sc:.0f}</span>",
                             x=0.5, y=0.3, showarrow=False, xref="paper", yref="paper")
        fig_g.add_annotation(text=f"<span style='font-size:12px;color:{fc};font-weight:800;font-family:Sora,sans-serif;letter-spacing:2px'>{gl2}</span>",
                             x=0.5, y=0.08, showarrow=False, xref="paper", yref="paper")
        fig_g.add_annotation(text="<span style='font-size:10px;color:#4a3a28;letter-spacing:3px;font-family:Sora,sans-serif;font-weight:700'>FOCUS SCORE</span>",
                             x=0.5, y=-0.1, showarrow=False, xref="paper", yref="paper")
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=10, b=20), height=230,
                            xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig_g, width="stretch")

    with c2:
        tot = r["session_minutes"]; dw = r["deep_work_minutes"]
        di = r["distraction_minutes"]; idl = r["idle_minutes"]; neut = max(tot-dw-di-idl, 0)
        fig_d = go.Figure(go.Pie(
            labels=["Deep Work","Distraction","Idle","Neutral"],
            values=[max(dw,0), max(di,0), max(idl,0), max(neut,0)], hole=0.64,
            marker=dict(colors=[C_G, C_R, "#2a1a0a","#1a0a00"], line=dict(color="#08080f", width=3)),
            textfont=dict(size=12, family="Sora,sans-serif"),
            hovertemplate="<b>%{label}</b><br>%{value:.1f} min · %{percent}<extra></extra>",
            direction="clockwise", sort=False))
        fig_d.add_annotation(
            text=(f"<span style='font-size:22px;font-weight:900;color:#f0ece4;font-family:Sora,sans-serif'>{fmt_min(tot)}</span><br>"
                  "<span style='font-size:10px;color:#4a3a28;letter-spacing:3px;font-family:Sora,sans-serif;font-weight:700'>SESSION</span>"),
            x=0.5, y=0.5, showarrow=False, align="center")
        pt(fig_d, h=240,
           legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12, family="Sora,sans-serif")),
           margin=dict(l=10, r=90, t=20, b=20))
        st.plotly_chart(fig_d, width="stretch")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE 2 — FOCUS ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🎯  Focus Analysis":
    st.markdown("""<div class="pg-hdr"><div>
      <div class="pg-eye"></div><div class="pg-title">Focus Analysis</div>
    </div></div>""", unsafe_allow_html=True)

    if not he:
        st.markdown('<div class="nodata"><div class="nodata-ico">📊</div><h3>No event data</h3>'
                    '<p>Run <code>python monitor.py</code> first.</p></div>', unsafe_allow_html=True)
        st.stop()

    ev = data["events"]

    sec("Activity Density (5-min buckets)")
    ea = ev[ev["event_type"] != "idle"].copy()
    ea["bucket"] = ea["timestamp"].dt.floor("5min")
    dens = ea.groupby("bucket").size().reset_index(name="count")
    fig_d = go.Figure(go.Scatter(x=dens["bucket"], y=dens["count"], mode="lines", fill="tozeroy",
        line=dict(color="#f5a623", width=2.5, shape="spline", smoothing=0.7),
        fillcolor=hex_rgba("#f5a623", 0.08),
        hovertemplate="<b>%{x|%H:%M}</b><br>Events: %{y}<extra></extra>"))
    pt(fig_d, h=240, xaxis_title="Time", yaxis_title="Events / 5 min")
    st.plotly_chart(fig_d, width="stretch")

    sec("Interaction Type Distribution")
    cnts = {"Keystrokes": int(ev["key_burst"].sum()), "Mouse Clicks": int((ev["event_type"]=="mouse_click").sum()),
            "Scroll Ticks": int(ev["scroll_ticks"].sum()), "Arrow Nav": int(ev["nav_count"].sum()),
            "Window Switch": int((ev["event_type"]=="window_switch").sum()), "Idle": int((ev["event_type"]=="idle").sum())}
    cnts = {k: v for k, v in cnts.items() if v > 0}
    cmap = {"Keystrokes":"#f5a623","Mouse Clicks":"#e8650a","Scroll Ticks":"#4caf50",
            "Arrow Nav":"#f0c040","Window Switch":"#9c6fff","Idle":"#4a3a28"}
    sc_d = dict(sorted(cnts.items(), key=lambda x: x[1]))
    fig_e = go.Figure(go.Bar(x=list(sc_d.values()), y=list(sc_d.keys()), orientation="h",
        marker=dict(color=[cmap.get(k,"#8a9bb8") for k in sc_d], line=dict(width=0)),
        text=[f"  {v:,}" for v in sc_d.values()], textposition="outside",
        textfont=dict(color="#f0ece4", size=12),
        hovertemplate="<b>%{y}</b>: %{x:,}<extra></extra>"))
    pt(fig_e, h=max(220, len(sc_d)*55), xaxis_title="Count",
       yaxis={**_AX,"autorange":"reversed"}, margin=dict(l=110, r=80, t=38, b=44))
    st.plotly_chart(fig_e, width="stretch")

    sec("Application Intelligence Table")
    if ha:
        rows = data["app_summary"]
        if not show_idle:
            rows = [r for r in rows if "idle" not in r["application"].lower()
                    and "screensaver" not in r["application"].lower()]
        df = pd.DataFrame(rows)
        badge = {"deep_work":"🟢 deep work","distraction":"🔴 distraction","neutral":"⚪ neutral"}
        df["type"] = df["type"].map(badge).fillna(df["type"])
        ren = {"application":"App","type":"Type","focus_minutes":"Min","focus_pct":"Share%",
               "events_per_min":"Ev/min","keystrokes":"Keys","clicks":"Clicks",
               "scroll_ticks":"Scrolls","context_switches_out":"Switches","attention_score":"Score"}
        df = df.rename(columns=ren)
        for col in ["Min","Share%","Ev/min"]:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").round(1)
        cfg = {}
        if "Score"  in df.columns: cfg["Score"]  = st.column_config.ProgressColumn("Score",  min_value=0, max_value=100, format="%.0f")
        if "Share%" in df.columns: cfg["Share%"] = st.column_config.ProgressColumn("Share%", min_value=0, max_value=100, format="%.1f%%")
        st.dataframe(df, width="stretch", hide_index=True, column_config=cfg)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE 3 — SCROLL & INPUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🖱  Scroll & Input":
    st.markdown("""<div class="pg-hdr"><div>
      <div class="pg-eye"></div><div class="pg-title">Scroll & Input Analysis</div>
    </div></div>""", unsafe_allow_html=True)

    if not he:
        st.markdown('<div class="nodata"><div class="nodata-ico">🖱</div><h3>No event data</h3>'
                    '<p>Run <code>python monitor.py</code> first.</p></div>', unsafe_allow_html=True)
        st.stop()

    ev = data["events"]; r = data["report"]; it = r["interaction_totals"]
    st.markdown(f"""<div class="kg3">
      {kpi("📜","Scroll Ticks", f'{it["scroll_ticks"]:,}',"","Real scroll distance","kp")}
      {kpi("⌨️","Keystrokes",  f'{it["keystrokes"]:,}',  "","Burst-decoded keystrokes","kb")}
      {kpi("🖱","Mouse Clicks", f'{it["clicks"]:,}',       "","Individual click events","kg_")}
    </div>""", unsafe_allow_html=True)

    sc_rows = int((ev["event_type"]=="scroll").sum())
    avg_t   = round(it["scroll_ticks"] / max(sc_rows, 1), 1)
    st.markdown(f"""<div class="stat-row">
      {stat_box("Scroll Event Rows", str(sc_rows), "Batched scroll entries")}
      {stat_box("Avg Ticks/Event",   str(avg_t),   "Ticks per batch")}
      {stat_box("Window Switches",   str(r["context_switches"]), "App context changes")}
    </div>""", unsafe_allow_html=True)

    def _lm(labs): return min(max(int(max(len(str(l)) for l in labs)*7+20), 160), 480)

    if ha:
        sec("Scroll Volume by App")
        rows = sorted(data["app_summary"], key=lambda x: x["scroll_ticks"], reverse=True)[:12]
        rows = [r for r in rows if r["scroll_ticks"] > 0]
        if rows:
            apps = [r["application"] for r in rows][::-1]; vals = [r["scroll_ticks"] for r in rows][::-1]
            fig  = go.Figure(go.Bar(x=vals, y=apps, orientation="h",
                marker=dict(color=vals, colorscale=[[0,"#1a0830"],[0.45,"#6a2fbf"],[1,"#c084fc"]], line=dict(width=0)),
                text=[f"  {v:,}" for v in vals], textposition="outside",
                textfont=dict(size=13, color="#c084fc", family="Sora,sans-serif"),
                hovertemplate="<b>%{y}</b><br>%{x:,} ticks<extra></extra>"))
            pt(fig, h=max(380, len(apps)*60), xaxis_title="Scroll Ticks",
               margin=dict(l=_lm(apps), r=120, t=30, b=50), showlegend=False)
            st.plotly_chart(fig, width="stretch")

        sec("Keystrokes by App")
        rows = sorted(data["app_summary"], key=lambda x: x["keystrokes"], reverse=True)[:12]
        rows = [r for r in rows if r["keystrokes"] > 0]
        if rows:
            apps = [r["application"] for r in rows]; vals = [r["keystrokes"] for r in rows]
            fig  = go.Figure(go.Bar(x=apps, y=vals, orientation="v",
                marker=dict(color=vals, colorscale=[[0,"#2a0e00"],[0.35,"#e8650a"],[1,"#f5a623"]], line=dict(width=0)),
                text=[f"{v:,}" for v in vals], textposition="outside",
                textfont=dict(size=11, color="#f5a623", family="Sora,sans-serif"),
                hovertemplate="<b>%{x}</b><br>%{y:,} keystrokes<extra></extra>"))
            pt(fig, h=380, xaxis_title="Application", yaxis_title="Keystrokes",
               xaxis={**_AX,"tickangle":-35,"tickfont":dict(size=11,color="#a89880",family="Sora,sans-serif")},
               margin=dict(l=60, r=30, t=40, b=120), showlegend=False)
            st.plotly_chart(fig, width="stretch")

        sec("Mouse Clicks by App")
        rows = sorted(data["app_summary"], key=lambda x: x["clicks"], reverse=True)[:12]
        rows = [r for r in rows if r["clicks"] > 0]
        if rows:
            apps = [r["application"] for r in rows][::-1]; vals = [r["clicks"] for r in rows][::-1]
            fig  = go.Figure(go.Bar(x=vals, y=apps, orientation="h",
                marker=dict(color=vals, colorscale=[[0,"#052a1a"],[0.35,"#1e8a50"],[1,"#4caf50"]], line=dict(width=0)),
                text=[f"  {v:,}" for v in vals], textposition="outside",
                textfont=dict(size=13, color="#4caf50", family="Sora,sans-serif"),
                hovertemplate="<b>%{y}</b><br>%{x:,} clicks<extra></extra>"))
            pt(fig, h=max(380, len(apps)*60), xaxis_title="Clicks",
               margin=dict(l=_lm(apps), r=120, t=30, b=50), showlegend=False)
            st.plotly_chart(fig, width="stretch")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE 4 — CONTEXT SWITCHING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🔀  Context Switching":
    st.markdown("""<div class="pg-hdr"><div>
      <div class="pg-eye"></div><div class="pg-title">Context Switching</div>
    </div></div>""", unsafe_allow_html=True)

    if not he:
        st.markdown('<div class="nodata"><div class="nodata-ico">🔀</div><h3>No event data</h3>'
                    '<p>Run <code>python monitor.py</code> first.</p></div>', unsafe_allow_html=True)
        st.stop()

    ev = data["events"]; r = data["report"]
    sw = ev[ev["event_type"] == "window_switch"].copy()
    if sw.empty:
        st.info("No window switch events found in this session."); st.stop()

    sw_hr = r["switches_per_hour"]; sess = max(r["session_minutes"], 1)
    st.markdown(f"""<div class="kg3" style="max-width:640px">
      {kpi("🔀","Total Switches", str(len(sw)),          "","Window changes recorded","kp")}
      {kpi("⚡","Rate",           f"{sw_hr:.1f}",        "/hr","Context switches per hour","ka")}
      {kpi("⏱","Avg Focus Gap",  f"{sess/max(len(sw),1):.1f}","min","Minutes between switches","kb")}
    </div>""", unsafe_allow_html=True)

    sec("Switch Frequency Over Time")
    sw["bucket"] = sw["timestamp"].dt.floor("5min")
    sw_b = sw.groupby("bucket").size().reset_index(name="switches")
    fig = go.Figure(go.Bar(x=sw_b["bucket"], y=sw_b["switches"],
        marker=dict(color=sw_b["switches"],
            colorscale=[[0,"#1a0a00"],[0.5,"#e8650a"],[1,"#f5a623"]], line=dict(width=0)),
        hovertemplate="<b>%{x|%H:%M}</b><br>%{y} switches<extra></extra>"))
    pt(fig, h=240, xaxis_title="Time (5-min bins)", yaxis_title="Switches")
    st.plotly_chart(fig, width="stretch")

    sec("Most Frequently Switched To")
    sw["from_a"] = sw["application"].apply(clean_app)
    sw["to_a"]   = sw["switch_dest"].apply(clean_app)
    pairs = (sw.groupby(["from_a","to_a"]).size()
               .reset_index(name="Switch Count")
               .sort_values("Switch Count", ascending=False)
               .head(30))
    pairs = pairs[(pairs["from_a"] != pairs["to_a"]) & (pairs["to_a"] != "")]
    pairs.columns = ["From Application","To Application","Switch Count"]
    if not pairs.empty:
        st.dataframe(pairs, width="stretch", hide_index=True)
    else:
        st.info("Not enough switch data to build transition table.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE 5 — RAW DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🖥  Raw Data":
    st.markdown("""<div class="pg-hdr"><div>
      <div class="pg-eye"></div><div class="pg-title">Raw Data</div>
    </div></div>""", unsafe_allow_html=True)

    if hr:
        r = data["report"]
        sec("Session Metadata")
        c1, c2, c3 = st.columns(3)
        def mc(k, v):
            return (f'<div style="background:linear-gradient(145deg,var(--bg3),var(--bg2));border:1px solid rgba(245,166,35,.12);'
                    f'border-radius:var(--rl);padding:.9rem 1.1rem;margin-bottom:.6rem">'
                    f'<div style="font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.14em;color:var(--txt3);margin-bottom:.35rem">{k}</div>'
                    f'<div style="font-size:15px;color:var(--txt);font-weight:600">{v}</div></div>')
        with c1:
            st.markdown(mc("Session Start", str(r.get("session_start","—"))[:19]), unsafe_allow_html=True)
            st.markdown(mc("Session End",   str(r.get("session_end",  "—"))[:19]), unsafe_allow_html=True)
        with c2:
            st.markdown(mc("Active Time", f"{r['session_minutes']:.1f} min"),    unsafe_allow_html=True)
            st.markdown(mc("Wall-clock",  f"{r['wall_clock_minutes']:.1f} min"), unsafe_allow_html=True)
        with c3:
            st.markdown(mc("Total Events", f"{r['total_events']:,}"),              unsafe_allow_html=True)
            st.markdown(mc("Focus Score",  f"{r['overall_focus_score']:.1f}/100"), unsafe_allow_html=True)

  if he:
        sec("Event Log — last 500 events")
        ev = data["events"].copy()
        df_r = ev[["timestamp","event_type","application"]].tail(500).iloc[::-1].copy()
        df_r["timestamp"] = df_r["timestamp"].dt.strftime("%H:%M:%S")
        df_r.columns = ["Time","Type","Application"]
        st.dataframe(df_r, width="stretch", hide_index=True)
