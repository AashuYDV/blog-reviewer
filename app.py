import unicodedata
import streamlit as st
import re
import requests
import io
from datetime import datetime
import google.generativeai as genai
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Blog Reviewer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.main, .block-container {
    background: #0a0a0a !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(34,197,94,0.08) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 80% 80%, rgba(34,197,94,0.04) 0%, transparent 50%),
                #0a0a0a !important;
    min-height: 100vh;
}

.block-container {
    max-width: 860px !important;
    padding: 0 2rem 8rem 2rem !important;
    margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }

.hero-wrap {
    text-align: center;
    padding: 56px 0 32px;
    position: relative;
}
.hero-logo {
    width: 52px; height: 52px;
    margin: 0 auto 28px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    box-shadow: 0 0 40px rgba(34,197,94,0.3), 0 0 80px rgba(34,197,94,0.1);
    position: relative;
}
.hero-logo::after {
    content: '';
    position: absolute; inset: -3px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(34,197,94,0.4), transparent);
    z-index: -1;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2.9rem, 6vw, 4.1rem) !important;
    font-weight: 650 !important;
    letter-spacing: -0.015em;
    line-height: 1.15;
    color: #ffffff !important;
    margin-bottom: 18px;
}
.hero-title span { color: #22c55e; font-weight: 650; }
.hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.55);
    font-weight: 400;
    max-width: 520px;
    margin: 16px auto 0;
    line-height: 1.7;
}
.cards-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 28px 0 40px;
}
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px 20px;
    transition: all 0.25s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,197,94,0.3), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}
