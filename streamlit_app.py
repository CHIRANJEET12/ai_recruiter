import json
from pathlib import Path

import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Recruiter", layout="wide", page_icon="⊕")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Space+Grotesk:wght@500;600;700&display=swap');

* { font-family: 'DM Sans', sans-serif; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    letter-spacing: -0.02em;
}

.stApp {
    background: #F5F4F0;
}

.candidate-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid #E5E4E2;
    transition: box-shadow 0.2s;
}
.candidate-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.score-bar-bg {
    background: #F0EFEB;
    border-radius: 999px;
    height: 8px;
    width: 100%;
}
.score-bar-fill {
    border-radius: 999px;
    height: 8px;
    background: #B8914A;
}
.score-label {
    font-size: 13px;
    color: #71717A;
    font-weight: 500;
}
.score-value {
    font-size: 14px;
    font-weight: 600;
    color: #18181B;
}
.rank-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #B8914A;
    letter-spacing: 0.02em;
}
.candidate-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: #18181B;
}
.candidate-headline {
    font-size: 13px;
    color: #71717A;
    margin-top: 2px;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #18181B;
    margin-bottom: 16px;
}
.jd-box {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #E5E4E2;
    font-size: 14px;
    line-height: 1.7;
    color: #3F3F46;
    white-space: pre-wrap;
}
.stat-label {
    font-size: 12px;
    color: #A1A1AA;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}
.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #18181B;
}
.divider {
    border: none;
    border-top: 1px solid #E5E4E2;
    margin: 4px 0;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("DATA")
SUBMISSION_DIR = Path("submission")

@st.cache_data
def load_scores():
    path = SUBMISSION_DIR / "candidate_scores.json"
    if not path.exists():
        path = Path("src") / "final_ranked_candidates.csv"
        if path.exists():
            df = pd.read_csv(path)
            return df.to_dict("records")
        return []
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_profiles():
    path = DATA_DIR / "sample_candidates.json"
    if not path.exists():
        return {}
    with open(path) as f:
        data = json.load(f)
    return {c["candidate_id"]: c for c in data}

scores = load_scores()
profiles = load_profiles()

jd_text = """Looking for a senior applied AI engineer who has successfully built and shipped
production-grade retrieval, ranking, search, recommendation, or matching systems
used by real users in product companies.

The ideal candidate combines strong machine learning depth with a product-focused
execution mindset. They should have hands-on experience designing semantic retrieval
pipelines using embeddings, vector databases, hybrid search, and LLM-based ranking
or re-ranking systems."""

if not scores:
    st.error("No candidate scores found. Run the pipeline first.")
    st.stop()

for c in scores:
    cid = c["candidate_id"]
    profile = profiles.get(cid, {}).get("profile", {})
    c["_name"] = profile.get("anonymized_name", cid)
    c["_headline"] = profile.get("headline", "")
    c["_skills"] = [s["name"] for s in profiles.get(cid, {}).get("skills", [])]

scores.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

total = len(scores)
avg_score = round(sum(s.get("overall_score", 0) for s in scores) / total, 1)

col_logo, col_title = st.columns([0.06, 1])
with col_logo:
    st.markdown("<div style='margin-top:6px; font-size:28px;'>⊕</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<div style='font-family:Space Grotesk;font-weight:700;font-size:26px;letter-spacing:-0.03em;color:#18181B;margin-bottom:0;'>AI Recruiter</div><div style='font-size:13px;color:#71717A;margin-top:-2px;'>Intelligent Candidate Discovery & Ranking</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='stat-label'>Candidates</div><div class='stat-value'>{total}</div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='stat-label'>Avg Score</div><div class='stat-value'>{avg_score}</div>", unsafe_allow_html=True)
with m3:
    top_score = scores[0]["overall_score"]
    st.markdown(f"<div class='stat-label'>Top Score</div><div class='stat-value'>{top_score}</div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='stat-label'>Min Score</div><div class='stat-value'>{scores[-1]['overall_score']}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("Job Description", expanded=False):
    st.markdown(f"<div class='jd-box'>{jd_text}</div>", unsafe_allow_html=True)

PAGE_SIZE = 10
if "page" not in st.session_state:
    st.session_state.page = 0

total_pages = max(1, (len(scores) + PAGE_SIZE - 1) // PAGE_SIZE)
page = st.session_state.page

page_start = page * PAGE_SIZE
page_end = page_start + PAGE_SIZE
page_scores = scores[page_start:page_end]

nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if page > 0:
        if st.button("← Previous", use_container_width=True, key="prev_top"):
            st.session_state.page -= 1
            st.rerun()
with nav_col2:
    st.markdown(f"<div style='text-align:center;font-family:Space Grotesk;font-size:14px;font-weight:500;color:#71717A;padding:6px 0;'>Page {page+1} of {total_pages}  ·  {page_start+1}–{min(page_end, len(scores))} of {len(scores)}</div>", unsafe_allow_html=True)
with nav_col3:
    if page < total_pages - 1:
        if st.button("Next →", use_container_width=True, key="next_top"):
            st.session_state.page += 1
            st.rerun()

for rank_offset, c in enumerate(page_scores, 1):
    rank = page_start + rank_offset
    name = c["_name"]
    headline = c["_headline"]
    overall = c["overall_score"]
    cross = c.get("cross_score", 0)
    career = c.get("career_match_score", 0)
    evidence = c.get("evidence_score", 0)
    behavior = c.get("behavior_score", 0)
    experience = c.get("experience_score", 0)
    trajectory = c.get("trajectory_score", 0)
    honeypot = c.get("honeypot_score", 0)
    skills = c["_skills"]

    st.markdown(f"""
    <div class='candidate-card'>
        <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;'>
            <div style='display:flex;align-items:center;gap:14px;'>
                <span class='rank-badge'>#{rank:02d}</span>
                <div>
                    <span class='candidate-name'>{name}</span>
                    <div class='candidate-headline'>{headline[:80] + '...' if len(headline) > 80 else headline}</div>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-family:Space Grotesk;font-size:24px;font-weight:700;color:#18181B;'>{overall}</div>
                <div class='stat-label' style='font-size:11px;'>overall</div>
            </div>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;'>
            <div><div class='score-label'>Cross-Encoder</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{cross}%'></div></div><div class='score-value'>{cross}</div></div>
            <div><div class='score-label'>Career Match</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{career}%'></div></div><div class='score-value'>{career}</div></div>
            <div><div class='score-label'>Evidence</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{evidence}%'></div></div><div class='score-value'>{evidence}</div></div>
            <div><div class='score-label'>Behavioral</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{behavior}%'></div></div><div class='score-value'>{behavior}</div></div>
            <div><div class='score-label'>Experience</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{experience}%'></div></div><div class='score-value'>{experience}</div></div>
            <div><div class='score-label'>Trajectory</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{trajectory}%'></div></div><div class='score-value'>{trajectory}</div></div>
            <div><div class='score-label'>Honeypot</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{100 - honeypot}%'></div></div><div class='score-value'>{100 - honeypot}</div></div>
            <div><div class='score-label'>F1 (Career×Evidence)</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(c.get("f1_candidate_score", 0), 100)}%'></div></div><div class='score-value'>{c.get("f1_candidate_score", 0):.1f}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View Profile", expanded=False):
        pid = c["candidate_id"]
        profile = profiles.get(pid, {}).get("profile", {})
        if profile:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Location:** {profile.get('location', '—')}, {profile.get('country', '—')}")
                st.markdown(f"**Current Title:** {profile.get('current_title', '—')}")
                st.markdown(f"**Company:** {profile.get('current_company', '—')} ({profile.get('current_company_size', '—')})")
                st.markdown(f"**Industry:** {profile.get('current_industry', '—')}")
                st.markdown(f"**Experience:** {profile.get('years_of_experience', '—')} years")
            with col_b:
                st.markdown(f"**Skills ({len(skills)}):** {', '.join(skills[:12])}")
                st.markdown(f"**Headline:** {profile.get('headline', '—')}")
                st.markdown(f"**Summary:** {profile.get('summary', '')[:300]}")
        else:
            st.markdown(f"*No profile data for {pid}*")

nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if page > 0:
        if st.button("← Previous", use_container_width=True, key="prev_bottom"):
            st.session_state.page -= 1
            st.rerun()
with nav_col2:
    st.markdown(f"<div style='text-align:center;font-family:Space Grotesk;font-size:14px;font-weight:500;color:#71717A;padding:6px 0;'>Page {page+1} of {total_pages}</div>", unsafe_allow_html=True)
with nav_col3:
    if page < total_pages - 1:
        if st.button("Next →", use_container_width=True, key="next_bottom"):
            st.session_state.page += 1
            st.rerun()
