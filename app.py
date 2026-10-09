import html
import time
from datetime import datetime

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg: #08080d;
  --card: rgba(255,255,255,0.035);
  --line: rgba(255,255,255,0.08);
  --text: #ece7dd;
  --muted: #8d867c;
  --accent: #ff8c32;
  --accent2: #ff5a1a;
  --ok: #4fd18b;
  --err: #ff5d5d;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--text); }
.stApp {
  background: var(--bg);
  background-image:
    radial-gradient(ellipse 70% 45% at 15% -10%, rgba(255,140,50,.14), transparent 60%),
    radial-gradient(ellipse 55% 40% at 90% 110%, rgba(255,80,30,.09), transparent 55%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 3rem 4rem; max-width: 1180px; }

/* Hero */
.hero { text-align: center; padding: 2.4rem 0 1.6rem; }
.eyebrow {
  font-family: 'DM Mono', monospace; font-size: .7rem; letter-spacing: .28em;
  text-transform: uppercase; color: var(--accent); margin-bottom: .9rem;
}
.hero h1 {
  font-family: 'Syne', sans-serif; font-weight: 800; letter-spacing: -.03em;
  font-size: clamp(2.6rem, 6vw, 4.6rem); line-height: 1; margin: 0 0 .9rem; color: #f4efe4;
}
.hero h1 span {
  background: linear-gradient(120deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: var(--muted); max-width: 540px; margin: 0 auto; line-height: 1.65; font-weight: 300; }

/* Inputs */
.stTextInput > label {
  font-family: 'DM Mono', monospace !important; font-size: .7rem !important;
  letter-spacing: .16em !important; text-transform: uppercase !important; color: var(--accent) !important;
}
.stTextInput input {
  background: rgba(255,255,255,.05) !important; border: 1px solid rgba(255,140,50,.28) !important;
  border-radius: 12px !important; color: #f4efe4 !important; padding: .85rem 1rem !important; font-size: 1rem !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(255,140,50,.14) !important; }

.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: #0a0a0f !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
  border: none !important; border-radius: 12px !important; padding: .75rem 1.6rem !important;
  box-shadow: 0 6px 24px rgba(255,140,50,.28) !important; transition: transform .15s, box-shadow .15s !important;
}
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(255,140,50,.4) !important; }
.stButton > button:disabled { opacity: .5; }

/* Example chips (real buttons so they work) */
.chips-label { font-family: 'DM Mono', monospace; font-size: .66rem; letter-spacing: .15em; color: var(--muted); margin: .4rem 0 .3rem; }

/* Pipeline */
.pipe-wrap { background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 1.4rem 1.6rem 1.6rem; margin: 1.2rem 0; }
.pipe-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .9rem; }
.pipe-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.05rem; }
.pipe-meta { font-family: 'DM Mono', monospace; font-size: .72rem; color: var(--muted); letter-spacing: .08em; }
.bar { height: 6px; border-radius: 99px; background: rgba(255,255,255,.07); overflow: hidden; margin-bottom: 1.3rem; }
.bar > div {
  height: 100%; border-radius: 99px; transition: width .5s ease;
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent));
  background-size: 200% 100%; animation: slide 2s linear infinite;
}
.bar.complete > div { background: var(--ok); animation: none; }
.bar.failed > div { background: var(--err); animation: none; }
@keyframes slide { to { background-position: -200% 0; } }