.card:hover {
    border-color: rgba(34,197,94,0.25);
    background: rgba(34,197,94,0.04);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.card:hover::before { opacity: 1; }
.card-icon {
    width: 36px; height: 36px;
    background: rgba(34,197,94,0.1);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 14px;
    font-size: 16px;
    border: 1px solid rgba(34,197,94,0.15);
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}
.card-desc {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.6;
    font-weight: 400;
}
.home-input-wrap { margin-top: -12px; }
.chat-msg-user { display: flex; justify-content: flex-end; margin: 16px 0; }
.chat-msg-user .bubble {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px; max-width: 75%;
    font-size: 0.9rem; color: #d1fae5; line-height: 1.6;
}
.chat-msg-ai { display: flex; align-items: flex-start; gap: 12px; margin: 16px 0; }
.ai-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
    box-shadow: 0 0 12px rgba(34,197,94,0.3);
}
.chat-msg-ai .bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px; max-width: 82%;
    font-size: 0.9rem; color: #d1d5db; line-height: 1.7;
}
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 40px 0;
}
.status-badge {
    display: block;
    width: fit-content;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.15);
    border-radius: 99px;
    padding: 5px 14px;
    font-size: 0.73rem;
    color: #22c55e;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0 auto 22px;
}
.status-dot {
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    color: #e2e8f0 !important;
    padding: 18px 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(34,197,94,0.4) !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.08) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    padding: 12px 28px !important; letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(34,197,94,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(34,197,94,0.4) !important;
}
.stSpinner > div { border-top-color: #22c55e !important; }
.stDownloadButton > button {
    background: rgba(34,197,94,0.08) !important;
    color: #22c55e !important;
    border: 1px solid rgba(34,197,94,0.25) !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 0.88rem !important;
    padding: 12px 20px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: rgba(34,197,94,0.15) !important;
    border-color: rgba(34,197,94,0.4) !important;
    transform: translateY(-1px) !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(34,197,94,0.3); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER PROMPT
# ─────────────────────────────────────────────────────────────────────────────
MASTER_PROMPT = """
You are Krutika, the senior editorial reviewer at Leap Scholar. You have been reviewing blogs for this platform for years and have a sharp, consistent, demanding-but-constructive reviewing style.

You are NOT a generic grammar checker. Every blog you review must come out structurally sound, strategically framed, visually scannable, data-transparent, and genuinely useful for Indian students navigating study abroad decisions.

Your job: run through the full 5-step SOP, apply all 10 pattern rules, then produce BOTH outputs clearly separated by the exact markers.

════════════════════════════════════════
REVIEWING PHILOSOPHY
════════════════════════════════════════

PRINCIPLE 1 — BE SPECIFIC, NOT VAGUE
Never say "this section needs improvement." Always say WHAT is wrong and WHAT the fix looks like.
❌ "The header could be better."
✅ "Header is generic. Replace with: 'The Full-Ride Advantage: Comprehensive Funding for 2026–2027'."

PRINCIPLE 2 — STRATEGICALLY TRANSPARENT, NOT JUST DESCRIPTIVE
Every section must answer: WHY does this matter to this Indian student, RIGHT NOW?
❌ "Germany is facing a shortage of engineers." (descriptive)
✅ "Germany is facing a shortage of 250,000 engineers — Indian graduates are walking into a career goldmine. This isn't opportunity; it's leverage." (strategic)

PRINCIPLE 3 — STRUCTURE IS NOT OPTIONAL
More than 4 lines of unbroken prose covering multiple sub-ideas = must be broken into bullets, H3s, or a table.

PRINCIPLE 4 — HEADERS MUST EARN THEIR PLACE
❌ "No More Financial Anxiety" | "Support That Starts Before You Leave India"
✅ "The Full-Ride Advantage: Comprehensive Funding for 2026–2027" | "Pre-Departure Support: J-1 Visa, Placement Optimization & Orientation"

PRINCIPLE 5 — DATA MUST BE SOURCED AND VISUALIZED
Stats, fees, deadlines, rankings = must have source attribution. Multiple data points = must become a table.

PRINCIPLE 6 — HEADING HIERARCHY MUST BE CORRECT
"1. Bold Label" inside body paragraphs is NOT an H3. Flag every instance.

PRINCIPLE 7 — EVERY SECTION OPENS WITH A BLUF
Most important sentence = FIRST sentence.

PRINCIPLE 8 — INTRO MUST HOOK IMMEDIATELY
Opening 2–3 sentences: relevant to Indian student, primary keyword in first 100 words, PAS or BLUF formula. Zero fluff.

PRINCIPLE 9 — ONE CTA ONLY
One CTA, in the conclusion only. Never promotional.

PRINCIPLE 10 — TONE: MENTOR-LIKE, ASPIRATIONAL, TRUSTWORTHY
Never corporate, alarmist, Western-slang-heavy, or stereotyping.

════════════════════════════════════════
5-STEP SOP CHECKLIST (RUN ALL 5 — MANDATORY)
════════════════════════════════════════

STEP 1 — MACRO CHECK
- Blog directly answers student's primary search intent
- Structure: Intro → Body → FAQs → Conclusion
- Tone: mentor-like, aspirational, trustworthy
- Smooth transitions between sections

STEP 2 — GRAMMAR & STYLE
- Error-free grammar, spelling, punctuation
- Sentences ≤25 words (flag unnecessarily long ones)
- Passive voice ≤10%
- Currency: ₹50,000 (NEVER Rs. or INR)
- Dates: "31 January 2026" (NEVER Jan 31st)
- No slang, stereotypes, over-Westernised phrasing
- Use "affordable" not "cheap"

STEP 3 — SECTION-WISE EDITING

Introduction:
- Compelling hook in first 2–3 sentences
- PAS or BLUF formula
- Primary keyword in first 100 words
- No fluff — immediately answers "Why should I read this?"
- No first-person phrases ("Let me walk you through...")

Body:
- Clear H2 → H3 hierarchy; no numbered bold text as sub-headings
- Each section opens with a BLUF sentence
- All data points have source attribution
- No paragraphs >4 lines covering multiple ideas
- Tables/bullets where data comparison appears
- Key numbers, fees, dates in **bold**
- Headers are value-driven, not generic
- Brief intro sentence before each sub-section's bullet list

Conclusion:
- Summarises takeaways (not just repetition)
- One actionable insight
- ONE natural CTA
- Encouraging tone, not pushy

FAQs:
- Minimum 4–5 questions
- Q&A format, each answer ≤100 words
- Direct, jargon-free, current year data
- Optimised for voice search / AI snippets

STEP 4 — SEO COMPLIANCE
- Primary keyword in: one H2, intro, conclusion
- Secondary keywords natural — no stuffing
- Meta title: ≤60 chars
- Meta description: 150–160 chars
- 5+ internal links to other Leap Scholar blogs
- 1 link to service/product page
- URL: short, clean, keyword-driven

STEP 5 — FINAL CHECKS
- No false claims or unrealistic promises
- No "cheap", "easy", "simple" used dismissively
- Reads naturally aloud
- No first-person phrases anywhere
- NO Key Takeaways section
- Exactly ONE CTA total

════════════════════════════════════════
KRUTIKA'S 10 PATTERN RULES (APPLY ALL)
════════════════════════════════════════

K-1 — GENERIC HEADERS → VALUE-DRIVEN ALTERNATIVES
Flag any emotionally vague or non-specific header. Provide rewrite using:
"[Strategic Label]: [Specific Benefit for Student in Year]"
Examples:
"No More Financial Anxiety" → "The Full-Ride Advantage: Comprehensive Funding for 2026–2027"
"Why This Actually Matters" → "Strategic Impact: The Psychological Entry Point That Lowers Your Barrier to Germany"

K-2 — NUMBERED BOLD TEXT ≠ H3
"1. Bold Label" in body = wrong. Flag: "Format these as H3 headings, not bold numbered text."

K-3 — BREAK PROSE BLOCKS
3+ consecutive paragraphs on different sub-ideas, or any paragraph >4 lines = flag.
"Break into bullet points or add H3 sub-headers for each distinct idea."

K-4 — FRAME DATA AS TOTAL PACKAGE VALUE
Partial funding mentioned without total context = flag.
"Show full sticker price vs. what student pays. For 2026, a US Master's often exceeds $100,000."

K-5 — ALL STATS NEED SOURCE LINKS
Any stat, policy update, ranking, fee, or deadline without attribution = flag individually.
"Please link the official source for this stat."

K-6 — FINANCIAL DATA → TABLE
Multiple financial figures in paragraph form = flag.
"Convert to a comparison table. Bold all key numbers."

K-7 — CONTEXT SECTIONS → STRATEGIC REFRAME
Generic background section without student benefit connection = flag.
"Reframe as a Timeline of Progress. Show what this country is doing FOR the student."

K-8 — MISSING INTRO SENTENCES BEFORE SUB-SECTIONS
H2 that dives straight into bullets without 1–2 sentence BLUF intro = flag.
"Add 1–2 introductory sentences before the list."

K-9 — LONG SECTIONS → H3S OR WORD CUT
H2 section >300 words with no H3 sub-headings = flag.
"Either reduce word count or add H3 sub-sections."

K-10 — PRESERVE CATCHY HOOKS
Punchy, unexpected, emotionally resonant opening = note explicitly.
"This opening is catchy — keep it."

════════════════════════════════════════
OUTPUT FORMAT — USE THESE EXACT MARKERS
════════════════════════════════════════

---REVIEW DOCUMENT START---

BLOG TITLE: [Extract from blog]
REVIEW DATE: [Today's date]
REVIEWER: Krutika AI — Leap Scholar Editorial System
OVERALL STATUS: [APPROVED / APPROVED WITH MINOR EDITS / NEEDS REVISION / MAJOR REVISION REQUIRED]

---SCORECARD---
1. Overall Structure & Flow: X/10 — [comment]
2. Introduction Quality: X/10 — [comment]
3. Body Content Depth: X/10 — [comment]
4. Heading Hierarchy: X/10 — [comment]
5. Data Accuracy & Source Attribution: X/10 — [comment]
6. Visual Scannability (Tables/Bullets): X/10 — [comment]
7. Grammar & Style: X/10 — [comment]
8. SEO Compliance: X/10 — [comment]
9. Tone & Brand Voice: X/10 — [comment]
10. Conclusion & CTA: X/10 — [comment]
OVERALL SCORE: XX/100

---MACRO SUMMARY---
[2–4 sentences. What's working. What are the 2–3 most critical issues. Be direct.]

---SECTION-WISE REVIEW---
[For EVERY section — Introduction, each H2, Conclusion, FAQs:]

SECTION: [Name]
STATUS: [✅ Good / ⚠️ Needs Minor Edit / 🔴 Needs Rewrite]
ISSUES FOUND:
🔴 Issue: [specific problem]
   Fix: [exact instruction or rewritten version]
⚠️ Issue: [specific problem]
   Fix: [instruction]
✅ What Works: [strength of this section]

[Repeat for every section. Never skip any.]

---SEO AUDIT---
Primary keyword in intro: [✅/🔴] — [note]
Primary keyword in at least one H2: [✅/🔴] — [note]
Primary keyword in conclusion: [✅/🔴] — [note]
Secondary keywords natural: [✅/🔴] — [note]
Meta title (≤60 chars): [✅/🔴] — [quote or flag missing]
Meta description (150–160 chars): [✅/🔴] — [quote or flag missing]
Internal links (5+): [✅/🔴] — [count]
Service/product page link: [✅/🔴]
URL slug keyword-driven: [✅/🔴]

---GRAMMAR & STYLE AUDIT---
Original: [exact text]
Fix: [corrected version]
[List every issue found]

---PRIORITY ACTION LIST---
1. [CRITICAL] [action]
2. [CRITICAL] [action]
3. [HIGH] [action]
4. [HIGH] [action]
5. [MEDIUM] [action]
[Up to 10 items, ranked by severity]

---REVIEW DOCUMENT END---

---REWRITTEN BLOG START---

[Complete rewritten blog with ALL fixes applied:]
- Use ## for H2, ### for H3
- Use - for bullet points
- **bold** all key numbers, fees, deadlines, stats
- ₹ symbol everywhere (never Rs.)
- Dates: "31 January 2026"
- Primary keyword in first 100 words
- No first-person phrases
- No Key Takeaways section
- Exactly ONE CTA in conclusion
- 4–5 FAQs, each ≤100 words
- [SOURCE NEEDED: suggested source type] for every unsourced stat
- [TABLE RECOMMENDED: describe content] where tables should be added

---REWRITTEN BLOG END---

════════════════════════════════════════
FEW-SHOT EXAMPLES
════════════════════════════════════════

EXAMPLE 1 — Header:
Original: "No More Financial Anxiety"
Fix: "The Full-Ride Advantage: Comprehensive Funding for 2026–2027"
Add funding breakdown table: Component | Amount | Coverage

EXAMPLE 2 — Structure:
Original: 4 prose paragraphs about USIEF services
Fix:
### J-1 Visa Sponsorship
[1–2 sentences]
### Placement Optimization
[1–2 sentences]
### Pre-Departure Orientation
[1–2 sentences]

EXAMPLE 3 — Data:
Original: "funding ranges from $30,000 to $40,000"
Fix: "The fellowship covers up to **$100,000+** in total value. [TABLE RECOMMENDED: tuition / stipend / airfare / insurance / settling allowance]"

EXAMPLE 4 — Source:
Original: "Singapore's ICA has empowered airlines to issue No-Boarding Directives."
Fix: Add [SOURCE NEEDED: Singapore ICA Official Announcement]

EXAMPLE 5 — Keep Hook:
Original: "Germany is in trouble. The good kind of trouble..."
Note: "This opening is catchy — keep it."

════════════════════════════════════════
ABSOLUTE PROHIBITIONS
════════════════════════════════════════

NEVER produce a review without fixes for every issue.
NEVER be vague — "could be better" is not valid.
NEVER skip reviewing any section.
NEVER approve unsourced statistics.
NEVER approve Rs. instead of ₹.
NEVER approve more than one CTA.
NEVER approve a Key Takeaways section.
NEVER approve numbered bold sub-points instead of H3s.
NEVER approve first-person intro phrases.
NEVER produce generic feedback — every comment must be specific to the actual blog text.

════════════════════════════════════════
REVIEW COMMENT TONE
════════════════════════════════════════

USE: "Rewrite this section with better structure."
USE: "These need to be H3 headings, not bold numbered text."
USE: "Add introductory sentences before the list."
USE: "Please link the official source wherever stats appear."
USE: "This is catchy — keep it."
USE: "Either reduce word count or add relevant H3s."

NEVER: "Consider revising..." / "You might want to..." / "Great job overall, just a few tweaks..."

════════════════════════════════════════
LEAP SCHOLAR CONTEXT
════════════════════════════════════════

Audience: Indian students aged 18–30 planning to study abroad.
Destinations covered: USA, UK, Germany, Canada, Australia, Singapore, Ireland, Netherlands, France, Bulgaria, Finland, Switzerland.
Topics: Scholarships, Visa Guides, University Guides, Career Guides, Financial Planning, SOP Writing.
Student: ambitious, cost-conscious, first-generation or aspirational, needs trustworthy information for life-defining decisions.
Voice: mentor-like (not corporate), aspirational (not alarmist), specific (not generic), transparent (not promotional).
Goal: Every blog makes the student feel informed, empowered, and clear on their next step.

════════════════════════════════════════
EDGE CASES
════════════════════════════════════════

Blog <600 words → Flag: minimum 1,000 words required.
No FAQs → Flag: mandatory, suggest 4–5 PAA-style questions.
No meta title/description → Flag and write suggested versions in rewrite.
Multiple CTAs → Flag and remove all except conclusion CTA.
Key Takeaways present → Flag and remove entirely.
First-person phrases → Flag every instance and remove all.
"""


# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE DOC FETCHER
# ─────────────────────────────────────────────────────────────────────────────
def extract_doc_id(url: str):
    for pattern in [r"/document/d/([a-zA-Z0-9_-]+)", r"id=([a-zA-Z0-9_-]+)"]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def fetch_google_doc(url: str):
    doc_id = extract_doc_id(url)
    if not doc_id:
        raise ValueError(
            "Could not find a valid Google Doc ID in this URL.\n"
            "Make sure it's a standard Google Docs link (docs.google.com/document/d/...)."
        )

    # FIX: warn if blog is very long before hitting Gemini
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        resp = requests.get(export_url, timeout=30)
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Network error — could not reach Google Docs. Check your internet connection.")

    if resp.status_code == 403:
        raise PermissionError(
            "Document is private.\n"
            "Please change sharing to 'Anyone with the link can view' and try again."
        )
    if resp.status_code != 200:
        raise ConnectionError(f"Could not fetch document (HTTP {resp.status_code}). Please check the link.")

    text = resp.text.strip()
    if not text:
        raise ValueError("The document appears to be empty.")

    if len(text) > 30000:
        raise ValueError(
            f"This document is very long ({len(text):,} characters). "
            "Please trim it to under ~30,000 characters to avoid Gemini token limit issues."
        )

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0] if lines else "Untitled Blog"
    return text, title


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI API
# ─────────────────────────────────────────────────────────────────────────────
def run_initial_review(api_key: str, blog_text: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=MASTER_PROMPT
    )
    prompt = (
        "Please review the following Leap Scholar blog in full.\n\n"
        "Apply the complete 5-step SOP and all 10 pattern rules (K-1 through K-10).\n\n"
        "Produce BOTH outputs separated by the EXACT markers:\n"
        "---REVIEW DOCUMENT START--- ... ---REVIEW DOCUMENT END---\n"
        "---REWRITTEN BLOG START--- ... ---REWRITTEN BLOG END---\n\n"
        "Here is the blog:\n\n"
        f"{blog_text}"
    )
    response = model.generate_content(prompt)
    return response.text


def run_followup(api_key: str, history: list, user_message: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=MASTER_PROMPT
    )
    chat = model.start_chat(history=history)
    response = chat.send_message(user_message)
    return response.text


# ─────────────────────────────────────────────────────────────────────────────
# PARSE GEMINI RESPONSE
# FIX: Instead of a broken character-split fallback, surface a clear error
# ─────────────────────────────────────────────────────────────────────────────
def parse_response(text: str):
    review, rewrite = "", ""
    m1 = re.search(r"---REVIEW DOCUMENT START---(.*?)---REVIEW DOCUMENT END---", text, re.DOTALL)
    if m1:
        review = m1.group(1).strip()
    m2 = re.search(r"---REWRITTEN BLOG START---(.*?)---REWRITTEN BLOG END---", text, re.DOTALL)
    if m2:
        rewrite = m2.group(1).strip()

    if not review and not rewrite:
        raise ValueError(
            "Gemini did not return the expected output markers.\n\n"
            "This can happen if the blog is too complex or the model hit a limit. "
            "Please try again or use '🔄 New Review' to reset."
        )
    if not review:
        review = "⚠️ Review section was not returned by the model. Please try again."
    if not rewrite:
        rewrite = "⚠️ Rewritten blog was not returned by the model. Please try again."

    return review, rewrite


# ─────────────────────────────────────────────────────────────────────────────
# DOCX HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def add_hr(doc, color="1a56a0"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single')
    b.set(qn('w:sz'), '4')
    b.set(qn('w:space'), '1')
    b.set(qn('w:color'), color)
    pBdr.append(b)
    pPr.append(pBdr)


def mixed_run(para, text):
    """Render **bold** and *italic* markdown inline."""
    # Handle bold first, then italic
    segments = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for part in segments:
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            r = para.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = para.add_run(part[1:-1])
            r.italic = True
        else:
            r = para.add_run(part)
        r.font.size = Pt(11)


# ─────────────────────────────────────────────────────────────────────────────
# SAFE FILENAME HELPER
# FIX: handles unicode/international characters in blog titles
# ─────────────────────────────────────────────────────────────────────────────
def safe_filename(title: str, max_len: int = 40) -> str:
    normalized = unicodedata.normalize('NFKD', title)
    ascii_title = normalized.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^\w\s-]', '', ascii_title)[:max_len].strip()


