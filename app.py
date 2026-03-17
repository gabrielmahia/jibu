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
import streamlit as st

from jibu.llm.language import detect_or_default, Language
from jibu.llm.prompt import build_system_prompt

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
</style>
""", unsafe_allow_html=True)

# ── Config ─────────────────────────────────────────────────────────────────────
_BASE = "https://generativelanguage.googleapis.com"

def _get_key():
    try:
        k = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        if k: return k
    except Exception:
        pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

def _call_gemini(system: str, user: str, api_key: str) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}], "role": "user"}],
        "generationConfig": {"maxOutputTokens": 800, "temperature": 0.3},
    }
    url = f"{_BASE}/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        err = e.read()[:200].decode("utf-8", "ignore")
        if e.code == 429:
            return "_quota_"
        return f"_error_{err}"
    except Exception as e:
        return f"_error_{str(e)[:80]}"

# ── Static fallback answers ───────────────────────────────────────────────────
_FALLBACKS = {
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
    "eviction|kufukuzwa": (
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
    "arrest|rights when arrested|kukamatwa": (
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
                "The service is busy. Please try again shortly. "
                "For immediate help: Kituo cha Sheria +254 20 387 4785"
            )
        elif raw.startswith("_error_"):
            reply = _static_response(pending) or "Unable to connect — try again shortly."
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
                "The service is temporarily at capacity. "
                "For immediate help: Kituo cha Sheria +254 20 387 4785"
            )
        elif raw.startswith("_error_"):
            reply = _static_response(question) or "Unable to connect — try again shortly."
        else:
            reply = raw
    else:
        reply = _static_response(question) or (
            "**Jibu** can answer questions about Kenyan civic rights in English and Kiswahili. "
            "For immediate legal help, contact:\n\n"
            "- **Kituo cha Sheria**: +254 20 387 4785 (free legal aid)\n"
            "- **FIDA Kenya**: +254 20 271 0705 (women's legal rights)\n"
            "- **KNHCR**: 020 271 2020 (human rights)\n"
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

st.divider()
st.markdown("""
**Legal aid organisations:**
[Kituo cha Sheria](https://kituochasheria.or.ke) · 020 387 4785 &nbsp;|&nbsp;
[FIDA Kenya](https://fidakenya.org) · 020 271 0705 &nbsp;|&nbsp;
[Legal Resources Foundation](https://lrfkenya.org) · 020 241 1322

Jibu · CC BY-NC-ND 4.0 · contact@aikungfu.dev · Not a substitute for legal advice
""")