.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; }
@media (max-width: 800px) { .steps { grid-template-columns: 1fr 1fr; } }
.step {
  position: relative; border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1rem .9rem;
  background: rgba(255,255,255,.02); transition: all .3s;
}
.step.running { border-color: rgba(255,140,50,.55); background: rgba(255,140,50,.06); box-shadow: 0 0 0 1px rgba(255,140,50,.15), 0 8px 30px rgba(255,140,50,.12); }
.step.done { border-color: rgba(79,209,139,.35); background: rgba(79,209,139,.04); }
.step.error { border-color: rgba(255,93,93,.5); background: rgba(255,93,93,.05); }
.step-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: .6rem; }
.step-icon { font-size: 1.35rem; }
.badge { font-family: 'DM Mono', monospace; font-size: .62rem; letter-spacing: .12em; padding: .18rem .5rem; border-radius: 99px; border: 1px solid var(--line); color: var(--muted); }
.step.running .badge { color: var(--accent); border-color: rgba(255,140,50,.5); }
.step.done .badge { color: var(--ok); border-color: rgba(79,209,139,.4); }
.step.error .badge { color: var(--err); border-color: rgba(255,93,93,.5); }
.dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); margin-right: .35rem; animation: pulse 1s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: .3; transform: scale(.8);} 50% { opacity: 1; transform: scale(1.3);} }
.step-name { font-family: 'Syne', sans-serif; font-weight: 700; font-size: .95rem; }
.step-desc { font-size: .78rem; color: var(--muted); margin: .2rem 0 .7rem; line-height: 1.4; min-height: 2.2em; }
.step-foot { font-family: 'DM Mono', monospace; font-size: .68rem; color: var(--muted); display: flex; justify-content: space-between; }
.step.running .step-foot { color: var(--accent); }
.step.done .step-foot { color: var(--ok); }

