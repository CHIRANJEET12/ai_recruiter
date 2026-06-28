import sys
import json
import csv
import io
from pathlib import Path

import streamlit as st
import pandas as pd

SRC = Path(__file__).parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DATA_DIR = Path("DATA")
SAMPLE_PATH = DATA_DIR / "sample_candidates.json"

st.set_page_config(page_title="AI Recruiter", layout="wide", page_icon="⊕")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Space+Grotesk:wght@500;600;700&display=swap');
* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif; font-weight: 600; letter-spacing: -0.02em; }
.stApp { background: #F5F4F0; }
.candidate-card { background: #FFFFFF; border-radius: 16px; padding: 20px 24px; margin-bottom: 12px; border: 1px solid #E5E4E2; transition: box-shadow 0.2s; }
.candidate-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.score-bar-bg { background: #F0EFEB; border-radius: 999px; height: 8px; width: 100%; }
.score-bar-fill { border-radius: 999px; height: 8px; background: #B8914A; }
.score-label { font-size: 13px; color: #71717A; font-weight: 500; }
.score-value { font-size: 14px; font-weight: 600; color: #18181B; }
.rank-badge { font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 700; color: #B8914A; letter-spacing: 0.02em; }
.candidate-name { font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600; color: #18181B; }
.candidate-headline { font-size: 13px; color: #71717A; margin-top: 2px; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 600; color: #18181B; margin-bottom: 16px; }
.jd-box { background: #FFFFFF; border-radius: 12px; padding: 20px 24px; border: 1px solid #E5E4E2; font-size: 14px; line-height: 1.7; color: #3F3F46; white-space: pre-wrap; }
.stat-label { font-size: 12px; color: #A1A1AA; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }
.stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; color: #18181B; }
.divider { border: none; border-top: 1px solid #E5E4E2; margin: 4px 0; }
.pipeline-box { background: #FFFFFF; border-radius: 12px; padding: 16px 20px; border: 1px solid #E5E4E2; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

JD_TEXT = """Looking for a senior applied AI engineer who has successfully built and shipped
production-grade retrieval, ranking, search, recommendation, or matching systems
used by real users in product companies.

The ideal candidate combines strong machine learning depth with a product-focused
execution mindset. They should have hands-on experience designing semantic retrieval
pipelines using embeddings, vector databases, hybrid search, and LLM-based ranking
or re-ranking systems.

Experience handling:
- embedding drift, retrieval quality degradation, index refreshes
- evaluation frameworks and online experimentation

Strong candidates have owned search systems, recommendation systems,
candidate matching systems, marketplace ranking systems, or information retrieval systems.

Required skills: Python, Information Retrieval, Embeddings, Vector Databases,
Pinecone, Milvus, Qdrant, FAISS, Hybrid Search, Semantic Search, Ranking,
Retrieval, Learning to Rank, NLP, Sentence Transformers, Production ML Systems

Evaluation experience: NDCG, MRR, MAP, A/B Testing, Offline/Online Evaluation"""

@st.cache_data
def load_sample():
    if not SAMPLE_PATH.exists():
        return []
    with open(SAMPLE_PATH) as f:
        return json.load(f)

@st.cache_data
def parse_upload(contents, filename):
    if filename.endswith(".jsonl"):
        return [json.loads(line) for line in contents.decode().strip().splitlines() if line.strip()]
    return json.loads(contents.decode())

@st.cache_resource
def get_cross_encoder():
    from ranking.cross_encoder import CrossEncoderRanker
    return CrossEncoderRanker()

def candidate_to_text(c):
    profile = c.get("profile", {})
    skills = [s["name"] for s in c.get("skills", []) if s.get("name")]
    recent = []
    for job in c.get("career_history", [])[:3]:
        title = job.get("title", "").strip()
        company = job.get("company", "").strip()
        if title or company:
            recent.append(f"{title} at {company}")
    return (
        f"Current Title: {profile.get('current_title', '').strip()}\n"
        f"Experience: {profile.get('years_of_experience', 0)} years\n"
        f"Industry: {profile.get('current_industry', '').strip()}\n"
        f"Skills: {', '.join(skills)}\n"
        f"Recent Roles: {' | '.join(recent)}\n"
        f"Headline: {profile.get('headline', '').strip()}\n"
        f"Summary: {profile.get('summary', '').strip()}"
    )

def run_pipeline(candidates, jd_text, progress_bar, status_text):
    from ranking.rule_engine import RuleBasedReranker
    from ranking.main import RankingEngine
    from ranking.schemas import CandidateComponentScores
    from jd_understanding.parser import JDParserEngine
    from intelligence.main import Intelligence

    status_text.text("Building candidate profiles…")
    for c in candidates:
        c["text"] = candidate_to_text(c)

    status_text.text("Loading cross-encoder model…")
    reranker = get_cross_encoder()
    progress_bar.progress(15)

    status_text.text("Scoring candidates against job description…")
    scored = reranker.rerank(jd_text, candidates, top_k=len(candidates))
    progress_bar.progress(40)

    status_text.text("Applying availability rules…")
    rule_engine = RuleBasedReranker()
    rule_scored = rule_engine.rerank(scored, top_k=len(scored))
    progress_bar.progress(50)

    status_text.text("Running intelligence analysis (career, evidence, behavior, trajectory, honeypot)…")
    for c in rule_scored:
        c.update(Intelligence.score_candidate(c))
    progress_bar.progress(75)

    status_text.text("Computing final JD-weighted ranking…")
    parsed_jd = JDParserEngine.parse(jd_text)
    component_scores = [
        CandidateComponentScores(
            candidate_id=c["candidate_id"],
            cross_score=c.get("cross_score", 50.0),
            experience_score=c.get("experience_score"),
            behavior_score=c.get("behavior_score"),
            evidence_score=c.get("evidence_score"),
            trajectory_score=c.get("trajectory_score"),
        )
        for c in rule_scored
    ]
    ranked = RankingEngine.rank(parsed_jd, component_scores)
    progress_bar.progress(90)

    results = []
    for rank, r in enumerate(ranked, 1):
        results.append({
            "candidate_id": r.candidate_id,
            "rank": rank,
            "score": round(r.final_score, 6),
            "reasoning": r.reasoning,
        })

    progress_bar.progress(100)
    status_text.text("Pipeline complete.")
    return results, ranked, rule_scored

col_logo, col_title = st.columns([0.06, 1])
with col_logo:
    st.markdown("<div style='margin-top:6px; font-size:28px;'>⊕</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<div style='font-family:Space Grotesk;font-weight:700;font-size:26px;letter-spacing:-0.03em;color:#18181B;margin-bottom:0;'>AI Recruiter</div><div style='font-size:13px;color:#71717A;margin-top:-2px;'>Intelligent Candidate Discovery & Ranking · Sandbox Demo</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

with st.expander("Job Description", expanded=False):
    st.markdown(f"<div class='jd-box'>{JD_TEXT}</div>", unsafe_allow_html=True)

for k in ["candidates", "results", "enriched", "csv_bytes", "elapsed"]:
    if k not in st.session_state:
        st.session_state[k] = None

sample = load_sample()
data_tab, upload_tab = st.tabs(["Sample Data (100 candidates)", "Upload Custom File"])

with data_tab:
    if sample:
        st.markdown(f"<div class='pipeline-box' style='margin-bottom:16px;'><strong>{len(sample)}</strong> pre-loaded candidates from <code>DATA/sample_candidates.json</code></div>", unsafe_allow_html=True)
        if st.button("Run Pipeline on Sample Data", type="primary", use_container_width=True):
            for k in ["results", "enriched", "csv_bytes", "elapsed"]:
                st.session_state[k] = None
            st.session_state.candidates = sample
            st.rerun()

with upload_tab:
    uploaded = st.file_uploader("Upload candidates.json or .jsonl", type=["json", "jsonl"], label_visibility="collapsed")
    if uploaded:
        try:
            parsed = parse_upload(uploaded.getvalue(), uploaded.name)
            st.markdown(f"<div class='pipeline-box' style='margin-bottom:16px;'><strong>{len(parsed)}</strong> candidates loaded from <code>{uploaded.name}</code></div>", unsafe_allow_html=True)
            if st.button("Run Pipeline on Uploaded Data", type="primary", use_container_width=True):
                for k in ["results", "enriched", "csv_bytes", "elapsed"]:
                    st.session_state[k] = None
                st.session_state.candidates = parsed
                st.rerun()
        except Exception as e:
            st.error(f"Failed to parse file: {e}")

candidates = st.session_state.candidates

if candidates:
    cand_list = candidates[:100] if len(candidates) > 100 else candidates
    if len(candidates) > 100:
        st.warning(f"Dataset contains {len(candidates)} candidates. Only the first 100 will be used (sandbox limit).")

    results = st.session_state.results
    enriched = st.session_state.enriched
    csv_bytes = st.session_state.csv_bytes
    _elapsed = st.session_state.elapsed

    if results is None:
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Initializing…")

        import time as _time
        _t0 = _time.time()
        try:
            results, ranked_objects, enriched = run_pipeline(cand_list, JD_TEXT, progress_bar, status_text)
            _elapsed = _time.time() - _t0
            csv_buf = io.StringIO()
            writer = csv.DictWriter(csv_buf, fieldnames=["candidate_id", "rank", "score", "reasoning"])
            writer.writeheader()
            writer.writerows(results)
            csv_bytes = csv_buf.getvalue().encode("utf-8")
            st.session_state.results = results
            st.session_state.enriched = enriched
            st.session_state.csv_bytes = csv_bytes
            st.session_state.elapsed = _elapsed
            st.rerun()
        except Exception as e:
            progress_bar.empty()
            status_text.error(f"Pipeline failed: {e}")
            st.error(f"Pipeline error: {e}")
            st.stop()

    _within_limit = _elapsed <= 300
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;padding:14px 20px;background:#{'ECFDF5' if _within_limit else 'FEF2F2'};border:1px solid #{'6EE7B7' if _within_limit else 'FCA5A5'};border-radius:12px;margin-bottom:18px;'>"
        f"<span style='font-size:22px;line-height:1;'>{'✓' if _within_limit else '✗'}</span>"
        f"<div><div style='font-weight:600;color:#{'065F46' if _within_limit else '991B1B'};font-size:15px;'>{'Within time budget' if _within_limit else 'Exceeded time budget'}</div>"
        f"<div style='font-size:13px;color:#{'047857' if _within_limit else 'B91C1C'};'>Pipeline completed in <strong>{_elapsed:.1f}s</strong> of 300s (5 min) CPU budget</div></div></div>",
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='stat-label'>Candidates</div><div class='stat-value'>{len(results)}</div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='stat-label'>Top Score</div><div class='stat-value'>{results[0]['score']}</div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='stat-label'>Min Score</div><div class='stat-value'>{results[-1]['score']}</div>", unsafe_allow_html=True)
    with m4:
        profile_matched = sum(1 for c in enriched if "profile" in c and c["profile"].get("anonymized_name"))
        st.markdown(f"<div class='stat-label'>Profiles Enriched</div><div class='stat-value'>{profile_matched}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.download_button(
        label="Download Ranked CSV",
        data=csv_bytes,
        file_name="ranked_candidates.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Ranked Candidates</div>", unsafe_allow_html=True)

    PAGE_SIZE = 10
    if "page" not in st.session_state:
        st.session_state.page = 0

    total_pages = max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = st.session_state.page
    page_start = page * PAGE_SIZE
    page_end = page_start + PAGE_SIZE
    page_results = results[page_start:page_end]

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if page > 0:
            if st.button("← Previous", use_container_width=True, key="prev_top"):
                st.session_state.page -= 1
                st.rerun()
    with nav_col2:
        st.markdown(f"<div style='text-align:center;font-family:Space Grotesk;font-size:14px;font-weight:500;color:#71717A;padding:6px 0;'>Page {page+1} of {total_pages}  ·  {page_start+1}–{min(page_end, len(results))} of {len(results)}</div>", unsafe_allow_html=True)
    with nav_col3:
        if page < total_pages - 1:
            if st.button("Next →", use_container_width=True, key="next_top"):
                st.session_state.page += 1
                st.rerun()

    enriched_map = {c["candidate_id"]: c for c in enriched}

    for rank_offset, r in enumerate(page_results, 1):
        rank = page_start + rank_offset
        c = enriched_map.get(r["candidate_id"], {})
        profile = c.get("profile", {})
        name = profile.get("anonymized_name", r["candidate_id"])
        headline = profile.get("headline", "")
        skills_list = [s["name"] for s in c.get("skills", [])]

        cross = r.get("cross_score") or c.get("cross_score", 0)
        if isinstance(cross, float) and cross <= 1:
            cross = cross * 100
        career = c.get("career_match_score", 0)
        evidence = c.get("evidence_score", 0)
        behavior = c.get("behavior_score", 0)
        experience = c.get("experience_score", 0)
        trajectory = c.get("trajectory_score", 0)
        honeypot = c.get("honeypot_score", 0)

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
                    <div style='font-family:Space Grotesk;font-size:24px;font-weight:700;color:#18181B;'>{r['score']}</div>
                    <div class='stat-label' style='font-size:11px;'>final score</div>
                </div>
            </div>
            <div style='display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;'>
                <div><div class='score-label'>Cross-Encoder</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(cross), 100)}%'></div></div><div class='score-value'>{cross}</div></div>
                <div><div class='score-label'>Career Match</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(career), 100)}%'></div></div><div class='score-value'>{career}</div></div>
                <div><div class='score-label'>Evidence</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(evidence), 100)}%'></div></div><div class='score-value'>{evidence}</div></div>
                <div><div class='score-label'>Behavioral</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(behavior), 100)}%'></div></div><div class='score-value'>{behavior}</div></div>
                <div><div class='score-label'>Experience</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(experience), 100)}%'></div></div><div class='score-value'>{experience}</div></div>
                <div><div class='score-label'>Trajectory</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(trajectory), 100)}%'></div></div><div class='score-value'>{trajectory}</div></div>
                <div><div class='score-label'>Honeypot (inv.)</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{max(0, 100 - float(honeypot) * 10)}%'></div></div><div class='score-value'>{100 - float(honeypot) * 10:.0f}</div></div>
                <div><div class='score-label'>JD Weighted</div><div class='score-bar-bg'><div class='score-bar-fill' style='width:{min(float(r['score']) * 100, 100)}%'></div></div><div class='score-value'>{r['score']}</div></div>
            </div>
            <div style='margin-top:10px;font-size:13px;color:#52525B;font-style:italic;'>“{r['reasoning']}”</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View Profile", expanded=False):
            if profile:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Location:** {profile.get('location', '—')}, {profile.get('country', '—')}")
                    st.markdown(f"**Current Title:** {profile.get('current_title', '—')}")
                    st.markdown(f"**Company:** {profile.get('current_company', '—')} ({profile.get('current_company_size', '—')})")
                    st.markdown(f"**Industry:** {profile.get('current_industry', '—')}")
                    st.markdown(f"**Experience:** {profile.get('years_of_experience', '—')} years")
                with col_b:
                    st.markdown(f"**Skills ({len(skills_list)}):** {', '.join(skills_list[:12])}")
                    st.markdown(f"**Headline:** {profile.get('headline', '—')}")
                    st.markdown(f"**Summary:** {profile.get('summary', '')[:300]}")
            else:
                st.markdown(f"*No profile data for {r['candidate_id']}*")

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

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="Download Ranked CSV",
        data=csv_bytes,
        file_name="ranked_candidates.csv",
        mime="text/csv",
        use_container_width=True,
    )
