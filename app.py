"""
Jibu — Know your rights in plain Kiswahili (and English).

A civic rights information assistant for Kenya, grounded in:
- Constitution of Kenya 2010
- Employment Act (Cap 226)
- Land Act 2012
- Consumer Protection Act 2012
- Criminal Procedure Code (Cap 75)

This is legal INFORMATION, not legal ADVICE. For your specific situation,
speak with a lawyer or contact Kituo cha Sheria (+254 20 387 4785).
"""
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re as _re
import streamlit as st

from jibu.llm.language import detect_or_default
from jibu.llm.prompt import build_system_prompt


@st.cache_data(ttl=7200)
def fetch_legal_updates():
    """Latest publications from LSK, FIDA Kenya, and Kenya Judiciary."""
    sources = {
        "LSK":        "https://www.lsk.or.ke/feed/",
        "FIDA Kenya": "https://fidakenya.org/feed/",
        "Judiciary":  "https://judiciary.go.ke/feed/",
    }
    all_items = []
    for source, url in sources.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "jibu-kenya/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                root = ET.fromstring(r.read())
            for item in root.findall(".//item")[:3]:
                title = item.findtext("title", "").strip()
                link  = item.findtext("link",  "").strip()
                date  = item.findtext("pubDate", "").strip()[:16]
                desc  = _re.sub(r"<[^>]+>", "", item.findtext("description", "")).strip()[:140]
                if title:
                    all_items.append({"source": source, "title": title,
                                       "link": link, "date": date, "summary": desc})
        except Exception:
            pass
    return sorted(all_items, key=lambda x: x["date"], reverse=True)[:8]


@st.cache_data(ttl=3600)
def fetch_kes_rate_jibu():
    """Live KES rate for diaspora users accessing Jibu from abroad."""
    try:
        with urllib.request.urlopen(
            "https://open.er-api.com/v6/latest/USD", timeout=5
        ) as r:
            d = json.loads(r.read())
        return {"kes": round(d["rates"]["KES"], 2),
                "updated": d.get("time_last_update_utc", "")[:16], "live": True}
    except Exception:
        return {"live": False}


st.set_page_config(
    page_title="Jibu — Know Your Rights Kenya",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}