/* Live log */
.term { background: #050508; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; margin-top: .4rem; }
.term-bar { display: flex; align-items: center; gap: .4rem; padding: .55rem .9rem; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.03); }
.term-bar i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.term-bar span { margin-left: .6rem; font-family: 'DM Mono', monospace; font-size: .68rem; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; }
.term-body {
  padding: .8rem 1rem; font-family: 'DM Mono', monospace; font-size: .75rem; line-height: 1.75;
  max-height: 260px; overflow-y: auto; overflow-x: hidden;
  display: flex; flex-direction: column-reverse; /* keeps view pinned to newest line */
  scrollbar-width: thin; scrollbar-color: rgba(255,140,50,.4) transparent;
}
.term-body::-webkit-scrollbar { width: 6px; }
.term-body::-webkit-scrollbar-thumb { background: rgba(255,140,50,.4); border-radius: 99px; }
.ln { white-space: pre-wrap; word-break: break-word; color: #b9b2a6; }
.ln .t { color: #5d574f; margin-right: .6rem; }
.ln .a { color: var(--accent); margin-right: .5rem; }
.ln.ok { color: var(--ok); } .ln.err { color: var(--err); }
.cursor { display: inline-block; width: 7px; height: 13px; background: var(--accent); vertical-align: middle; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* Live draft preview */
.draft { background: var(--card); border: 1px dashed rgba(255,140,50,.35); border-radius: 14px; padding: 1.1rem 1.4rem; margin-top: 1rem; max-height: 320px; overflow: hidden; position: relative; }
.draft-label { font-family: 'DM Mono', monospace; font-size: .66rem; letter-spacing: .16em; color: var(--accent); margin-bottom: .6rem; text-transform: uppercase; }
.draft-text { font-size: .85rem; line-height: 1.7; color: #bdb6aa; white-space: pre-wrap; }

/* Results */
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-family: 'DM Mono', monospace; font-size: .75rem; letter-spacing: .08em; color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--accent) !important; }
.section { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.35rem; margin: 2rem 0 .6rem; }
.stat-row { display: flex; gap: .8rem; flex-wrap: wrap; margin: .6rem 0 1rem; }
.stat { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: .6rem 1rem; }
.stat b { display: block; font-family: 'Syne', sans-serif; font-size: 1.15rem; color: var(--accent); }
.stat span { font-family: 'DM Mono', monospace; font-size: .64rem; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; }
.notice { font-family: 'DM Mono', monospace; font-size: .7rem; color: #5d574f; text-align: center; margin-top: 3rem; letter-spacing: .08em; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Pipeline definition ───────────────────────────────────────────────────────
STEPS = [
    ("search", "🔍", "Search Agent", "Gathers recent information from the web"),
    ("reader", "📄", "Reader Agent", "Scrapes the best source for deep content"),
    ("writer", "✍️", "Writer Chain", "Drafts the full research report"),
    ("critic", "🧐", "Critic Chain", "Reviews and scores the report"),
]


def fmt_secs(s: float) -> str:
    return f"{s:0.1f}s" if s < 60 else f"{int(s // 60)}m {int(s % 60):02d}s"


def to_text(content) -> str:
    """Normalise LangChain message content (str or list of blocks) to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, str):
                parts.append(b)
            elif isinstance(b, dict) and b.get("type") == "text":
                parts.append(b.get("text", ""))
        return "".join(parts)
    return str(content)


# ── Renderers ─────────────────────────────────────────────────────────────────
def pipeline_html(states, durations, started_at, status_text, mode="running"):
    done_n = sum(1 for k, *_ in STEPS if states.get(k) == "done")
    running = any(v == "running" for v in states.values())
    pct = (done_n + (0.5 if running else 0)) / len(STEPS) * 100
    if mode == "complete":
        pct = 100
    elapsed = fmt_secs(time.time() - started_at) if started_at else "—"
    bar_cls = {"complete": "complete", "failed": "failed"}.get(mode, "")

    cards = []
    for key, icon, name, desc in STEPS:
        s = states.get(key, "waiting")
        badge = {
            "waiting": "WAITING",
            "running": '<span class="dot"></span>RUNNING',
            "done": "✓ DONE",
            "error": "✕ FAILED",
        }[s]
        dur = durations.get(key)
        if s == "done" and dur is not None:
            foot = f"<span>completed</span><span>{fmt_secs(dur)}</span>"
        elif s == "running":
            foot = "<span>in progress…</span><span></span>"
        elif s == "error":
            foot = "<span>stopped</span><span></span>"
        else:
            foot = "<span>queued</span><span></span>"
        cards.append(
            f'<div class="step {s}"><div class="step-top"><span class="step-icon">{icon}</span>'
            f'<span class="badge">{badge}</span></div><div class="step-name">{name}</div>'
            f'<div class="step-desc">{desc}</div><div class="step-foot">{foot}</div></div>'
        )

    return (
        '<div class="pipe-wrap"><div class="pipe-head">'
        f'<div class="pipe-title">{html.escape(status_text)}</div>'
        f'<div class="pipe-meta">STEP {min(done_n + (1 if running else 0), 4)}/4 · {elapsed} elapsed</div></div>'
        f'<div class="bar {bar_cls}"><div style="width:{pct:.0f}%"></div></div>'
        f'<div class="steps">{"".join(cards)}</div></div>'
    )


def log_html(lines, live=True):
    body = []
    for ts, agent, msg, kind in lines[-300:]:
        body.append(
            f'<div class="ln {kind}"><span class="t">{ts}</span>'
            f'<span class="a">[{html.escape(agent)}]</span>{html.escape(msg)}</div>'
        )
    if live:
        body.append('<div class="ln"><span class="cursor"></span></div>')
    return (
        '<div class="term"><div class="term-bar">'
        '<i style="background:#ff5f56"></i><i style="background:#ffbd2e"></i><i style="background:#27c93f"></i>'
        '<span>Live activity</span></div>'
        f'<div class="term-body"><div>{"".join(body)}</div></div></div>'
    )


def draft_html(text):
    tail = text[-900:]
    words = len(text.split())
    return (
        f'<div class="draft"><div class="draft-label">✍️ Live draft · {words} words</div>'
        f'<div class="draft-text">{html.escape(tail)}<span class="cursor"></span></div></div>'
    )


# ── Pipeline runner (real-time) ───────────────────────────────────────────────
class Runner:
    def __init__(self, topic, pipe_ph, log_ph, draft_ph):
        self.topic = topic
        self.pipe_ph, self.log_ph, self.draft_ph = pipe_ph, log_ph, draft_ph
        self.states = {k: "waiting" for k, *_ in STEPS}
        self.durations = {}
        self.logs = []
        self.t0 = time.time()
        self.status = "Starting pipeline…"
        self._step_t: float = 0.0

    # UI helpers
    def refresh(self, mode="running", live=True):
        self.pipe_ph.markdown(
            pipeline_html(self.states, self.durations, self.t0, self.status, mode),
            unsafe_allow_html=True,
        )
        self.log_ph.markdown(log_html(self.logs, live), unsafe_allow_html=True)

    def log(self, agent, msg, kind=""):
        self.logs.append((datetime.now().strftime("%H:%M:%S"), agent, msg, kind))
        self.refresh()

    def begin(self, key, status):
        self.states[key] = "running"
        self.status = status
        self._step_t = time.time()
        self.log(key, "started")

    def finish(self, key, chars):
        self.states[key] = "done"
        self.durations[key] = time.time() - self._step_t
        self.log(key, f"finished · {chars:,} chars · {fmt_secs(self.durations[key])}", "ok")

    # Agent with live tool-call streaming
    def run_agent(self, key, agent, prompt):
        payload = {"messages": [{"role": "user", "content": prompt}]}
        final, seen = "", 0
        try:
            for chunk in agent.stream(payload, stream_mode="values"):
                msgs = chunk.get("messages", [])
                for m in msgs[seen:]:
                    kind = getattr(m, "type", "")
                    for tc in getattr(m, "tool_calls", None) or []:
                        args = str(tc.get("args", ""))[:90]
                        self.log(key, f"🔧 calling {tc.get('name')}({args})")
                    if kind == "tool":
                        self.log(key, f"↩ tool returned {len(to_text(m.content)):,} chars")
                    elif kind == "ai" and not getattr(m, "tool_calls", None):
                        self.log(key, "💭 composing answer…")
                seen = len(msgs)
                if msgs:
                    final = to_text(msgs[-1].content)
        except (AttributeError, NotImplementedError):
            self.log(key, "streaming unavailable, waiting for result…")
            resp = agent.invoke(payload)
            final = to_text(resp["messages"][-1].content)
        return final

    # Chain with live token streaming
    def run_chain(self, key, chain, inputs, show_draft=False):
        text = ""
        last_paint = 0.0
        try:
            for piece in chain.stream(inputs):
                text += piece if isinstance(piece, str) else to_text(getattr(piece, "content", piece))
                now = time.time()
                if show_draft and now - last_paint > 0.15:
                    self.draft_ph.markdown(draft_html(text), unsafe_allow_html=True)
                    last_paint = now
                if now - last_paint > 1.0:
                    self.refresh()
                    last_paint = now
        except (AttributeError, NotImplementedError, TypeError):
            out = chain.invoke(inputs)
            text = out if isinstance(out, str) else to_text(getattr(out, "content", out))
        self.draft_ph.empty()
        return text


# ── Session state ─────────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("meta", {})
st.session_state.setdefault("topic_input", "")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero"><div class="eyebrow">Multi-Agent AI System</div>'
    "<h1>Research<span>Mind</span></h1>"
    "<p>Four specialised agents search, read, write and critique — "
    "and you watch every step happen live.</p></div>",
    unsafe_allow_html=True,
)

# ── Input ─────────────────────────────────────────────────────────────────────
def set_topic(value):
    st.session_state.topic_input = value


c1, c2 = st.columns([5, 2], vertical_alignment="bottom")
with c1:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2026",
        key="topic_input",
    )
with c2:
    run_btn = st.button("⚡ Run Research", use_container_width=True)

st.markdown('<div class="chips-label">TRY →</div>', unsafe_allow_html=True)
chip_cols = st.columns([1, 1, 1, 3])
for col, ex in zip(chip_cols, ["LLM agents 2026", "CRISPR gene editing", "Fusion energy progress"]):
    col.button(ex, key=f"chip_{ex}", on_click=set_topic, args=(ex,), use_container_width=True)

# ── Live pipeline area ────────────────────────────────────────────────────────
pipe_ph = st.empty()
log_ph = st.empty()
draft_ph = st.empty()

if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        topic_val = topic.strip()
        st.session_state.results = {}
        results = {}
        run = Runner(topic_val, pipe_ph, log_ph, draft_ph)
        run.refresh()
        current = None
        try:
            # 1 · Search
            current = "search"
            run.begin("search", "Search Agent is browsing the web…")
            results["search"] = run.run_agent("search", build_search_agent(), f"Find information about: {topic_val}")
            run.finish("search", len(results["search"]))

            # 2 · Reader
            current = "reader"
            run.begin("reader", "Reader Agent is scraping the top source…")
            reader_prompt = (
                f"Based on the following search results about '{topic_val}', "
                f"extract and scrape the most relevant URL for deep content.\n\n"
                f"Search Results:\n{results['search']}"
            )
            results["reader"] = run.run_agent("reader", build_reader_agent(), reader_prompt)
            run.finish("reader", len(results["reader"]))

            # 3 · Writer
            current = "writer"
            run.begin("writer", "Writer is drafting your report…")
            research = f"SEARCH RESULTS:\n{results['search']}\n\nDETAILED SCRAPED CONTENT:\n{results['reader']}"
            results["writer"] = run.run_chain(
                "writer", writer_chain, {"topic": topic_val, "research": research}, show_draft=True
            )
            run.finish("writer", len(results["writer"]))

            # 4 · Critic
            current = "critic"
            run.begin("critic", "Critic is reviewing the report…")
            results["critic"] = run.run_chain("critic", critic_chain, {"report": results["writer"]})
            run.finish("critic", len(results["critic"]))

            run.status = "Pipeline complete ✓"
            run.refresh(mode="complete", live=False)
            st.session_state.meta = {
                "topic": topic_val,
                "total": time.time() - run.t0,
                "durations": dict(run.durations),
                "words": len(results["writer"].split()),
                "pipe_html": pipeline_html(run.states, run.durations, run.t0, run.status, "complete"),
                "log": list(run.logs),
            }
        except Exception as e:  # noqa: BLE001
            if current:
                run.states[current] = "error"
            run.status = f"Failed at {current or 'start'}"
            run.logs.append((datetime.now().strftime("%H:%M:%S"), current or "pipeline", f"{type(e).__name__}: {e}", "err"))
            run.refresh(mode="failed", live=False)
            st.error(f"Pipeline stopped at **{current}**: {e}")
        finally:
            st.session_state.results = dict(results)

elif st.session_state.results and st.session_state.meta:
    # Restore the finished pipeline view after any rerun (e.g. clicking Download)
    m = st.session_state.meta
    pipe_ph.markdown(m["pipe_html"], unsafe_allow_html=True)
    with log_ph.container():
        with st.expander("📟 Activity log", expanded=False):
            st.markdown(log_html(m["log"], live=False), unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results
if r.get("writer"):
    m = st.session_state.meta
    st.markdown('<div class="section">Results</div>', unsafe_allow_html=True)
    if m:
        st.markdown(
            '<div class="stat-row">'
            f'<div class="stat"><b>{fmt_secs(m["total"])}</b><span>Total time</span></div>'
            f'<div class="stat"><b>{m["words"]:,}</b><span>Report words</span></div>'
            f'<div class="stat"><b>4/4</b><span>Steps complete</span></div></div>',
            unsafe_allow_html=True,
        )

    tab_report, tab_critic, tab_search, tab_reader = st.tabs(
        ["📝 Report", "🧐 Critic feedback", "🔍 Search results", "📄 Scraped content"]
    )
    with tab_report:
        st.markdown(r["writer"])
        st.download_button(
            "⬇ Download report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )
    with tab_critic:
        st.markdown(r.get("critic", "_No feedback produced._"))
    with tab_search:
        st.markdown(r.get("search", ""))
    with tab_reader:
        st.markdown(r.get("reader", ""))

st.markdown(
    '<div class="notice">ResearchMind · LangChain multi-agent pipeline · Streamlit</div>',
    unsafe_allow_html=True,
)