# ─────────────────────────────────────────────────────────────────────────────
# BUILD REVIEW DOCX
# ─────────────────────────────────────────────────────────────────────────────
def build_review_docx(review_text: str, blog_title: str) -> bytes:
    doc = DocxDocument()
    for sec in doc.sections:
        sec.top_margin = Inches(1)
        sec.bottom_margin = Inches(1)
        sec.left_margin = Inches(1.2)
        sec.right_margin = Inches(1.2)

    # Title block
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LEAP SCHOLAR — BLOG REVIEW")
    r.bold = True; r.font.size = Pt(22)
    r.font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Editorial Review by Krutika AI")
    r2.italic = True; r2.font.size = Pt(11)
    r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8b)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run(f"Generated: {datetime.now().strftime('%d %B %Y')}")
    r3.font.size = Pt(10)
    r3.font.color.rgb = RGBColor(0x94, 0xa3, 0xb8)

    add_hr(doc, "1a56a0")
    doc.add_paragraph()

    in_scorecard = False
    in_priority = False

    for raw_line in review_text.split('\n'):
        s = raw_line.strip()
        if not s:
            doc.add_paragraph(); continue

        if s == "---SCORECARD---":
            in_scorecard = True
            h = doc.add_heading("📊 Scorecard", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue
        if s == "---MACRO SUMMARY---":
            in_scorecard = False
            h = doc.add_heading("📝 Macro Summary", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue
        if s == "---SECTION-WISE REVIEW---":
            h = doc.add_heading("🔍 Section-Wise Review", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue
        if s == "---SEO AUDIT---":
            h = doc.add_heading("🔎 SEO Audit", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue
        if s == "---GRAMMAR & STYLE AUDIT---":
            h = doc.add_heading("✏️ Grammar & Style Audit", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue
        if s == "---PRIORITY ACTION LIST---":
            in_priority = True
            h = doc.add_heading("⚡ Priority Action List", 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            continue

        if s.startswith("BLOG TITLE:"):
            p = doc.add_paragraph()
            r1 = p.add_run("Blog Title:  "); r1.bold = True; r1.font.size = Pt(12)
            p.add_run(s.replace("BLOG TITLE:", "").strip()).font.size = Pt(12)

        elif s.startswith("REVIEW DATE:") or s.startswith("REVIEWER:"):
            p = doc.add_paragraph()
            r = p.add_run(s); r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0x64, 0x74, 0x8b)

        elif s.startswith("OVERALL STATUS:"):
            val = s.replace("OVERALL STATUS:", "").strip()
            p = doc.add_paragraph()
            r1 = p.add_run("Overall Status:  "); r1.bold = True; r1.font.size = Pt(12)
            r2 = p.add_run(val); r2.bold = True; r2.font.size = Pt(12)
            if "APPROVED" in val and "MINOR" not in val:
                r2.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a)
            elif "MINOR" in val:
                r2.font.color.rgb = RGBColor(0xd9, 0x77, 0x06)
            else:
                r2.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)

        elif s.startswith("OVERALL SCORE:"):
            p = doc.add_paragraph()
            r = p.add_run(s); r.bold = True; r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            p.paragraph_format.space_before = Pt(6)

        elif s.startswith("SECTION:"):
            doc.add_paragraph()
            h = doc.add_heading(s.replace("SECTION:", "Section:"), 2)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)

        elif s.startswith("STATUS:"):
            val = s.replace("STATUS:", "").strip()
            p = doc.add_paragraph()
            r = p.add_run(f"Status: {val}"); r.bold = True; r.font.size = Pt(11)
            if "🔴" in val: r.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)
            elif "⚠️" in val: r.font.color.rgb = RGBColor(0xd9, 0x77, 0x06)
            elif "✅" in val: r.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a)

        elif s.startswith("ISSUES FOUND:"):
            p = doc.add_paragraph()
            r = p.add_run("Issues Found:"); r.bold = True; r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0x2e, 0x40, 0x57)

        elif s.startswith("🔴"):
            p = doc.add_paragraph(style='List Bullet')
            r = p.add_run(s); r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)

        elif s.startswith("⚠️"):
            p = doc.add_paragraph(style='List Bullet')
            r = p.add_run(s); r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0xd9, 0x77, 0x06)

        elif s.startswith("✅"):
            p = doc.add_paragraph(style='List Bullet')
            r = p.add_run(s); r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a)

        elif s.startswith("Fix:"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.space_before = Pt(2)
            r1 = p.add_run("Fix: "); r1.bold = True; r1.font.size = Pt(11)
            r1.font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)
            p.add_run(s.replace("Fix:", "").strip()).font.size = Pt(11)

        elif s.startswith("Original:"):
            p = doc.add_paragraph()
            r1 = p.add_run("Original: "); r1.bold = True; r1.font.size = Pt(11)
            r2 = p.add_run(s.replace("Original:", "").strip())
            r2.font.size = Pt(11); r2.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)

        elif in_priority and re.match(r'^\d+\.', s):
            p = doc.add_paragraph(style='List Number')
            r = p.add_run(s); r.font.size = Pt(11)
            if "[CRITICAL]" in s: r.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)
            elif "[HIGH]" in s: r.font.color.rgb = RGBColor(0xd9, 0x77, 0x06)

        elif in_scorecard and re.match(r'^\d+\.', s):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            parts = s.split(":", 1)
            if len(parts) == 2:
                r1 = p.add_run(parts[0] + ":"); r1.bold = True; r1.font.size = Pt(11)
                p.add_run(parts[1]).font.size = Pt(11)
            else:
                p.add_run(s).font.size = Pt(11)

        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.add_run(s).font.size = Pt(11)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# BUILD REWRITTEN BLOG DOCX