.jibu-header{
  background:linear-gradient(135deg,#0d1b2a 0%,#1b2d3e 60%,#1a3a5c 100%);
  color:white;padding:2rem 2rem 1.5rem;border-radius:12px;margin-bottom:1.5rem;
}
.jibu-header h1{font-family:'IBM Plex Mono',monospace;font-size:1.8rem;
  margin:0 0 .25rem;letter-spacing:-1px;}
.jibu-header p{font-size:.9rem;opacity:.72;margin:0;}

.disclaimer-box{
  background:#fff8e1;border-left:4px solid #f59e0b;
  padding:.8rem 1rem;border-radius:4px;font-size:.82rem;margin-bottom:1rem;
}

.msg-user{
  background:#e8f4fd;border-radius:12px 12px 4px 12px;
  padding:.75rem 1rem;margin:.5rem 0;font-size:.93rem;
}
.msg-jibu{
  background:#f0f4f8;border-left:3px solid #1b2d3e;border-radius:0 12px 12px 0;
  padding:.75rem 1rem;margin:.5rem 0;font-size:.93rem;line-height:1.65;
}
.msg-jibu.sw{border-left-color:#2e7d32;}

.topic-chip{
  display:inline-block;background:#e3eaf5;color:#1b2d3e;
  padding:4px 12px;border-radius:20px;font-size:.78rem;
  margin:3px;cursor:pointer;border:none;font-family:'IBM Plex Mono',monospace;
}
.topic-chip:hover{background:#1b2d3e;color:white;}

.source-tag{
  font-family:'IBM Plex Mono',monospace;font-size:.7rem;
  background:#e8f5e9;color:#2e7d32;padding:2px 8px;
  border-radius:10px;margin-left:4px;
}

@media(max-width:768px){
  [data-testid="column"]{width:100%!important;flex:1 1 100%!important;min-width:100%!important;}
  .jibu-header h1{font-size:1.4rem!important;}
  .stButton>button{width:100%!important;min-height:48px!important;}
}
    @media (max-width: 480px) {
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.15rem !important; }
        [data-testid="stMetricValue"] { font-size: 1rem !important; }
        .stButton > button { min-height: 52px !important; font-size: 0.95rem !important; }
    }

    /* Metric text — explicit colours, light + dark (both OS pref and Streamlit toggle) */
    [data-testid="stMetricLabel"]  { color: #444444 !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"]  { color: #111111 !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"]  { color: #333333 !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
        [data-testid="stMetricValue"] { color: #f0f0f0 !important; }
        [data-testid="stMetricDelta"] { color: #cccccc !important; }
    }
    [data-theme="dark"] [data-testid="stMetricLabel"],
    .stApp[data-theme="dark"] [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    [data-theme="dark"] [data-testid="stMetricValue"],
    .stApp[data-theme="dark"] [data-testid="stMetricValue"] { color: #f0f0f0 !important; }
    [data-theme="dark"] [data-testid="stMetricDelta"],
    .stApp[data-theme="dark"] [data-testid="stMetricDelta"] { color: #cccccc !important; }

</style>
""", unsafe_allow_html=True)

# ── Config ─────────────────────────────────────────────────────────────────────
_BASE = "https://generativelanguage.googleapis.com"

def _get_key():
    try:
        k = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        if k: return k  # noqa: E701
    except Exception:
        pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

def _call_gemini(system: str, user: str, api_key: str) -> str:
    # Inline system prompt — same pattern as the working catholic assistant.
    # system_instruction block is rejected by some model versions.
    full_prompt = f"{system}\n\nUser question: {user}\n\nAnswer:"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"maxOutputTokens": 800, "temperature": 0.3},
    }
    # Try gemini-2.0-flash first, fall back to 1.5-flash
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
    last_err = ""
    for model in models:
        url = f"{_BASE}/v1beta/models/{model}:generateContent?key={api_key}"
        body = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=body,
                                      headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            err = e.read()[:300].decode("utf-8", "ignore")
            if e.code == 429:
                continue  # try next model
            if e.code == 404:
                continue  # model not available, try next
            return f"_error_{e.code}:{err}"
        except Exception as e:
            last_err = str(e)[:80]
            continue
    # All models tried
    if last_err:
        return f"_error_{last_err}"
    return "_quota_"

# ── Static fallback answers ───────────────────────────────────────────────────
_FALLBACKS = {
    # Identity / what is this
    "what are you|who are you|what is jibu|nini wewe|wewe ni nani": (
        "I am Jibu — a civic information assistant for Kenya. I can answer questions "
        "about your rights under Kenyan law: labour rights, land rights, arrest rights, "
        "consumer protection, business registration, and government services. "
        "I provide general legal information in English and Kiswahili. "
        "For advice on your specific situation, speak with a lawyer or contact "
        "Kituo cha Sheria: +254 20 387 4785 (free legal aid)."
    ),
    # Employment
    "fire|dismiss|terminate|redundan|unfair|nafukuzwa|without notice|bila notisi": (
        "Under Kenya's Employment Act (Cap 226), your employer must give written notice "
        "before terminating your contract. The minimum notice period depends on your pay cycle: "
        "1 month if paid monthly, 2 weeks if paid fortnightly, 1 week if paid weekly. "
        "Termination without notice is only lawful for gross misconduct — and even then "
        "the employer must follow a fair disciplinary process (Employment Act Section 41). "
        "If you are dismissed unfairly, you can file a complaint with the "
        "Employment and Labour Relations Court or the Ministry of Labour.\n\n"
        "_This is general legal information. For your specific case, contact "
        "Kituo cha Sheria: +254 20 387 4785._"
    ),
    # Business registration
    "register a business|biashara|usajili|sole proprietor|limited company|register my business": (
        "To register a business in Kenya:\n"
        "**Sole proprietorship or partnership:** Register at the Registrar of Companies "
        "(eCitizen portal — ecitizen.go.ke). Cost: KES 950. Takes 1–3 days.\n"
        "**Limited company:** Register via eCitizen. Cost: ~KES 10,650. Takes 3–5 days. "
        "Requires a Memorandum and Articles of Association.\n"
        "**Cooperative society:** Register with the Commissioner for Cooperatives, "
        "Ministry of Trade. Minimum 10 members required.\n\n"
        "All businesses need a Single Business Permit from your county government. "
        "(Source: Companies Act 2015, Business Registration Service Act 2015)\n\n"
        "_For specific advice on the right structure for your business, contact "
        "the Business Registration Service at businessregistration.go.ke._"
    ),
    # NHIF
    "nhif|health insurance|bima ya afya|sha |social health": (
        "NHIF (National Hospital Insurance Fund) — now being transitioned to SHA "
        "(Social Health Authority) — covers inpatient and outpatient treatment "
        "at accredited public and private hospitals. "
        "Contributions are mandatory for formal employees (deducted from salary) "
        "and voluntary for self-employed and informal workers. "
        "Your card covers you, your spouse, and all children under 18. "
        "(Source: NHIF Act Cap 255, Social Health Insurance Act 2023)\n\n"
        "_Check your cover and accredited facilities at nhif.or.ke or sha.go.ke._"
    ),
    # Swahili arrest
    "haki zangu|ninakamatwa|nikikamatwa|polisi wanin": (
        "Unakamatwa Kenya, una haki hizi (Katiba ya Kenya 2010, Ibara 49):\n"
        "• Kuambiwa sababu ya kukamatwa mara moja\n"
        "• Kukaa kimya (kile unachosema kinaweza kutumika dhidi yako)\n"
        "• Kuwasiliana na mwanasheria mara moja\n"
        "• Kupelekwa mahakamani ndani ya masaa 24\n"
        "• Kutoteswa wala kudhalilishwa (Ibara 25)\n\n"
        "Ukihitaji msaada wa kisheria bure, wasiliana na "
        "Kituo cha Sheria: +254 20 387 4785."
    ),
    "minimum wage": (
        "Under Kenya's Labour Laws (Regulation of Wages) Order, the national minimum wage "
        "varies by sector and region. General labourers in Nairobi (2024): ~KES 15,201/month. "
        "Agricultural/domestic workers have different rates. Your employer is legally required "
        "to pay at least the gazetted rate for your category. "
        "(Source: Regulation of Wages Order, revised annually by the Ministry of Labour)\n\n"
        "_This is general legal information, not advice for your specific situation. "
        "For your case, contact the Ministry of Labour nearest office or Kituo cha Sheria._"
    ),
    "mshahara wa chini": (
        "Mshahara wa chini nchini Kenya unabadilika kulingana na sekta na eneo. "
        "Kwa mfanyakazi wa kawaida Nairobi (2024): karibu KES 15,201 kwa mwezi. "
        "(Chanzo: Agizo la Udhibiti wa Mishahara, linapitiwa kila mwaka na Wizara ya Kazi)\n\n"
        "_Hii ni habari ya kisheria kwa ujumla, si ushauri maalum kwa hali yako. "
        "Wasiliana na ofisi ya Wizara ya Kazi au Kituo cha Sheria._"
    ),
    "evict|court order|landlord|tenant|kufukuzwa|amri ya mahakama": (
        "Under the Land Act 2012 and the Prevention, Protection and Assistance to "
        "Internally Displaced Persons Act (2012), you cannot be evicted without:\n"
        "1. Written notice (minimum 3 months for residential tenants under the Landlord "
        "and Tenant (Shops, Hotels and Catering Establishments) Act)\n"
        "2. A court order (for protected tenants)\n"
        "3. Reasonable alternative arrangements if it is a government eviction\n\n"
        "Informal settlement residents have additional protections under the "
        "Constitution Article 43(1)(b) (right to housing). "
        "Police-assisted evictions without a court order are illegal.\n\n"
        "_Speak with Kituo cha Sheria (020 387 4785) for specific advice._"
    ),
    "arrest|arrested|kukamatwa|rights when|police|bail|kukamatwa": (
        "When arrested in Kenya, you have the following rights "
        "(Constitution of Kenya 2010, Article 49):\n"
        "• Be informed promptly of the reason for arrest\n"
        "• Remain silent (anything you say can be used against you)\n"
        "• Contact a lawyer immediately\n"
        "• Be brought before a court within 24 hours\n"
        "• Not be subjected to torture, cruel or degrading treatment (Article 25)\n\n"
        "If you cannot afford a lawyer, you may request legal aid from "
        "the National Legal Aid Service (NLAS) or Kituo cha Sheria."
    ),
}

def _static_response(q: str) -> str | None:
    q_lower = q.lower()
    for keys, answer in _FALLBACKS.items():
        if any(k in q_lower for k in keys.split("|")):
            return answer
    return None

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="jibu-header">
  <h1>⚖️ Jibu</h1>
  <p>Know your rights in Kenya · Jua haki zako · English &amp; Kiswahili</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
⚖️ <strong>Legal information only — not legal advice.</strong>
Jibu provides general information grounded in Kenyan law. For your specific situation,
speak with a lawyer or contact <strong>Kituo cha Sheria: +254 20 387 4785</strong>
(free legal aid) or <strong>FIDA Kenya: +254 20 271 0705</strong>.
</div>
""", unsafe_allow_html=True)

# ── Quick topic buttons ─────────────────────────────────────────────────────────
st.markdown("**Ask about your rights:**")

TOPICS_EN = [
    "What are my rights if I am arrested?",
    "Can my employer fire me without notice?",
    "What is the minimum wage in Kenya?",
    "Can I be evicted without a court order?",
    "How do I register a business in Kenya?",
    "What does NHIF cover?",
]
TOPICS_SW = [
    "Haki zangu zikiwa ninakamatwa?",
    "Mwajiri wangu anaweza kunifukuza bila notisi?",
    "Mshahara wa chini nchini Kenya ni ngapi?",
    "Naweza kufukuzwa bila amri ya mahakama?",
    "Ninajisajilisha biashara vipi?",
]

col1, col2 = st.columns(2)
with col1:
    st.markdown("**English**")
    for topic in TOPICS_EN:
        if st.button(topic, key=f"t_{topic[:20]}", use_container_width=True):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({"role": "user", "content": topic})
            st.session_state.pending = topic
            st.rerun()

with col2:
    st.markdown("**Kiswahili**")
    for topic in TOPICS_SW:
        if st.button(topic, key=f"t_{topic[:20]}", use_container_width=True):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({"role": "user", "content": topic})
            st.session_state.pending = topic
            st.rerun()

st.divider()

# ── Chat ───────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">👤 {msg["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        lang_cls = "sw" if msg.get("lang") == "sw" else ""
        st.markdown(f'<div class="msg-jibu {lang_cls}">⚖️ {msg["content"]}</div>',
                    unsafe_allow_html=True)

# Process pending (from topic buttons)
pending = st.session_state.pop("pending", None)
if pending:
    api_key = _get_key()
    lang = detect_or_default(pending)
    reply = None

    if api_key:
        system = build_system_prompt(lang)
        with st.spinner("Jibu inafikiria… / Thinking…"):
            raw = _call_gemini(system, pending, api_key)
        if raw.startswith("_quota_"):
            reply = _static_response(pending) or (
                "Jibu is taking a short break. Please try again in a moment. "
                "For urgent help: Kituo cha Sheria +254 20 387 4785."
            )
        elif raw.startswith("_error_"):
            reply = _static_response(pending) or (
                "Jibu is having a moment — please try again shortly. "
                "For urgent help: Kituo cha Sheria +254 20 387 4785."
            )
        else:
            reply = raw
    else:
        reply = _static_response(pending) or (
            "Jibu needs an AI key to answer custom questions. "
            "Topic buttons use built-in answers. "
            "Contact Kituo cha Sheria (+254 20 387 4785) for immediate legal help."
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "lang": lang.value,
    })
    st.session_state.input_counter += 1
    st.rerun()

# Text input
st.markdown("")
col_in, col_btn = st.columns([5, 1])
with col_in:
    user_input = st.text_input(
        "Ask your question",
        placeholder="What are my rights if my employer doesn't pay me? / Haki zangu zikiwa sijalipiwa?",
        label_visibility="collapsed",
        key=f"input_{st.session_state.input_counter}",
    )
with col_btn:
    send = st.button("Send", type="primary", use_container_width=True)

if send and user_input.strip():
    question = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": question})

    api_key = _get_key()
    lang = detect_or_default(question)
    reply = None

    if api_key:
        system = build_system_prompt(lang)
        with st.spinner("Jibu inafikiria… / Thinking…"):
            raw = _call_gemini(system, question, api_key)
        if raw.startswith("_quota_"):
            reply = _static_response(question) or (
                "Jibu is taking a short break. For immediate help, contact "
                "Kituo cha Sheria: +254 20 387 4785 (free legal aid)."
            )
        elif raw.startswith("_error_"):
            reply = _static_response(question) or (
                "Jibu is having a moment — please try again shortly. "
                "For urgent help: Kituo cha Sheria +254 20 387 4785."
            )
        else:
            reply = raw
    else:
        reply = _static_response(question) or (
            "Jibu answers questions about Kenyan civic rights in English and Kiswahili. "
            "The AI assistant is being set up — for immediate legal help:\n\n"
            "- **Kituo cha Sheria**: +254 20 387 4785 (free legal aid)\n"
            "- **FIDA Kenya**: +254 20 271 0705 (women's legal rights)\n"
            "- **Kenya National Commission on Human Rights**: 020 271 2020\n"
            "- **Legal Resources Foundation**: 020 241 1322"
        )

    st.session_state.messages.append({
        "role": "assistant", "content": reply, "lang": lang.value
    })
    st.session_state.input_counter += 1
    st.rerun()

if st.session_state.messages:
    if st.button("Clear conversation", key="clear"):
        st.session_state.messages = []
        st.session_state.input_counter += 1
        st.rerun()

# ── Live legal signal ─────────────────────────────────────────────────────
_legal = fetch_legal_updates()
_kes_j = fetch_kes_rate_jibu()

if _kes_j.get("live"):
    st.caption(f"📡 Diaspora rate: 1 USD = {_kes_j['kes']} KES · open.er-api.com")

if _legal:
    with st.expander(f"📡 Latest: LSK · FIDA · Judiciary ({len(_legal)} recent)", expanded=False):
        for _li in _legal:
            _src_icon = {"LSK": "🔵", "FIDA Kenya": "🟣", "Judiciary": "⚫"}.get(_li["source"], "⚪")
            st.markdown(
                f"{_src_icon} **{_li['source']}** · *{_li['date']}*  \n"
                f"[{_li['title'][:80]}{'…' if len(_li['title'])>80 else ''}]({_li['link']})"
            )
            if _li["summary"]:
                st.caption(_li["summary"][:120] + "…")
            st.divider()

st.divider()
st.markdown("""
**Legal aid organisations:**
[Kituo cha Sheria](https://kituochasheria.or.ke) · 020 387 4785 &nbsp;|&nbsp;
[FIDA Kenya](https://fidakenya.org) · 020 271 0705 &nbsp;|&nbsp;
[Legal Resources Foundation](https://lrfkenya.org) · 020 241 1322

Jibu · CC BY-NC-ND 4.0 · contact@aikungfu.dev · Not a substitute for legal advice
""")

# -- Feedback sidebar ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "**Was this useful?**\n\n"
        f"[:pencil: Leave feedback](https://docs.google.com/forms/d/e/1FAIpQLSff_cjR102HNUeYU428ROv56TScLBzsQRc1JTwY4wGizvTQKw/viewform) (2 min)\n\n"
        "[:bug: Report a bug](https://github.com/gabrielmahia/jibu/issues/new)\n\n"
        "---\n"
        "*Built by [Gabriel Mahia](https://aikungfu.dev)*\n\n"
        "[Back to all tools](https://gabrielmahia.github.io)"
    )
