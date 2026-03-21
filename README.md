# jibu

**AI civic assistant for Kenya.**

[![Status](https://img.shields.io/badge/status-early%20development-orange)](#roadmap)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-red)](LICENSE)
[![Live Data](https://img.shields.io/badge/Live%20Data-LSK%20%C2%B7%20FIDA%20%C2%B7%20Judiciary%20%C2%B7%20open.er-api.com-00b4d8)](#jibu)
[![Live App](https://img.shields.io/badge/Live%20App-jibuyangu.streamlit.app-brightgreen)](https://jibuyangu.streamlit.app)

> **jibu** /jíbu/ — *Kiswahili*: answer, response.

The information gap between what Kenyan citizens are entitled to and what they know they're entitled to is vast. Labor rights, land rights, housing rights, what happens when police arrest you, how to register a business, how to apply for a government tender, what NHIF covers — this information exists, but it's buried in legalese, outdated government portals, and legal clinics that serve a fraction of who needs them.

Jibu is an AI assistant that gives Kenyans plain-language answers about their rights and government services, in Kiswahili and English.

---


**Live app:** https://jibuyangu.streamlit.app

## The problem

Kenya has good laws. The Constitution (2010) is widely praised. Labor law has protections. Consumer protection exists. But:

- Legal information is hard to access without a lawyer
- Government portals are outdated, hard to navigate, and English-only
- Legal aid organisations are underfunded and urban-concentrated
- Informal workers (the majority) often don't know their rights exist

The result: people don't claim rights they have, and don't access services they qualify for.

---

## What jibu does

Answers civic questions in plain language, bilingual, with source attribution.

**Domains in scope:**

| Domain | Examples |
|---|---|
| Labor rights | Minimum wage, termination, maternity leave, NSSF, NHIF |
| Land rights | Land tenure, eviction, caution notices, title deeds |
| Consumer rights | Defective goods, overcharging, mobile money disputes |
| Police and justice | Arrest rights, bail, legal representation, complaint filing |
| Business registration | Sole proprietor, limited company, partnership, cooperative |
| Government services | Huduma Centre services, passport, birth certificate, driving licence |
| Health rights | Public hospital rights, NHIF coverage, referral process |

**What jibu does not do:**
- Provide specific legal advice for individual cases (it provides legal information)
- Replace lawyers (it surfaces when a lawyer is needed)
- Cover outside Kenya

---

## Design principles

**Source-grounded answers only.**
Every answer cites its source: a specific constitutional article, a statute section, a government circular. Jibu never generates answers from general knowledge without a traceable source.

**Kiswahili is a first-class language.**
Not a translation of an English interface. Jibu is designed in Kiswahili first for Kiswahili speakers.

**Knows its limits.**
If a question requires specific legal advice, jibu says so clearly and points to legal aid organisations. It doesn't improvise legal strategy.

**Accessible on basic connections.**
Web-first but designed to function on slow connections. USSD interface planned for legal rights quick-reference without data.

---

## Architecture

```
jibu/
├── knowledge/
│   ├── sources.py        # Constitution, statutes, regulations as structured data
│   ├── indexer.py        # Chunk, embed, and index source documents
│   └── retriever.py      # RAG: retrieve relevant passages for a question
├── llm/
│   ├── client.py         # Gemini + Google Search grounding
│   ├── prompt.py         # System prompt: domain scope, citation rules, limits
│   └── guardrails.py     # Detect and handle out-of-scope questions
├── languages/
│   ├── detector.py       # Detect question language (sw/en)
│   └── strings.py        # UI strings in Kiswahili and English
├── api/
│   └── v1/               # REST API for web and future mobile client
└── web/
    └── app.py            # Streamlit public interface
```

**Knowledge base (planned):**
- Kenya Constitution 2010
- Employment Act (Cap 226)
- Consumer Protection Act 2012
- Land Act 2012
- National Police Service Act
- NHIF Act
- Business Registration Service procedures

---

## Roadmap

### v0.1 — Labor rights pilot
- [ ] Employment Act knowledge base (chunked, embedded)
- [ ] Bilingual chat interface (Kiswahili / English)
- [ ] Source citation on every answer
- [ ] "Talk to a lawyer" escalation for complex cases

### v0.2 — Consumer and police rights
- [ ] Consumer Protection Act coverage
- [ ] Police rights quick reference
- [ ] Complaint filing guides with links to relevant bodies

### v0.3 — Full civic coverage + USSD
- [ ] All 7 domains covered
- [ ] USSD quick-reference for offline access
- [ ] Usage analytics (aggregate only, no PII)

### v1.0 — Public launch
- [ ] Production deployment
- [ ] Partnership with legal aid organisations for escalation
- [ ] Product Hunt launch

---

## Why not just use ChatGPT?

General-purpose LLMs hallucinate on jurisdiction-specific legal questions. They answer confidently with wrong statute numbers, outdated provisions, or procedures from other countries.

Jibu uses retrieval-augmented generation anchored to actual Kenyan legal text. Every answer must trace to a specific source document. If the source doesn't support the answer, jibu doesn't give the answer.

---

## Contributing

Not accepting pull requests yet. Open an issue to discuss.
Contact: contact@aikungfu.dev

---

## License

CC BY-NC-ND 4.0. Commercial licensing: contact@aikungfu.dev

---

*Part of the [gabrielmahia](https://github.com/gabrielmahia) portfolio — infrastructure where Africa's economic reality meets software engineering.*