# ─────────────────────────────────────────────────────────────────────────────
def build_rewritten_docx(rewritten_text: str, blog_title: str) -> bytes:
    doc = DocxDocument()
    for sec in doc.sections:
        sec.top_margin = Inches(1)
        sec.bottom_margin = Inches(1)
        sec.left_margin = Inches(1.2)
        sec.right_margin = Inches(1.2)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("REWRITTEN BLOG"); r.bold = True; r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x22, 0xc5, 0x5e)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Revised by Krutika AI — Leap Scholar Editorial System")
    r2.italic = True; r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(0x94, 0xa3, 0xb8)

    add_hr(doc, "22c55e")
    doc.add_paragraph()

    for raw_line in rewritten_text.split('\n'):
        s = raw_line.strip()
        if not s:
            doc.add_paragraph(); continue

        if s.startswith("# "):
            h = doc.add_heading(s[2:].strip(), 1)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)

        elif s.startswith("## "):
            h = doc.add_heading(s[3:].strip(), 2)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)

        elif s.startswith("### "):
            h = doc.add_heading(s[4:].strip(), 3)
            if h.runs: h.runs[0].font.color.rgb = RGBColor(0x2e, 0x40, 0x57)

        elif s.startswith("- ") or s.startswith("• "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            mixed_run(p, s[2:].strip())

        elif re.match(r'^\d+\.\s', s):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(3)
            mixed_run(p, re.sub(r'^\d+\.\s*', '', s))

        elif s.startswith("[SOURCE NEEDED"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            r = p.add_run(s); r.bold = True; r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0xdc, 0x26, 0x26)

        elif s.startswith("[TABLE RECOMMENDED"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            r = p.add_run(s); r.bold = True; r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0x1a, 0x56, 0xa0)

        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            mixed_run(p, s)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "messages": [], "phase": "home", "doc_url": "",
    "blog_text": "", "blog_title": "",
    "review_bytes": None, "rewrite_bytes": None,
    "gemini_history": [], "review_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# FIX: st.secrets fallback so key can be pre-set on Streamlit Cloud
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;
                color:#22c55e;margin-bottom:16px;margin-top:8px;">✦ Configuration</div>
    """, unsafe_allow_html=True)

    default_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    api_key = st.text_input(
        "Gemini API Key", type="password", placeholder="AIza...",
        value=default_key,
        help="Get your free key at aistudio.google.com"
    )

    st.markdown("""
    <div style="font-size:0.75rem;color:#6b7280;margin-top:8px;line-height:1.7;">
        Your key is never stored or logged.<br>
        Uses <strong style="color:#22c55e">gemini-2.0-flash</strong><br><br>
        📄 Google Doc must be set to<br><em>"Anyone with the link can view"</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 New Review", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# HOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.phase == "home":

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-logo">✦</div>
        <div class="hero-title">How can I help<br>you <span>today?</span></div>
        <p class="hero-sub">Paste a Google Doc link and I'll review it in Krutika's style —<br>
        section-by-section, with fixes and a fully rewritten version.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="status-badge">
        <span class="status-dot"></span>&nbsp; Krutika AI · Ready
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cards-row">
        <div class="card">
            <div class="card-icon">📋</div>
            <div class="card-title">Section-Wise Review</div>
            <div class="card-desc">Every H2 and H3 reviewed individually with 🔴 issues and ✅ fixes — exactly how Krutika does it.</div>
        </div>
        <div class="card">
            <div class="card-icon">✍️</div>
            <div class="card-title">Rewritten Blog</div>
            <div class="card-desc">A fully rewritten version of your blog incorporating every fix — download-ready as a Word doc.</div>
        </div>
        <div class="card">
            <div class="card-icon">📊</div>
            <div class="card-title">Scorecard + SEO Audit</div>
            <div class="card-desc">10-category scorecard, SEO compliance check, grammar audit, and a priority action list.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="home-input-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        url = st.text_input(
            "", placeholder="✦  Paste your Google Doc link here...",
            key="url_input", label_visibility="collapsed"
        )
    with col2:
        go = st.button("Review →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if go:
        if not api_key:
            st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
        elif not url:
            st.markdown("""
            <div style="text-align:center;color:#ef4444;font-size:0.85rem;margin-top:12px;">
                Please paste a Google Doc link before clicking Review →
            </div>""", unsafe_allow_html=True)
        else:
            with st.spinner("Fetching your Google Doc..."):
                try:
                    blog_text, blog_title = fetch_google_doc(url)
                    st.session_state.update({
                        "doc_url": url, "blog_text": blog_text,
                        "blog_title": blog_title, "phase": "chat",
                        "review_done": False,
                        "messages": [{
                            "role": "ai",
                            "content": (
                                f"✦ Document fetched: **{blog_title}**\n\n"
                                "Running full review against Krutika's guidelines...\n\n"
                                "I'll produce:\n"
                                "**① Section-wise Review Document** (.docx)\n"
                                "**② Rewritten Blog** (.docx)\n\n"
                                "This will take 30–60 seconds. Hang tight."
                            )
                        }]
                    })
                    st.rerun()
                except (ValueError, PermissionError, ConnectionError) as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CHAT SCREEN
# ─────────────────────────────────────────────────────────────────────────────
else:

    st.markdown("""
    <div style="padding: 28px 0 8px; display:flex; align-items:center; gap:12px;">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,#22c55e,#16a34a);
                    border-radius:10px;display:flex;align-items:center;justify-content:center;
                    font-size:14px;box-shadow:0 0 12px rgba(34,197,94,0.3);">✦</div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#f0f0f0;">
                Krutika AI</div>
            <div style="font-size:0.72rem;color:#22c55e;letter-spacing:0.05em;text-transform:uppercase;font-weight:500;">
                <span style="display:inline-block;width:5px;height:5px;background:#22c55e;border-radius:50%;
                             margin-right:5px;vertical-align:middle;animation:pulse-dot 2s infinite;"></span>
                Reviewing · Active</div>
        </div>
    </div>
    <div class="section-divider"></div>
    """, unsafe_allow_html=True)

    if st.session_state.doc_url:
        short = (st.session_state.doc_url[:55] + "...") if len(st.session_state.doc_url) > 55 else st.session_state.doc_url
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;
                    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;padding:10px 14px;width:fit-content;max-width:100%;">
            <span style="font-size:13px;">🔗</span>
            <span style="font-size:0.78rem;color:#6b7280;font-family:'DM Sans',sans-serif;
                         overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{short}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── AUTO-TRIGGER REVIEW ──
    if not st.session_state.review_done and st.session_state.blog_text:
        with st.spinner("🔍 Krutika AI is reviewing your blog — 30–60 seconds..."):
            try:
                raw = run_initial_review(api_key, st.session_state.blog_text)
                review_text, rewritten_text = parse_response(raw)

                st.session_state.review_bytes = build_review_docx(review_text, st.session_state.blog_title)
                st.session_state.rewrite_bytes = build_rewritten_docx(rewritten_text, st.session_state.blog_title)
                st.session_state.review_done = True
                st.session_state.gemini_history = [
                    {"role": "user", "parts": [f"Review this Leap Scholar blog:\n\n{st.session_state.blog_text}"]},
                    {"role": "model", "parts": [raw]},
                ]
                st.session_state.messages.append({
                    "role": "ai",
                    "content": (
                        f"✅ Review complete for **{st.session_state.blog_title}**\n\n"
                        "Both documents are ready — download them below.\n\n"
                        "You can also ask me follow-up questions:\n"
                        "- *'Rewrite only the introduction'*\n"
                        "- *'Give me 5 better FAQ questions'*\n"
                        "- *'Make the conclusion more punchy'*"
                    )
                })
                st.rerun()
            except Exception as e:
                st.session_state.review_done = True
                st.session_state.messages.append({
                    "role": "ai",
                    "content": f"❌ Error during review: {e}\n\nCheck your API key in the sidebar and use '🔄 New Review' to reset."
                })
                st.rerun()

    # ── Chat messages ──
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-msg-user">
                <div class="bubble">{msg["content"]}</div>
            </div>""", unsafe_allow_html=True)
        else:
            html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#d1fae5;">\1</strong>', msg["content"])
            html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
            html = html.replace("\n", "<br>")
            st.markdown(f"""
            <div class="chat-msg-ai">
                <div class="ai-avatar">✦</div>
                <div class="bubble">{html}</div>
            </div>""", unsafe_allow_html=True)

    # ── Download panel ──
    if st.session_state.review_done and st.session_state.review_bytes:
        st.markdown("""
        <div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.15);
                    border-radius:16px;padding:20px 24px;margin:8px 0 16px;">
            <div style="font-family:'Syne',sans-serif;font-weight:600;font-size:0.9rem;
                        color:#22c55e;margin-bottom:14px;letter-spacing:0.02em;">
                📥 Your Documents Are Ready
            </div>
        """, unsafe_allow_html=True)

        safe = safe_filename(st.session_state.blog_title)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "📋 Download Review (.docx)",
                data=st.session_state.review_bytes,
                file_name=f"Review_{safe}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, key="dl_review"
            )
        with d2:
            st.download_button(
                "✍️ Download Rewritten Blog (.docx)",
                data=st.session_state.rewrite_bytes,
                file_name=f"Rewritten_{safe}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, key="dl_rewrite"
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # ── Follow-up input (single functional input — decorative duplicate removed) ──
    # FIX: guard added so follow-up only fires after review is complete
    with st.container():
        c1, c2 = st.columns([6, 1])
        with c1:
            follow_up = st.text_input(
                "", placeholder="Ask a follow-up — e.g. 'Rewrite only the intro' or 'Make the conclusion punchier'...",
                key="followup", label_visibility="collapsed"
            )
        with c2:
            send = st.button("Send ✦", key="send_btn")

        if send and follow_up:
            if not api_key:
                st.warning("Please enter your Gemini API key in the sidebar.")
            elif not st.session_state.review_done:
                st.warning("Please wait for the review to complete before sending follow-up questions.")
            elif not st.session_state.gemini_history:
                st.warning("No review context found. Please use '🔄 New Review' to start fresh.")
            else:
                st.session_state.messages.append({"role": "user", "content": follow_up})
                with st.spinner("Krutika AI is thinking..."):
                    try:
                        reply = run_followup(api_key, st.session_state.gemini_history, follow_up)
                        st.session_state.gemini_history += [
                            {"role": "user", "parts": [follow_up]},
                            {"role": "model", "parts": [reply]},
                        ]
                        st.session_state.messages.append({"role": "ai", "content": reply})
                    except Exception as e:
                        st.session_state.messages.append({"role": "ai", "content": f"❌ Error: {e}"})
                st.rerun()
