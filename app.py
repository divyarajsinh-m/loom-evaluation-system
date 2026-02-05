"""
LOOM EVALUATION SYSTEM - Plivo
With Loom URL support, Batch Processing, Ranking & Reports
Supabase persistence, Authentication, Prompt-based KB, Hiring Manager View
"""

import streamlit as st
from google import genai
from google.genai import types
import tempfile
import os
import json
import csv
import time
from datetime import datetime
import PyPDF2
import io
import subprocess
import re
import hashlib
from fpdf import FPDF

# Page config - must be first
st.set_page_config(
    page_title="LOOM EVALUATION SYSTEM | Plivo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional UI CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ===== BASE ===== */
.stApp {
    background: #09090b;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #022c22 0%, #064e3b 50%, #047857 100%);
    border-right: 1px solid rgba(16, 185, 129, 0.15);
    padding-top: 0;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
    color: #ecfdf5 !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5 {
    color: #ffffff !important;
    letter-spacing: -0.01em !important;
}

[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: rgba(255,255,255,0.7) !important; }
[data-testid="stSidebar"] input { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #ffffff !important; border-radius: 8px !important; }
[data-testid="stSidebar"] .stDownloadButton button { background: rgba(255,255,255,0.1) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.2) !important; backdrop-filter: blur(10px); }
[data-testid="stSidebar"] .stDownloadButton button:hover { background: rgba(255,255,255,0.18) !important; }
[data-testid="stSidebar"] .stButton > button { background: rgba(255,255,255,0.12) !important; border: 1px solid rgba(255,255,255,0.2) !important; }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.2) !important; transform: none !important; box-shadow: none !important; }

/* ===== MAIN CONTENT ===== */
.main .block-container { padding: 1.5rem 3rem 3rem; max-width: 1280px; }

.main h1 { color: #fafafa !important; font-weight: 800 !important; font-size: 1.75rem !important; letter-spacing: -0.025em !important; }
.main h2 { color: #f4f4f5 !important; font-weight: 700 !important; font-size: 1.35rem !important; letter-spacing: -0.02em !important; }
.main h3 { color: #e4e4e7 !important; font-weight: 600 !important; font-size: 1.1rem !important; letter-spacing: -0.01em !important; }
.main p, .main span, .main label, .main li { color: #a1a1aa !important; }
.main strong { color: #d4d4d8 !important; }

/* ===== CARDS ===== */
.eval-card {
    background: linear-gradient(145deg, #18181b 0%, #1c1c20 100%);
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.04);
    border: none;
    margin-bottom: 16px;
}

.score-card {
    background: linear-gradient(145deg, #18181b 0%, #1c1c20 100%);
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05);
    border: none;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.score-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.08); }
.score-value { font-size: 40px; font-weight: 800; line-height: 1; margin-bottom: 6px; letter-spacing: -0.03em; }
.score-label { font-size: 11px; color: #71717a; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.score-green { color: #10b981; }
.score-yellow { color: #f59e0b; }
.score-red { color: #ef4444; }

/* ===== RANK CARDS ===== */
.rank-card {
    background: linear-gradient(145deg, #18181b 0%, #1f1f23 100%);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 8px 0;
    border-left: 4px solid #10b981;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.rank-card:hover { transform: translateX(4px); box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
.rank-1 { border-left-color: #fbbf24; background: linear-gradient(145deg, #18181b 0%, #1f1d15 100%); }
.rank-2 { border-left-color: #a1a1aa; background: linear-gradient(145deg, #18181b 0%, #1c1c1e 100%); }
.rank-3 { border-left-color: #d97706; background: linear-gradient(145deg, #18181b 0%, #1e1b15 100%); }

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: #18181b;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #71717a !important;
    font-weight: 500;
    font-size: 13px;
    padding: 10px 20px;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #d4d4d8 !important; background: rgba(255,255,255,0.04); }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 11px 24px !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(5, 150, 105, 0.2) !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ===== FORM INPUTS ===== */
.stTextInput input, .stTextArea textarea {
    background: #18181b !important;
    border: 1.5px solid #27272a !important;
    border-radius: 10px !important;
    color: #fafafa !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    transition: all 0.15s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
    background: #1c1c20 !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #52525b !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
    color: #d4d4d8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    margin-bottom: 4px !important;
    letter-spacing: -0.01em !important;
}

/* ===== SELECTS ===== */
.stSelectbox > div > div {
    background: #18181b !important;
    border: 1.5px solid #27272a !important;
    border-radius: 10px !important;
    color: #fafafa !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background: #18181b;
    border: 2px dashed #27272a;
    border-radius: 14px;
    padding: 24px;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.04);
}

/* ===== RADIO ===== */
.stRadio > div { background: #18181b; border-radius: 10px; padding: 6px 12px; border: 1px solid #27272a; }
.stRadio label { color: #d4d4d8 !important; }

/* ===== CHECKBOX ===== */
.stCheckbox label { color: #d4d4d8 !important; }

/* ===== ALERTS ===== */
.stSuccess { background: rgba(16, 185, 129, 0.08) !important; border-left: 3px solid #10b981 !important; color: #6ee7b7 !important; border-radius: 8px !important; }
.stInfo { background: rgba(59, 130, 246, 0.08) !important; border-left: 3px solid #3b82f6 !important; color: #93c5fd !important; border-radius: 8px !important; }
.stWarning { background: rgba(245, 158, 11, 0.08) !important; border-left: 3px solid #f59e0b !important; color: #fcd34d !important; border-radius: 8px !important; }
.stError { background: rgba(239, 68, 68, 0.08) !important; border-left: 3px solid #ef4444 !important; color: #fca5a5 !important; border-radius: 8px !important; }

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    color: #d4d4d8 !important;
    transition: all 0.15s ease !important;
}
.streamlit-expanderHeader:hover { border-color: #3f3f46 !important; background: #1c1c20 !important; }

/* ===== METRICS ===== */
[data-testid="stMetricValue"] { color: #fafafa !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #71717a !important; font-weight: 500 !important; text-transform: uppercase !important; font-size: 11px !important; letter-spacing: 0.5px !important; }

/* ===== PROGRESS BAR ===== */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #059669, #10b981) !important; border-radius: 8px !important; }

/* ===== APP HEADER ===== */
.app-header {
    background: linear-gradient(145deg, #18181b 0%, #1c1c20 100%);
    padding: 20px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.04);
    display: flex;
    align-items: center;
    gap: 16px;
}
.app-title { font-size: 22px; font-weight: 800; color: #fafafa; margin: 0; letter-spacing: -0.03em; }
.app-subtitle { font-size: 13px; color: #71717a; margin: 4px 0 0 0; font-weight: 400; }
.plivo-badge {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: white;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

/* ===== SECTION HEADERS ===== */
.section-header {
    font-size: 11px;
    font-weight: 700;
    color: #10b981;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(16, 185, 129, 0.2);
}

/* ===== FOOTER ===== */
.app-footer {
    text-align: center;
    padding: 28px;
    color: #52525b;
    font-size: 12px;
    border-top: 1px solid #27272a;
    margin-top: 48px;
}
.app-footer a { color: #10b981; text-decoration: none; font-weight: 500; }
.app-footer a:hover { text-decoration: underline; }

/* ===== VIDEO ===== */
video { border-radius: 12px; }

/* ===== LOGIN PAGE ===== */
.login-title {
    text-align: center;
    font-size: 26px;
    font-weight: 800;
    color: #fafafa;
    margin-bottom: 4px;
    letter-spacing: -0.03em;
}
.login-subtitle {
    text-align: center;
    font-size: 14px;
    color: #71717a;
    margin-bottom: 28px;
}

/* ===== MANAGER CARDS ===== */
.manager-card {
    background: linear-gradient(145deg, #18181b 0%, #1c1c20 100%);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.04);
    display: flex;
    align-items: center;
    gap: 16px;
}

/* ===== FORM CONTAINER ===== */
[data-testid="stForm"] {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 14px;
    padding: 24px;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #09090b; }
::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #52525b; }

/* ===== STATUS WIDGET ===== */
[data-testid="stStatusWidget"] { background: #18181b !important; border: 1px solid #27272a !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# Constants
RESULTS_FILE = "evaluation_results.csv"
KB_DIR = "knowledge_base"
BATCH_DIR = "batch_videos"

os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(BATCH_DIR, exist_ok=True)


# ============== SUPABASE DATABASE LAYER ==============

def get_supabase_client():
    """Get Supabase client using st.secrets, returns None if not configured"""
    if "supabase_client" in st.session_state and st.session_state.supabase_client is not None:
        return st.session_state.supabase_client
    try:
        from supabase import create_client
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        if url.startswith("https://xxx") or key.startswith("eyJ..."):
            st.session_state.supabase_client = None
            return None
        client = create_client(url, key)
        st.session_state.supabase_client = client
        return client
    except Exception:
        st.session_state.supabase_client = None
        return None


def save_result(result, candidate_name, assessment_name, evaluation_prompt="", evaluated_by="hr"):
    """Save evaluation result to Supabase (primary) and CSV (fallback)"""
    # Always save to CSV as backup
    _save_result_csv(result, candidate_name, assessment_name, evaluation_prompt, evaluated_by)

    sb = get_supabase_client()
    if sb:
        try:
            sb.table("evaluations").insert({
                "candidate_name": candidate_name,
                "assessment_name": assessment_name,
                "score": int(result.get("score") or 0),
                "demo_score": int(result.get("demo_score") or 0),
                "requirements_score": int(result.get("requirements_score") or 0),
                "communication_score": int(result.get("communication_score") or 0),
                "recommendation": result.get("recommendation", "MAYBE"),
                "summary": result.get("summary", ""),
                "strengths": "|".join(result.get("strengths", [])),
                "improvements": "|".join(result.get("improvements", [])),
                "requirements_met": "|".join(result.get("requirements_met", [])),
                "requirements_missing": "|".join(result.get("requirements_missing", [])),
                "demo_working": result.get("demo_working", False),
                "demo_description": result.get("demo_description", ""),
                "communication_clear": result.get("communication_clear", False),
                "communication_description": result.get("communication_description", ""),
                "key_moments": result.get("key_moments", []),
                "detailed_feedback": result.get("detailed_feedback", ""),
                "evaluation_prompt": evaluation_prompt,
                "evaluated_by": evaluated_by,
            }).execute()
        except Exception as e:
            st.warning(f"Supabase save failed (CSV backup used): {e}")


def _save_result_csv(result, candidate_name, assessment_name, evaluation_prompt="", evaluated_by="hr"):
    """Save result to CSV file (fallback)"""
    exists = os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Timestamp", "Candidate", "Assessment", "Score", "Demo", "Requirements",
                           "Communication", "Recommendation", "Summary", "Strengths", "Improvements",
                           "Met", "Missing", "Demo Working", "Demo Description", "Comm Clear",
                           "Comm Description", "Moments", "Feedback", "Evaluation Prompt", "Evaluated By"])
        writer.writerow([
            datetime.now().isoformat(),
            candidate_name,
            assessment_name,
            result.get("score"),
            result.get("demo_score"),
            result.get("requirements_score"),
            result.get("communication_score"),
            result.get("recommendation"),
            result.get("summary"),
            "|".join(result.get("strengths", [])),
            "|".join(result.get("improvements", [])),
            "|".join(result.get("requirements_met", [])),
            "|".join(result.get("requirements_missing", [])),
            result.get("demo_working"),
            result.get("demo_description", ""),
            result.get("communication_clear"),
            result.get("communication_description", ""),
            json.dumps(result.get("key_moments", [])),
            result.get("detailed_feedback"),
            evaluation_prompt,
            evaluated_by,
        ])


def load_results():
    """Load evaluation results from Supabase (primary) or CSV (fallback)"""
    sb = get_supabase_client()
    if sb:
        try:
            resp = sb.table("evaluations").select("*").order("created_at", desc=True).execute()
            results = []
            for row in resp.data:
                results.append({
                    "Timestamp": row.get("created_at", ""),
                    "Candidate": row.get("candidate_name", ""),
                    "Assessment": row.get("assessment_name", ""),
                    "Score": str(row.get("score", "")),
                    "Demo": str(row.get("demo_score", "")),
                    "Requirements": str(row.get("requirements_score", "")),
                    "Communication": str(row.get("communication_score", "")),
                    "Recommendation": row.get("recommendation", ""),
                    "Summary": row.get("summary", ""),
                    "Strengths": row.get("strengths", ""),
                    "Improvements": row.get("improvements", ""),
                    "Met": row.get("requirements_met", ""),
                    "Missing": row.get("requirements_missing", ""),
                    "Demo Working": str(row.get("demo_working", "")),
                    "Demo Description": row.get("demo_description", ""),
                    "Comm Clear": str(row.get("communication_clear", "")),
                    "Comm Description": row.get("communication_description", ""),
                    "Moments": json.dumps(row.get("key_moments", [])) if isinstance(row.get("key_moments"), list) else row.get("key_moments", ""),
                    "Feedback": row.get("detailed_feedback", ""),
                    "Evaluation Prompt": row.get("evaluation_prompt", ""),
                    "Evaluated By": row.get("evaluated_by", "hr"),
                })
            return results
        except Exception:
            pass

    # Fallback to CSV
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, 'r') as f:
        return list(csv.DictReader(f))


def save_kb_document(assessment_name, doc_name, doc_type, content):
    """Save KB document to Supabase (primary) and filesystem (fallback)"""
    # Always save to filesystem as backup
    assessment_dir = os.path.join(KB_DIR, assessment_name.replace(" ", "_"))
    os.makedirs(assessment_dir, exist_ok=True)
    with open(os.path.join(assessment_dir, f"{doc_type}_{doc_name}.txt"), 'w') as f:
        f.write(content)

    sb = get_supabase_client()
    if sb:
        try:
            # Ensure assessment exists
            existing = sb.table("assessments").select("id").eq("name", assessment_name).execute()
            if not existing.data:
                sb.table("assessments").insert({"name": assessment_name, "description": "", "evaluation_prompt": ""}).execute()

            assessment_id_resp = sb.table("assessments").select("id").eq("name", assessment_name).execute()
            if assessment_id_resp.data:
                assessment_id = assessment_id_resp.data[0]["id"]
                sb.table("knowledge_base").insert({
                    "assessment_id": assessment_id,
                    "doc_name": doc_name,
                    "doc_type": doc_type,
                    "content": content,
                }).execute()
        except Exception as e:
            st.warning(f"Supabase KB save failed (filesystem backup used): {e}")


def load_kb_for_assessment(assessment_name):
    """Load knowledge base documents for an assessment from Supabase (primary) or filesystem (fallback)"""
    sb = get_supabase_client()
    if sb:
        try:
            assessment_resp = sb.table("assessments").select("id").eq("name", assessment_name).execute()
            if assessment_resp.data:
                assessment_id = assessment_resp.data[0]["id"]
                docs_resp = sb.table("knowledge_base").select("*").eq("assessment_id", assessment_id).execute()
                kb = {"job_description": "", "evaluation_criteria": "", "technical_requirements": "", "other": ""}
                for doc in docs_resp.data:
                    dt = doc.get("doc_type", "other")
                    content = doc.get("content", "")
                    if dt == "jd":
                        kb["job_description"] += content + "\n"
                    elif dt == "criteria":
                        kb["evaluation_criteria"] += content + "\n"
                    elif dt == "tech":
                        kb["technical_requirements"] += content + "\n"
                    else:
                        kb["other"] += content + "\n"
                return kb
        except Exception:
            pass

    # Fallback to filesystem
    assessment_dir = os.path.join(KB_DIR, assessment_name.replace(" ", "_"))
    kb = {"job_description": "", "evaluation_criteria": "", "technical_requirements": "", "other": ""}
    if not os.path.exists(assessment_dir):
        return kb
    for filename in os.listdir(assessment_dir):
        filepath = os.path.join(assessment_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            if filename.startswith("jd_"):
                kb["job_description"] += content + "\n"
            elif filename.startswith("criteria_"):
                kb["evaluation_criteria"] += content + "\n"
            elif filename.startswith("tech_"):
                kb["technical_requirements"] += content + "\n"
            else:
                kb["other"] += content + "\n"
    return kb


def get_saved_assessments():
    """Get list of saved assessments from Supabase (primary) or filesystem (fallback)"""
    sb = get_supabase_client()
    if sb:
        try:
            resp = sb.table("assessments").select("name").execute()
            names = [r["name"] for r in resp.data if r.get("name")]
            # Also merge in filesystem assessments
            fs_names = _get_filesystem_assessments()
            all_names = list(set(names + fs_names))
            return sorted(all_names)
        except Exception:
            pass
    return _get_filesystem_assessments()


def _get_filesystem_assessments():
    """Get assessments from filesystem"""
    if not os.path.exists(KB_DIR):
        return []
    return [d.replace("_", " ") for d in os.listdir(KB_DIR) if os.path.isdir(os.path.join(KB_DIR, d))]


def get_assessment_default_prompt(assessment_name):
    """Get default evaluation prompt for an assessment from Supabase"""
    sb = get_supabase_client()
    if sb:
        try:
            resp = sb.table("assessments").select("evaluation_prompt").eq("name", assessment_name).execute()
            if resp.data and resp.data[0].get("evaluation_prompt"):
                return resp.data[0]["evaluation_prompt"]
        except Exception:
            pass
    return ""


def save_assessment_default_prompt(assessment_name, prompt):
    """Save default evaluation prompt for an assessment to Supabase"""
    sb = get_supabase_client()
    if sb:
        try:
            existing = sb.table("assessments").select("id").eq("name", assessment_name).execute()
            if existing.data:
                sb.table("assessments").update({"evaluation_prompt": prompt}).eq("name", assessment_name).execute()
            else:
                sb.table("assessments").insert({"name": assessment_name, "description": "", "evaluation_prompt": prompt}).execute()
            return True
        except Exception as e:
            st.warning(f"Failed to save prompt to Supabase: {e}")
            return False
    else:
        st.warning("Supabase not configured. Default prompts require Supabase.")
        return False


def migrate_csv_to_supabase():
    """One-time migration of CSV results to Supabase"""
    sb = get_supabase_client()
    if not sb:
        st.error("Supabase not configured")
        return 0

    if not os.path.exists(RESULTS_FILE):
        st.info("No CSV results file found")
        return 0

    with open(RESULTS_FILE, 'r') as f:
        rows = list(csv.DictReader(f))

    migrated = 0
    for row in rows:
        try:
            sb.table("evaluations").insert({
                "candidate_name": row.get("Candidate", ""),
                "assessment_name": row.get("Assessment", ""),
                "score": int(row.get("Score") or row.get("Overall Score") or 0),
                "demo_score": int(row.get("Demo") or row.get("Demo Score") or 0),
                "requirements_score": int(row.get("Requirements") or row.get("Requirements Score") or 0),
                "communication_score": int(row.get("Communication") or row.get("Communication Score") or 0),
                "recommendation": row.get("Recommendation", "MAYBE"),
                "summary": row.get("Summary", ""),
                "strengths": row.get("Strengths", ""),
                "improvements": row.get("Improvements", ""),
                "requirements_met": row.get("Met") or row.get("Requirements Met", ""),
                "requirements_missing": row.get("Missing") or row.get("Requirements Missing", ""),
                "demo_working": str(row.get("Demo Working", "")).lower() in ["true", "1", "yes"],
                "demo_description": row.get("Demo Description", ""),
                "communication_clear": str(row.get("Comm Clear") or row.get("Communication Clear", "")).lower() in ["true", "1", "yes"],
                "communication_description": row.get("Comm Description") or row.get("Communication Description", ""),
                "key_moments": json.loads(row.get("Moments") or row.get("Key Moments") or "[]"),
                "detailed_feedback": row.get("Feedback") or row.get("Detailed Feedback", ""),
                "evaluation_prompt": row.get("Evaluation Prompt", ""),
                "evaluated_by": row.get("Evaluated By", "hr"),
            }).execute()
            migrated += 1
        except Exception:
            continue
    return migrated


# ============== AUTHENTICATION ==============

def hash_password(password):
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_hiring_manager(username, password):
    """Check hiring manager credentials against Supabase users table"""
    sb = get_supabase_client()
    if not sb:
        return None
    try:
        resp = sb.table("users").select("*").eq("username", username).eq("active", True).execute()
        if resp.data:
            user = resp.data[0]
            if user["password_hash"] == hash_password(password) and user["role"] == "hiring_manager":
                return user
    except Exception:
        pass
    return None


def add_hiring_manager(username, password, display_name):
    """Add a new hiring manager to Supabase"""
    sb = get_supabase_client()
    if not sb:
        return False, "Supabase not configured"
    try:
        existing = sb.table("users").select("id").eq("username", username).execute()
        if existing.data:
            return False, "Username already exists"
        sb.table("users").insert({
            "username": username,
            "password_hash": hash_password(password),
            "display_name": display_name,
            "role": "hiring_manager",
            "active": True,
        }).execute()
        return True, "Manager added"
    except Exception as e:
        return False, str(e)


def list_hiring_managers():
    """List all hiring managers from Supabase"""
    sb = get_supabase_client()
    if not sb:
        return []
    try:
        resp = sb.table("users").select("id, username, display_name, active, created_at").eq("role", "hiring_manager").order("created_at").execute()
        return resp.data or []
    except Exception:
        return []


def toggle_hiring_manager(user_id, active):
    """Enable or disable a hiring manager"""
    sb = get_supabase_client()
    if not sb:
        return False
    try:
        sb.table("users").update({"active": active}).eq("id", user_id).execute()
        return True
    except Exception:
        return False


def delete_hiring_manager(user_id):
    """Delete a hiring manager from Supabase"""
    sb = get_supabase_client()
    if not sb:
        return False
    try:
        sb.table("users").delete().eq("id", user_id).execute()
        return True
    except Exception:
        return False


def show_login_page():
    """Display login form"""
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; margin-bottom: 20px;">
        <div style="font-size: 48px; margin-bottom: 8px;">🎯</div>
        <div class="login-title">LOOM EVALUATION SYSTEM</div>
        <div class="login-subtitle">Sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                # Check HR admin credentials from secrets
                try:
                    hr_user = st.secrets["auth"]["hr_username"]
                    hr_pass = st.secrets["auth"]["hr_password"]
                except Exception:
                    hr_user = "hr_admin"
                    hr_pass = "admin123"

                if username == hr_user and password == hr_pass:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "hr"
                    st.session_state.username = username
                    st.session_state.display_name = "HR Admin"
                    st.rerun()
                else:
                    # Check hiring managers from Supabase
                    hm_user = authenticate_hiring_manager(username, password)
                    if hm_user:
                        st.session_state.authenticated = True
                        st.session_state.user_role = "hiring_manager"
                        st.session_state.username = hm_user["username"]
                        st.session_state.display_name = hm_user["display_name"]
                        st.rerun()
                    else:
                        st.error("Invalid credentials")


# Initialize auth session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "username" not in st.session_state:
    st.session_state.username = ""
if "display_name" not in st.session_state:
    st.session_state.display_name = ""

# Gate entire app with authentication
if not st.session_state.authenticated:
    show_login_page()
    st.stop()


# ============== HELPER FUNCTIONS ==============

def download_loom_video(loom_url: str, output_path: str) -> bool:
    """Download video from Loom URL using yt-dlp"""
    try:
        loom_url = loom_url.strip()
        if not loom_url:
            return False

        yt_dlp_paths = [
            "/Users/divyaraj.m/Library/Python/3.9/bin/yt-dlp",
            "/usr/local/bin/yt-dlp",
            "/opt/homebrew/bin/yt-dlp",
            "yt-dlp"
        ]

        yt_dlp_cmd = None
        for path in yt_dlp_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    yt_dlp_cmd = path
                    break
            except:
                continue

        if not yt_dlp_cmd:
            st.error("yt-dlp not found")
            return False

        cmd = [
            yt_dlp_cmd,
            "-f", "best[ext=mp4]/best",
            "-o", output_path,
            "--no-playlist",
            "--quiet",
            loom_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0 and os.path.exists(output_path)
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        return False


def get_loom_embed_url(loom_url: str) -> str:
    """Extract Loom video ID and return embed URL"""
    match = re.search(r'loom\.com/share/([a-zA-Z0-9]+)', loom_url)
    if match:
        video_id = match.group(1)
        return f"https://www.loom.com/share/{video_id}"
    return loom_url


def evaluate_loom_url_directly(loom_url, candidate_name, assessment_name, knowledge_base, additional_notes, evaluation_prompt=""):
    """Evaluate Loom video directly from URL without downloading"""
    client = genai.Client(api_key=st.session_state.api_key)

    match = re.search(r'loom\.com/share/([a-zA-Z0-9]+)', loom_url)
    if not match:
        raise Exception("Invalid Loom URL")

    video_id = match.group(1)

    kb_context = ""
    if knowledge_base.get("job_description"):
        kb_context += f"\n## JOB DESCRIPTION\n{knowledge_base['job_description']}"
    if knowledge_base.get("evaluation_criteria"):
        kb_context += f"\n## EVALUATION CRITERIA\n{knowledge_base['evaluation_criteria']}"
    if knowledge_base.get("technical_requirements"):
        kb_context += f"\n## TECHNICAL REQUIREMENTS\n{knowledge_base['technical_requirements']}"

    eval_prompt_section = ""
    if evaluation_prompt:
        eval_prompt_section = f"\n## EVALUATION FOCUS / CUSTOM INSTRUCTIONS\n{evaluation_prompt}\n"

    prompt = f"""I need you to evaluate a candidate's Loom demo video.

The Loom video URL is: {loom_url}
Loom Video ID: {video_id}

**Assessment Type:** {assessment_name}
**Candidate:** {candidate_name}
{kb_context}
{eval_prompt_section}
{f"**Additional Notes:** {additional_notes}" if additional_notes else ""}

Please analyze this Loom recording and provide a detailed JSON response with these exact fields:
{{
    "score": <integer 0-100>,
    "recommendation": "<STRONG_YES|YES|MAYBE|NO>",
    "summary": "<2-3 sentence summary>",
    "demo_score": <integer 0-100>,
    "requirements_score": <integer 0-100>,
    "communication_score": <integer 0-100>,
    "demo_working": <true or false>,
    "demo_description": "<detailed description of what was demonstrated, what worked, what didn't work, and the overall quality of the demo>",
    "communication_clear": <true or false>,
    "communication_description": "<detailed description of the candidate's communication style, clarity, pacing, and presentation skills>",
    "strengths": ["strength 1", "strength 2", ...],
    "improvements": ["area 1", "area 2", ...],
    "requirements_met": ["req 1", "req 2", ...],
    "requirements_missing": ["req 1", "req 2", ...],
    "key_moments": [{{"time": "MM:SS", "note": "description", "type": "positive|negative|neutral"}}],
    "detailed_feedback": "detailed paragraph of feedback"
}}

IMPORTANT: Return ONLY valid JSON, no other text."""

    response = client.models.generate_content(
        model="models/gemini-3-pro-preview",
        contents=[types.Content(parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json")
    )

    try:
        result = json.loads(response.text)
    except:
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {"score": 50, "summary": text[:500], "recommendation": "MAYBE"}

    return result


def download_drive_folder(folder_url: str, output_dir: str) -> list:
    """Download all videos from a Google Drive folder"""
    try:
        match = re.search(r'folders/([a-zA-Z0-9_-]+)', folder_url)
        if not match:
            return []

        folder_id = match.group(1)
        os.makedirs(output_dir, exist_ok=True)

        gdown.download_folder(
            id=folder_id,
            output=output_dir,
            quiet=False,
            use_cookies=False
        )

        video_extensions = ['*.mp4', '*.webm', '*.mov', '*.avi', '*.mkv']
        videos = []
        for ext in video_extensions:
            videos.extend(glob.glob(os.path.join(output_dir, '**', ext), recursive=True))

        return videos
    except Exception as e:
        st.error(f"Drive download error: {str(e)}")
        return []


def download_single_drive_file(file_url: str, output_path: str) -> bool:
    """Download a single file from Google Drive"""
    try:
        match = re.search(r'(?:file/d/|id=)([a-zA-Z0-9_-]+)', file_url)
        if not match:
            return False

        file_id = match.group(1)
        gdown.download(id=file_id, output=output_path, quiet=True)
        return os.path.exists(output_path)
    except Exception as e:
        st.error(f"Drive download error: {str(e)}")
        return False


def extract_text_from_file(uploaded_file) -> str:
    content = uploaded_file.read()
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
        elif filename.endswith('.txt') or filename.endswith('.md'):
            return content.decode('utf-8')
        elif filename.endswith('.docx'):
            import zipfile
            from xml.etree import ElementTree
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                tree = ElementTree.fromstring(z.read('word/document.xml'))
                return " ".join(elem.text for elem in tree.iter() if elem.text)
        return content.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Error: {e}]"


def evaluate_video_with_gemini(video_path, candidate_name, assessment_name, knowledge_base, additional_notes, evaluation_prompt=""):
    client = genai.Client(api_key=st.session_state.api_key)

    with open(video_path, 'rb') as f:
        video_file = client.files.upload(file=f, config=types.UploadFileConfig(mime_type="video/mp4"))

    while video_file.state == "PROCESSING":
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)

    if video_file.state == "FAILED":
        raise Exception("Video processing failed")

    kb_context = ""
    if knowledge_base.get("job_description"):
        kb_context += f"\n## JOB DESCRIPTION\n{knowledge_base['job_description']}"
    if knowledge_base.get("evaluation_criteria"):
        kb_context += f"\n## EVALUATION CRITERIA\n{knowledge_base['evaluation_criteria']}"
    if knowledge_base.get("technical_requirements"):
        kb_context += f"\n## TECHNICAL REQUIREMENTS\n{knowledge_base['technical_requirements']}"

    eval_prompt_section = ""
    if evaluation_prompt:
        eval_prompt_section = f"\n## EVALUATION FOCUS / CUSTOM INSTRUCTIONS\n{evaluation_prompt}\n"

    prompt = f"""Evaluate this candidate's Loom demo video thoroughly.

**Assessment Type:** {assessment_name}
**Candidate:** {candidate_name}
{kb_context}
{eval_prompt_section}
{f"**Additional Notes:** {additional_notes}" if additional_notes else ""}

Analyze the video carefully and provide a detailed JSON response with these exact fields:
{{
    "score": <integer 0-100>,
    "recommendation": "<STRONG_YES|YES|MAYBE|NO>",
    "summary": "<2-3 sentence summary>",
    "demo_score": <integer 0-100>,
    "requirements_score": <integer 0-100>,
    "communication_score": <integer 0-100>,
    "demo_working": <true or false>,
    "demo_description": "<detailed description of what was demonstrated, what worked, what didn't work, and the overall quality of the demo>",
    "communication_clear": <true or false>,
    "communication_description": "<detailed description of the candidate's communication style, clarity, pacing, and presentation skills>",
    "strengths": ["strength 1", "strength 2", ...],
    "improvements": ["area 1", "area 2", ...],
    "requirements_met": ["req 1", "req 2", ...],
    "requirements_missing": ["req 1", "req 2", ...],
    "key_moments": [{{"time": "MM:SS", "note": "description", "type": "positive|negative|neutral"}}],
    "detailed_feedback": "detailed paragraph of feedback"
}}

IMPORTANT: Return ONLY valid JSON, no other text."""

    response = client.models.generate_content(
        model="models/gemini-3-pro-preview",
        contents=[types.Content(parts=[
            types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"),
            types.Part(text=prompt)
        ])],
        config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json")
    )

    try:
        client.files.delete(name=video_file.name)
    except:
        pass

    try:
        result = json.loads(response.text)
    except:
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {"score": 50, "summary": text[:500], "recommendation": "MAYBE"}

    return result


def get_rankings(assessment_filter="All"):
    """Get candidates ranked by score for an assessment"""
    results = load_results()
    if assessment_filter != "All":
        results = [r for r in results if r.get("Assessment") == assessment_filter]

    ranked = sorted(results, key=lambda x: int(x.get("Score") or x.get("Overall Score") or 0), reverse=True)
    return ranked


# ============== ENHANCED PDF REPORTS ==============

def generate_assessment_pdf(assessment_name: str, results: list) -> bytes:
    """Generate PDF report for an assessment with all candidates - Plivo branded"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # Plivo branded green header bar
    pdf.set_fill_color(5, 150, 105)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 8, 'PLIVO', ln=False, align='L')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, 'LOOM EVALUATION SYSTEM', ln=True, align='R')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(12)

    # Title
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, f'Assessment Report: {assessment_name}', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.cell(0, 6, f'Total Candidates: {len(results)}', ln=True, align='C')
    pdf.ln(8)

    # Summary stats
    if results:
        scores = [int(r.get("Score") or r.get("Overall Score") or 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        recs = [r.get("Recommendation", "") for r in results]
        strong_yes = sum(1 for r in recs if r == "STRONG_YES")
        yes_count = sum(1 for r in recs if r == "YES")
        maybe_count = sum(1 for r in recs if r == "MAYBE")
        no_count = sum(1 for r in recs if r == "NO")

        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'SUMMARY STATISTICS', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(95, 6, f'Average Score: {avg_score:.1f}', ln=False)
        pdf.cell(95, 6, f'Score Range: {min_score} - {max_score}', ln=True)
        pdf.cell(0, 6, f'Recommendations: {strong_yes} Strong Yes | {yes_count} Yes | {maybe_count} Maybe | {no_count} No', ln=True)
        pdf.ln(5)

    # Rankings table header
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(5, 150, 105)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(12, 8, 'Rank', border=1, fill=True)
    pdf.cell(45, 8, 'Candidate', border=1, fill=True)
    pdf.cell(20, 8, 'Score', border=1, fill=True)
    pdf.cell(30, 8, 'Recommend', border=1, fill=True)
    pdf.cell(83, 8, 'Summary', border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    pdf.set_font('Helvetica', '', 8)
    for idx, r in enumerate(results[:20], 1):
        score = str(r.get("Score") or r.get("Overall Score") or "-")
        candidate = str(r.get("Candidate", "Unknown"))[:22]
        rec = str(r.get("Recommendation", "-"))[:12]
        summary = str(r.get("Summary", "") or "")[:45]
        if len(str(r.get("Summary", ""))) > 45:
            summary += "..."

        pdf.cell(12, 7, str(idx), border=1)
        pdf.cell(45, 7, candidate, border=1)
        pdf.cell(20, 7, score, border=1)
        pdf.cell(30, 7, rec, border=1)
        pdf.cell(83, 7, summary, border=1)
        pdf.ln()

    # Detailed results for each candidate
    pdf.add_page()

    # Repeat branded header
    pdf.set_fill_color(5, 150, 105)
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(4)
    pdf.cell(0, 8, f'Detailed Candidate Reports - {assessment_name}', ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    for idx, r in enumerate(results, 1):
        if pdf.get_y() > 240:
            pdf.add_page()

        # Candidate header with green accent
        pdf.set_fill_color(5, 150, 105)
        pdf.rect(10, pdf.get_y(), 3, 7, 'F')
        pdf.set_font('Helvetica', 'B', 11)
        candidate_name = str(r.get("Candidate", "Unknown"))
        pdf.cell(5, 7, '', ln=False)
        pdf.cell(0, 7, f'{idx}. {candidate_name}', ln=True)

        pdf.set_font('Helvetica', '', 9)
        score_val = r.get("Score") or r.get("Overall Score") or "-"
        rec_val = r.get("Recommendation", "-")
        pdf.cell(0, 5, f'Score: {score_val} | Recommendation: {rec_val}', ln=True)

        demo_val = r.get("Demo Score") or r.get("Demo") or "-"
        req_val = r.get("Requirements Score") or r.get("Requirements") or "-"
        comm_val = r.get("Communication Score") or r.get("Communication") or "-"
        pdf.cell(0, 5, f'Demo: {demo_val} | Requirements: {req_val} | Communication: {comm_val}', ln=True)

        # Demo Working & Communication Clear
        demo_working = r.get('Demo Working', '')
        demo_w_text = "Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "No" if demo_working else "-"
        comm_clear = r.get('Comm Clear') or r.get('Communication Clear', '')
        comm_c_text = "Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "No" if comm_clear else "-"
        pdf.cell(0, 5, f'Demo Working: {demo_w_text} | Communication Clear: {comm_c_text}', ln=True)

        # Summary
        summary_text = str(r.get("Summary", "No summary") or "No summary")[:500]
        pdf.set_font('Helvetica', 'I', 8)
        pdf.multi_cell(190, 4, f'Summary: {summary_text}')

        # Demo Description
        demo_desc = r.get("Demo Description", "")
        if demo_desc:
            pdf.set_font('Helvetica', '', 8)
            pdf.multi_cell(190, 4, f'Demo: {str(demo_desc)[:400]}')

        # Communication Description
        comm_desc = r.get("Comm Description") or r.get("Communication Description", "")
        if comm_desc:
            pdf.multi_cell(190, 4, f'Communication: {str(comm_desc)[:400]}')

        # Requirements Met
        req_met = r.get("Requirements Met") or r.get("Met", "")
        if req_met:
            met_text = str(req_met).replace("|", ", ")[:300]
            pdf.set_font('Helvetica', '', 8)
            pdf.multi_cell(190, 4, f'Requirements Met: {met_text}')

        # Requirements Missing
        req_missing = r.get("Requirements Missing") or r.get("Missing", "")
        if req_missing:
            missing_text = str(req_missing).replace("|", ", ")[:300]
            pdf.multi_cell(190, 4, f'Requirements Missing: {missing_text}')

        # Strengths
        strengths = r.get("Strengths", "")
        if strengths:
            strengths_text = str(strengths).replace("|", ", ")[:300]
            pdf.multi_cell(190, 4, f'Strengths: {strengths_text}')

        # Improvements
        improvements = r.get("Improvements", "")
        if improvements:
            improvements_text = str(improvements).replace("|", ", ")[:300]
            pdf.multi_cell(190, 4, f'Improvements: {improvements_text}')

        # Key Moments
        moments_raw = r.get('Key Moments') or r.get('Moments', '')
        if moments_raw:
            try:
                moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
                if moments and isinstance(moments, list):
                    pdf.set_font('Helvetica', 'B', 8)
                    pdf.cell(0, 4, 'Key Moments:', ln=True)
                    pdf.set_font('Helvetica', '', 7)
                    for m in moments[:8]:
                        time_str = m.get('time', '')
                        note = m.get('note', '')
                        moment_type = m.get('type', 'neutral')
                        marker = "[+]" if moment_type == 'positive' else "[-]" if moment_type == 'negative' else "[o]"
                        pdf.cell(0, 3.5, f'  {marker} {time_str} - {note[:80]}', ln=True)
            except Exception:
                pass

        # Detailed Feedback
        feedback = r.get("Detailed Feedback") or r.get("Feedback", "")
        if feedback:
            pdf.set_font('Helvetica', '', 8)
            pdf.multi_cell(190, 4, f'Feedback: {str(feedback)[:500]}')

        pdf.ln(4)

    # Footer
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f'Generated by Plivo LOOM EVALUATION SYSTEM on {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')

    return bytes(pdf.output())


def generate_candidate_pdf(result: dict) -> bytes:
    """Generate PDF report for a single candidate - Plivo branded"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # Plivo branded green header bar
    pdf.set_fill_color(5, 150, 105)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(6)
    pdf.cell(0, 8, 'PLIVO', ln=False, align='L')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, 'Candidate Evaluation Report', ln=True, align='R')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(12)

    # Candidate info
    candidate_name = str(result.get("Candidate", "Unknown"))
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, f'Candidate: {candidate_name}', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f'Assessment: {result.get("Assessment", "-")}', ln=True)
    timestamp = str(result.get("Timestamp", ""))[:10] if result.get("Timestamp") else "-"
    pdf.cell(0, 6, f'Date: {timestamp}', ln=True)
    evaluated_by = result.get("Evaluated By", "hr")
    if evaluated_by:
        pdf.cell(0, 6, f'Evaluated By: {evaluated_by.replace("_", " ").title()}', ln=True)
    pdf.ln(8)

    # Scores box
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(5, 150, 105)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, '  SCORES', ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 10)
    score = result.get("Score") or result.get("Overall Score") or "-"
    rec = result.get("Recommendation", "-")
    pdf.cell(95, 7, f'Overall Score: {score}', border=1)
    pdf.cell(95, 7, f'Recommendation: {rec}', border=1, ln=True)

    demo = result.get("Demo Score") or result.get("Demo") or "-"
    req = result.get("Requirements Score") or result.get("Requirements") or "-"
    comm = result.get("Communication Score") or result.get("Communication") or "-"
    pdf.cell(63, 7, f'Demo: {demo}', border=1)
    pdf.cell(63, 7, f'Requirements: {req}', border=1)
    pdf.cell(64, 7, f'Communication: {comm}', border=1, ln=True)

    # Demo Working & Communication Clear
    demo_working = result.get('Demo Working', '')
    demo_w_text = "Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "No" if demo_working else "-"
    comm_clear = result.get('Comm Clear') or result.get('Communication Clear', '')
    comm_c_text = "Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "No" if comm_clear else "-"
    pdf.cell(95, 7, f'Demo Working: {demo_w_text}', border=1)
    pdf.cell(95, 7, f'Communication Clear: {comm_c_text}', border=1, ln=True)
    pdf.ln(8)

    # Summary
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, 'SUMMARY', ln=True)
    pdf.set_font('Helvetica', '', 9)
    summary_text = str(result.get("Summary", "No summary available") or "No summary available")[:1000]
    pdf.multi_cell(190, 5, summary_text)
    pdf.ln(5)

    # Demo Description
    demo_desc = result.get("Demo Description", "")
    if demo_desc:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'DEMO DESCRIPTION', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(190, 5, str(demo_desc)[:1500])
        pdf.ln(5)

    # Communication Description
    comm_desc = result.get("Comm Description") or result.get("Communication Description", "")
    if comm_desc:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'COMMUNICATION DESCRIPTION', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(190, 5, str(comm_desc)[:1500])
        pdf.ln(5)

    # Requirements Met
    req_met = result.get("Requirements Met") or result.get("Met", "")
    if req_met:
        if pdf.get_y() > 240:
            pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'REQUIREMENTS MET', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for req_item in str(req_met).split("|"):
            if req_item.strip():
                pdf.cell(0, 5, f'  + {req_item.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Requirements Missing
    req_missing = result.get("Requirements Missing") or result.get("Missing", "")
    if req_missing:
        if pdf.get_y() > 240:
            pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'REQUIREMENTS MISSING', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for req_item in str(req_missing).split("|"):
            if req_item.strip():
                pdf.cell(0, 5, f'  - {req_item.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Strengths
    strengths = result.get("Strengths", "")
    if strengths:
        if pdf.get_y() > 240:
            pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'STRENGTHS', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for s in str(strengths).split("|"):
            if s.strip():
                pdf.cell(0, 5, f'  + {s.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Improvements
    improvements = result.get("Improvements", "")
    if improvements:
        if pdf.get_y() > 240:
            pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'AREAS FOR IMPROVEMENT', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for i in str(improvements).split("|"):
            if i.strip():
                pdf.cell(0, 5, f'  - {i.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Key Moments
    moments_raw = result.get('Key Moments') or result.get('Moments', '')
    if moments_raw:
        try:
            moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
            if moments and isinstance(moments, list):
                if pdf.get_y() > 240:
                    pdf.add_page()
                pdf.set_font('Helvetica', 'B', 11)
                pdf.cell(0, 7, 'KEY MOMENTS', ln=True)
                pdf.set_font('Helvetica', '', 9)
                for m in moments:
                    time_str = m.get('time', '')
                    note = m.get('note', '')
                    moment_type = m.get('type', 'neutral')
                    marker = "[+]" if moment_type == 'positive' else "[-]" if moment_type == 'negative' else "[o]"
                    pdf.cell(0, 5, f'  {marker} {time_str} - {note[:100]}', ln=True)
                pdf.ln(5)
        except Exception:
            pass

    # Detailed feedback
    feedback = result.get("Detailed Feedback") or result.get("Feedback") or ""
    if feedback:
        if pdf.get_y() > 240:
            pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'DETAILED FEEDBACK', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(190, 5, str(feedback)[:2000])

    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f'Generated by Plivo LOOM EVALUATION SYSTEM on {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')

    return bytes(pdf.output())


def generate_assessment_csv(results: list) -> str:
    """Generate CSV for assessment results"""
    output = io.StringIO()
    if results:
        fieldnames = ["Rank", "Candidate", "Overall Score", "Demo Score", "Requirements Score", "Communication Score",
                     "Recommendation", "Demo Working", "Demo Description", "Communication Clear", "Communication Description",
                     "Summary", "Strengths", "Improvements", "Requirements Met", "Requirements Missing", "Detailed Feedback",
                     "Evaluation Prompt", "Evaluated By"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for idx, r in enumerate(results, 1):
            writer.writerow({
                "Rank": idx,
                "Candidate": r.get("Candidate", ""),
                "Overall Score": r.get("Overall Score") or r.get("Score") or "",
                "Demo Score": r.get("Demo Score") or r.get("Demo") or "",
                "Requirements Score": r.get("Requirements Score") or r.get("Requirements") or "",
                "Communication Score": r.get("Communication Score") or r.get("Communication") or "",
                "Recommendation": r.get("Recommendation", ""),
                "Demo Working": r.get("Demo Working", ""),
                "Demo Description": r.get("Demo Description", ""),
                "Communication Clear": r.get("Communication Clear") or r.get("Comm Clear", ""),
                "Communication Description": r.get("Comm Description") or r.get("Communication Description", ""),
                "Summary": r.get("Summary", ""),
                "Strengths": (r.get("Strengths") or "").replace("|", ", "),
                "Improvements": (r.get("Improvements") or "").replace("|", ", "),
                "Requirements Met": (r.get("Requirements Met") or r.get("Met") or "").replace("|", ", "),
                "Requirements Missing": (r.get("Requirements Missing") or r.get("Missing") or "").replace("|", ", "),
                "Detailed Feedback": r.get("Detailed Feedback") or r.get("Feedback") or "",
                "Evaluation Prompt": r.get("Evaluation Prompt", ""),
                "Evaluated By": r.get("Evaluated By", ""),
            })
    return output.getvalue()


def display_evaluation_results(result):
    """Display evaluation results - shared between Single Evaluation and Hiring Manager tabs"""
    st.markdown("---")
    st.markdown("## Evaluation Results")

    c1, c2, c3, c4 = st.columns(4)
    score = result.get('score')
    if score is None:
        score = result.get('overall_score')
    score = int(score) if score is not None else 0

    score_class = "score-green" if score >= 70 else "score-yellow" if score >= 50 else "score-red"
    c1.markdown(f'<div class="score-card"><div class="score-value {score_class}">{score}</div><div class="score-label">Overall Score</div></div>', unsafe_allow_html=True)

    rec = result.get("recommendation") or "MAYBE"
    rec_class = "score-green" if rec in ["STRONG_YES", "YES"] else "score-yellow" if rec == "MAYBE" else "score-red"
    c2.markdown(f'<div class="score-card"><div class="score-value {rec_class}" style="font-size: 24px;">{rec.replace("_", " ")}</div><div class="score-label">Recommendation</div></div>', unsafe_allow_html=True)

    demo_working = result.get("demo_working")
    demo_text = "YES" if demo_working else "NO"
    demo_class = "score-green" if demo_working else "score-red"
    c3.markdown(f'<div class="score-card"><div class="score-value {demo_class}">{demo_text}</div><div class="score-label">Demo Working</div></div>', unsafe_allow_html=True)

    comm_clear = result.get("communication_clear")
    comm_text = "YES" if comm_clear else "NO"
    comm_class = "score-green" if comm_clear else "score-red"
    c4.markdown(f'<div class="score-card"><div class="score-value {comm_class}">{comm_text}</div><div class="score-label">Communication</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Demo Score", f"{result.get('demo_score') or '-'}/100")
    c2.metric("Requirements", f"{result.get('requirements_score') or '-'}/100")
    c3.metric("Communication", f"{result.get('communication_score') or '-'}/100")

    st.markdown("### Summary")
    st.info(result.get("summary", "No summary available"))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Strengths")
        for s in result.get("strengths", []):
            st.markdown(f"- {s}")
    with c2:
        st.markdown("### Areas for Improvement")
        for i in result.get("improvements", []):
            st.markdown(f"- {i}")

    # Requirements
    c1, c2 = st.columns(2)
    with c1:
        req_met = result.get("requirements_met", [])
        if req_met:
            st.markdown("### Requirements Met")
            for r in req_met:
                st.markdown(f"- {r}")
    with c2:
        req_missing = result.get("requirements_missing", [])
        if req_missing:
            st.markdown("### Requirements Missing")
            for r in req_missing:
                st.markdown(f"- {r}")

    # Key moments
    moments = result.get("key_moments", [])
    if moments:
        st.markdown("### Key Moments")
        for m in moments:
            time_str = m.get('time', '')
            note = m.get('note', '')
            moment_type = m.get('type', 'neutral')
            icon = "+" if moment_type == 'positive' else "-" if moment_type == 'negative' else "o"
            st.markdown(f"[{icon}] **{time_str}** - {note}")

    # Detailed feedback
    feedback = result.get("detailed_feedback", "")
    if feedback:
        st.markdown("### Detailed Feedback")
        st.markdown(feedback)


# ============== INITIALIZE SESSION STATE ==============

# Gemini API key: secrets > env var > manual entry
if 'api_key' not in st.session_state:
    try:
        st.session_state.api_key = st.secrets["gemini"]["api_key"]
    except Exception:
        st.session_state.api_key = os.getenv('GOOGLE_GEMINI_API_KEY', '')
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []


# ============== SIDEBAR ==============
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "plivo_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    else:
        st.markdown('<div style="font-size: 28px; font-weight: 700; color: #ffffff;">plivo</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 4px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;">
        LOOM EVALUATION SYSTEM
    </div>
    """, unsafe_allow_html=True)

    # User info and logout
    role_label = "HR Admin" if st.session_state.user_role == "hr" else "Hiring Manager"
    st.markdown(f"**Logged in as:** {st.session_state.display_name or st.session_state.username}")
    st.markdown(f"**Role:** {role_label}")
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.username = ""
        st.session_state.display_name = ""
        st.rerun()

    st.markdown("---")
    st.markdown("##### Settings")

    # Only show API key input if not set from secrets
    try:
        _ = st.secrets["gemini"]["api_key"]
        api_key_from_secrets = True
    except Exception:
        api_key_from_secrets = False

    if not api_key_from_secrets:
        api_key = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password",
                               help="Enter your Google Gemini API key")
        if api_key:
            st.session_state.api_key = api_key

    # Supabase status
    sb = get_supabase_client()
    if sb:
        st.success("Supabase: Connected")
    else:
        st.warning("Supabase: Not configured (using CSV)")

    st.markdown("---")
    st.markdown("##### Statistics")

    col1, col2 = st.columns(2)
    col1.metric("Evaluations", len(load_results()))
    col2.metric("Assessments", len(get_saved_assessments()))

    if os.path.exists(RESULTS_FILE):
        st.markdown("---")
        with open(RESULTS_FILE, 'r') as f:
            st.download_button("Export All Results", f.read(), "evaluations.csv", "text/csv",
                             use_container_width=True)

    # Migration button (HR only)
    if st.session_state.user_role == "hr" and sb and os.path.exists(RESULTS_FILE):
        st.markdown("---")
        if st.button("Migrate CSV to Supabase", use_container_width=True):
            count = migrate_csv_to_supabase()
            st.success(f"Migrated {count} records to Supabase")


# ============== MAIN CONTENT ==============

# Header
st.markdown(f"""
<div class="app-header">
    <div style="flex: 1;">
        <h1 class="app-title">LOOM EVALUATION SYSTEM</h1>
        <p class="app-subtitle">AI-powered technical demo evaluation for hiring</p>
    </div>
    <div class="plivo-badge">PLIVO | {role_label.upper()}</div>
</div>
""", unsafe_allow_html=True)

# Conditional tabs based on role
if st.session_state.user_role == "hr":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Single Evaluation", "Batch Processing", "Rankings",
        "Knowledge Base", "History", "Hiring Manager View", "Manage Users"
    ])
else:
    # Hiring manager only sees evaluation tab
    tab1 = st.tabs(["Evaluation"])[0]
    tab2 = tab3 = tab4 = tab5 = tab6 = tab7 = None

# ============== TAB 1: SINGLE EVALUATION ==============
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">Assessment Details</div>', unsafe_allow_html=True)

        saved = get_saved_assessments()
        if saved:
            use_existing = st.radio("Assessment type", ["Use existing", "Create new"],
                                   horizontal=True, label_visibility="collapsed")
            if use_existing == "Use existing":
                assessment_name = st.selectbox("Select Assessment", saved)
            else:
                assessment_name = st.text_input("Assessment Name", placeholder="e.g., Backend Engineer Q1 2024")
        else:
            assessment_name = st.text_input("Assessment Name", placeholder="e.g., Backend Engineer Q1 2024")

        candidate_name = st.text_input("Candidate Name", placeholder="e.g., John Smith")
        notes = st.text_area("Additional Notes (Optional)",
                            placeholder="Any specific areas to focus on during evaluation...",
                            height=80)

        # Evaluation prompt
        default_prompt = ""
        if assessment_name:
            default_prompt = get_assessment_default_prompt(assessment_name)
        evaluation_prompt = st.text_area(
            "Evaluation Prompt (Optional)",
            value=default_prompt,
            placeholder="Enter custom evaluation instructions in plain English, e.g.: 'Focus on API design patterns, error handling, and whether they explain their architectural decisions clearly.'",
            height=100,
            key="eval_prompt_tab1"
        )

        if assessment_name:
            kb = load_kb_for_assessment(assessment_name)
            if any(kb.values()):
                st.success(f"Knowledge base loaded for **{assessment_name}**")
            else:
                st.info("No evaluation criteria uploaded. Add documents in the Knowledge Base tab.")

    with col2:
        st.markdown('<div class="section-header">Video Input</div>', unsafe_allow_html=True)

        input_method = st.radio("Input Method", ["Loom URL", "Upload File"], horizontal=True)

        video_path = None

        if input_method == "Loom URL":
            loom_url = st.text_input("Loom Share URL", placeholder="https://www.loom.com/share/...")
            if loom_url and st.button("Preview Video"):
                match = re.search(r'loom\.com/share/([a-zA-Z0-9]+)', loom_url)
                if match:
                    video_id = match.group(1)
                    st.markdown(f'<iframe src="https://www.loom.com/embed/{video_id}" width="100%" height="300" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                else:
                    st.warning("Invalid Loom URL format")
        else:
            video = st.file_uploader("Upload Loom Recording", type=["mp4", "webm", "mov"],
                                    help="Download your Loom video and upload it here")
            if video:
                st.video(video)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start Evaluation", type="primary", use_container_width=True, key="single_eval"):
        if not st.session_state.api_key:
            st.error("Please enter your Gemini API key in the sidebar")
        elif not candidate_name:
            st.error("Please enter the candidate's name")
        elif not assessment_name:
            st.error("Please enter or select an assessment")
        elif input_method == "Loom URL" and not loom_url:
            st.error("Please enter a Loom URL")
        elif input_method == "Upload File" and not video:
            st.error("Please upload a video file")
        else:
            with st.status("Processing...", expanded=True) as status:
                try:
                    kb = load_kb_for_assessment(assessment_name)

                    # Determine evaluation prompt to use
                    prompt_to_use = evaluation_prompt or default_prompt
                    tmp_path = None

                    if input_method == "Loom URL":
                        st.write("Attempting to download video from Loom...")
                        tmp_path = tempfile.mktemp(suffix=".mp4")
                        download_success = download_loom_video(loom_url, tmp_path)

                        if download_success:
                            st.write("Uploading to Gemini for analysis...")
                            result = evaluate_video_with_gemini(tmp_path, candidate_name, assessment_name, kb, notes, prompt_to_use)
                        else:
                            st.write("Download not available, analyzing via Loom URL directly...")
                            st.write("Gemini is analyzing the Loom recording...")
                            result = evaluate_loom_url_directly(loom_url, candidate_name, assessment_name, kb, notes, prompt_to_use)
                            tmp_path = None
                    else:
                        tmp_path = tempfile.mktemp(suffix=".mp4")
                        with open(tmp_path, 'wb') as f:
                            f.write(video.read())
                        st.write("Uploading to Gemini for analysis...")
                        result = evaluate_video_with_gemini(tmp_path, candidate_name, assessment_name, kb, notes, prompt_to_use)

                    st.write("Saving results...")
                    save_result(result, candidate_name, assessment_name, prompt_to_use, st.session_state.username)

                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    status.update(label="Evaluation Complete!", state="complete")

                    display_evaluation_results(result)

                except Exception as e:
                    status.update(label="Evaluation Failed", state="error")
                    st.error(f"Error: {str(e)}")

# ============== TAB 2: BATCH PROCESSING (HR Only) ==============
if tab2 is not None:
    with tab2:
        st.markdown('<div class="section-header">Batch Video Processing</div>', unsafe_allow_html=True)
        st.markdown("Process multiple candidate videos at once. Name files as `CandidateName.mp4`")

        batch_assessment = st.selectbox("Assessment Type for Batch", get_saved_assessments() or ["No assessments - create one first"])

        batch_videos = st.file_uploader("Upload Videos", type=["mp4", "webm", "mov"], accept_multiple_files=True,
                                        help="Upload multiple video files. Name them as CandidateName.mp4")
        if batch_videos:
            st.write(f"**{len(batch_videos)} videos selected:**")
            for v in batch_videos:
                candidate = os.path.splitext(v.name)[0]
                st.write(f"- {candidate}")

        if st.button("Start Batch Evaluation", type="primary", use_container_width=True, key="batch_eval"):
            if not st.session_state.api_key:
                st.error("Please enter your Gemini API key")
            elif not batch_assessment or batch_assessment == "No assessments - create one first":
                st.error("Please select or create an assessment first")
            elif not batch_videos:
                st.error("Please upload video files")
            else:
                kb = load_kb_for_assessment(batch_assessment)
                batch_prompt = get_assessment_default_prompt(batch_assessment)
                batch_items = []

                for v in batch_videos:
                    candidate = os.path.splitext(v.name)[0]
                    batch_items.append({"candidate": candidate, "video": v, "type": "file"})

                if batch_items:
                    progress = st.progress(0)

                    for idx, item in enumerate(batch_items):
                        with st.status(f"Processing {item['candidate']}...", expanded=False) as status:
                            try:
                                tmp_path = tempfile.mktemp(suffix=".mp4")
                                with open(tmp_path, 'wb') as f:
                                    f.write(item["video"].read())

                                result = evaluate_video_with_gemini(tmp_path, item["candidate"], batch_assessment, kb, "", batch_prompt)
                                save_result(result, item["candidate"], batch_assessment, batch_prompt, st.session_state.username)

                                if os.path.exists(tmp_path):
                                    os.unlink(tmp_path)

                                score = result.get("score", 0)
                                rec = result.get("recommendation", "MAYBE")
                                status.update(label=f"{item['candidate']}: Score {score}, {rec}", state="complete")

                            except Exception as e:
                                status.update(label=f"{item['candidate']}: Failed - {str(e)}", state="error")

                        progress.progress((idx + 1) / len(batch_items))

                    st.success("Batch processing complete! Check the Rankings tab to see results.")

# ============== TAB 3: RANKINGS (HR Only) ==============
if tab3 is not None:
    with tab3:
        st.markdown('<div class="section-header">Candidate Rankings</div>', unsafe_allow_html=True)

        assessments = list(set(r.get("Assessment", "") for r in load_results() if r.get("Assessment")))
        rank_assessment = st.selectbox("Filter by Assessment", ["All"] + assessments, key="rank_filter")

        ranked = get_rankings(rank_assessment)

        if not ranked:
            st.info("No evaluations yet. Complete some evaluations to see rankings!")
        else:
            st.markdown(f"### Top Candidates ({len(ranked)} total)")

            c1, c2, c3 = st.columns([2, 1, 1])
            with c2:
                pdf_data = generate_assessment_pdf(rank_assessment, ranked)
                st.download_button(
                    "Export PDF",
                    pdf_data,
                    f"assessment_report_{rank_assessment.replace(' ', '_')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            with c3:
                csv_data = generate_assessment_csv(ranked)
                st.download_button(
                    "Export CSV",
                    csv_data,
                    f"assessment_results_{rank_assessment.replace(' ', '_')}.csv",
                    "text/csv",
                    use_container_width=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            for idx, r in enumerate(ranked[:20], 1):
                score = r.get('Score') or r.get('Overall Score') or 0
                rec = r.get('Recommendation', '')
                candidate = r.get('Candidate', 'Unknown')
                assessment = r.get('Assessment', '')

                rank_class = f"rank-{idx}" if idx <= 3 else ""
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
                rec_icon = "🟢" if rec in ["STRONG_YES", "YES"] else "🟡" if rec == "MAYBE" else "🔴"

                st.markdown(f"""
                <div class="rank-card {rank_class}">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="font-size: 28px; min-width: 50px;">{medal}</div>
                        <div style="flex: 1;">
                            <div style="font-size: 18px; font-weight: 600; color: #ffffff;">{candidate}</div>
                            <div style="font-size: 13px; color: #94a3b8;">{assessment}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 32px; font-weight: 700; color: {'#10b981' if int(score) >= 70 else '#f59e0b' if int(score) >= 50 else '#ef4444'};">{score}</div>
                            <div style="font-size: 13px; color: #94a3b8;">{rec_icon} {rec.replace('_', ' ')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"View Details - {candidate}"):
                    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
                    c1.metric("Demo", r.get('Demo Score') or r.get('Demo') or '-')
                    c2.metric("Requirements", r.get('Requirements Score') or r.get('Requirements') or '-')
                    c3.metric("Communication", r.get('Communication Score') or r.get('Communication') or '-')

                    demo_working = r.get('Demo Working', '')
                    demo_working_text = "Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "No" if demo_working else "-"
                    c4.metric("Demo Working", demo_working_text)

                    comm_clear = r.get('Communication Clear') or r.get('Comm Clear', '')
                    comm_clear_text = "Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "No" if comm_clear else "-"
                    c5.metric("Comm Clear", comm_clear_text)

                    candidate_pdf = generate_candidate_pdf(r)
                    st.download_button(
                        "Download PDF Report",
                        candidate_pdf,
                        f"{candidate.replace(' ', '_')}_report.pdf",
                        "application/pdf",
                        key=f"pdf_{idx}_{candidate}",
                        use_container_width=True
                    )

                    st.markdown("---")

                    st.markdown(f"**Summary:**")
                    st.info(r.get('Summary', 'N/A'))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Demo Description:**")
                        demo_desc = r.get('Demo Description', '')
                        if demo_desc:
                            st.markdown(demo_desc)
                        else:
                            st.markdown("_No demo description available_")

                    with col2:
                        st.markdown("**Communication Description:**")
                        comm_desc = r.get('Comm Description') or r.get('Communication Description', '')
                        if comm_desc:
                            st.markdown(comm_desc)
                        else:
                            st.markdown("_No communication description available_")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Strengths:**")
                        strengths = r.get('Strengths', '')
                        if strengths:
                            for s in str(strengths).split("|"):
                                if s.strip():
                                    st.markdown(f"- {s.strip()}")
                        else:
                            st.markdown("_No strengths recorded_")

                    with col2:
                        st.markdown("**Areas for Improvement:**")
                        improvements = r.get('Improvements', '')
                        if improvements:
                            for i in str(improvements).split("|"):
                                if i.strip():
                                    st.markdown(f"- {i.strip()}")
                        else:
                            st.markdown("_No improvements recorded_")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Requirements Met:**")
                        req_met = r.get('Requirements Met') or r.get('Met', '')
                        if req_met:
                            for req in str(req_met).split("|"):
                                if req.strip():
                                    st.markdown(f"- {req.strip()}")
                        else:
                            st.markdown("_No requirements data_")

                    with col2:
                        st.markdown("**Requirements Missing:**")
                        req_missing = r.get('Requirements Missing') or r.get('Missing', '')
                        if req_missing:
                            for req in str(req_missing).split("|"):
                                if req.strip():
                                    st.markdown(f"- {req.strip()}")
                        else:
                            st.markdown("_None - All requirements met!_")

                    st.markdown("**Key Moments:**")
                    moments_raw = r.get('Key Moments') or r.get('Moments', '')
                    if moments_raw:
                        try:
                            moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
                            if moments and isinstance(moments, list):
                                for m in moments:
                                    time_str = m.get('time', '')
                                    note = m.get('note', '')
                                    moment_type = m.get('type', 'neutral')
                                    icon = "+" if moment_type == 'positive' else "-" if moment_type == 'negative' else "o"
                                    st.markdown(f"[{icon}] **{time_str}** - {note}")
                            else:
                                st.markdown("_No key moments recorded_")
                        except:
                            st.markdown(f"_{moments_raw}_")
                    else:
                        st.markdown("_No key moments recorded_")

                    st.markdown("**Detailed Feedback:**")
                    detailed_feedback = r.get('Detailed Feedback') or r.get('Feedback', '')
                    if detailed_feedback:
                        st.markdown(detailed_feedback)
                    else:
                        st.markdown("_No detailed feedback available_")

# ============== TAB 4: KNOWLEDGE BASE (HR Only) ==============
if tab4 is not None:
    with tab4:
        st.markdown('<div class="section-header">Knowledge Base Management</div>', unsafe_allow_html=True)
        st.markdown("Upload evaluation criteria, job descriptions, and requirements for each assessment type.")

        kb_name = st.text_input("Assessment Name", key="kb_assessment", placeholder="e.g., Backend Engineer Q1 2024")

        if kb_name:
            # Default evaluation prompt for this assessment
            st.markdown("---")
            st.markdown("**Default Evaluation Prompt**")
            st.markdown("_This prompt will be automatically loaded when evaluating candidates for this assessment._")
            current_prompt = get_assessment_default_prompt(kb_name)
            new_prompt = st.text_area(
                "Default Evaluation Prompt",
                value=current_prompt,
                placeholder="Enter default evaluation instructions, e.g.: 'Focus on system design, code quality, and communication clarity. Pay special attention to how the candidate handles edge cases.'",
                height=120,
                key="kb_default_prompt",
                label_visibility="collapsed"
            )
            if st.button("Save Default Prompt", key="save_default_prompt"):
                if save_assessment_default_prompt(kb_name, new_prompt):
                    st.success("Default prompt saved!")
                else:
                    st.error("Failed to save prompt")

            st.markdown("---")

            c1, c2 = st.columns(2, gap="large")

            with c1:
                st.markdown("**Job Description**")
                jd = st.file_uploader("Upload JD document", ["pdf", "txt", "docx", "md"], key="jd")
                if jd:
                    save_kb_document(kb_name, jd.name, "jd", extract_text_from_file(jd))
                    st.success("Job description saved!")

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("**Evaluation Criteria**")
                crit = st.file_uploader("Upload criteria document", ["pdf", "txt", "docx", "md"], key="crit")
                if crit:
                    save_kb_document(kb_name, crit.name, "criteria", extract_text_from_file(crit))
                    st.success("Evaluation criteria saved!")

            with c2:
                st.markdown("**Technical Requirements**")
                tech = st.file_uploader("Upload requirements document", ["pdf", "txt", "docx", "md"], key="tech")
                if tech:
                    save_kb_document(kb_name, tech.name, "tech", extract_text_from_file(tech))
                    st.success("Technical requirements saved!")

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("**Other Documents**")
                other = st.file_uploader("Upload other documents", ["pdf", "txt", "docx", "md"], key="other")
                if other:
                    save_kb_document(kb_name, other.name, "other", extract_text_from_file(other))
                    st.success("Document saved!")

            st.markdown("---")
            saved_assessments = get_saved_assessments()
            if saved_assessments:
                st.markdown("### Existing Assessments")
                for a in saved_assessments:
                    prompt = get_assessment_default_prompt(a)
                    prompt_indicator = " (has default prompt)" if prompt else ""
                    st.markdown(f"- **{a}**{prompt_indicator}")

# ============== TAB 5: HISTORY (HR Only) ==============
if tab5 is not None:
    with tab5:
        results = load_results()

        if not results:
            st.info("No evaluations yet. Complete your first evaluation to see results here!")
        else:
            st.markdown('<div class="section-header">Evaluation History</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns([2, 2, 1])
            assessments = list(set(r.get("Assessment", "") for r in results if r.get("Assessment")))
            filter_assessment = c1.selectbox("Filter by Assessment", ["All"] + assessments, key="hist_assess")
            filter_rec = c2.selectbox("Filter by Recommendation", ["All", "STRONG_YES", "YES", "MAYBE", "NO"], key="hist_rec")

            filtered = [r for r in results
                       if (filter_assessment == "All" or r.get("Assessment") == filter_assessment)
                       and (filter_rec == "All" or r.get("Recommendation") == filter_rec)]

            c3.metric("Results", len(filtered))

            for r in reversed(filtered):
                rec = r.get('Recommendation', '')
                icon = "+" if rec in ["STRONG_YES", "YES"] else "~" if rec == "MAYBE" else "-"
                score = r.get('Score') or r.get('Overall Score') or '-'
                evaluated_by = r.get('Evaluated By', 'hr')
                by_label = f" [{evaluated_by.replace('_', ' ').title()}]" if evaluated_by else ""

                with st.expander(f"[{icon}] **{r.get('Candidate', 'Unknown')}** -- {r.get('Assessment', '')} -- Score: {score}{by_label}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Date:** {r.get('Timestamp', '')[:10]}")
                    c2.markdown(f"**Recommendation:** {rec}")

                    c1, c2, c3, c4, c5 = st.columns(5)
                    demo_s = r.get('Demo Score') or r.get('Demo') or '-'
                    req_s = r.get('Requirements Score') or r.get('Requirements') or '-'
                    comm_s = r.get('Communication Score') or r.get('Communication') or '-'
                    c1.metric("Demo", demo_s)
                    c2.metric("Requirements", req_s)
                    c3.metric("Communication", comm_s)

                    demo_working = r.get('Demo Working', '')
                    demo_working_text = "Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "No" if demo_working else "-"
                    c4.metric("Demo Working", demo_working_text)

                    comm_clear = r.get('Communication Clear') or r.get('Comm Clear', '')
                    comm_clear_text = "Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "No" if comm_clear else "-"
                    c5.metric("Comm Clear", comm_clear_text)

                    # Show evaluation prompt if used
                    eval_prompt = r.get('Evaluation Prompt', '')
                    if eval_prompt:
                        st.markdown(f"**Evaluation Prompt Used:** {eval_prompt[:200]}{'...' if len(eval_prompt) > 200 else ''}")

                    st.markdown("---")

                    st.markdown(f"**Summary:**")
                    st.info(r.get('Summary', 'N/A'))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Demo Description:**")
                        demo_desc = r.get('Demo Description', '')
                        if demo_desc:
                            st.markdown(demo_desc)
                        else:
                            st.markdown("_No demo description available_")

                    with col2:
                        st.markdown("**Communication Description:**")
                        comm_desc = r.get('Comm Description') or r.get('Communication Description', '')
                        if comm_desc:
                            st.markdown(comm_desc)
                        else:
                            st.markdown("_No communication description available_")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Strengths:**")
                        strengths = r.get('Strengths', '')
                        if strengths:
                            for s in str(strengths).split("|"):
                                if s.strip():
                                    st.markdown(f"- {s.strip()}")
                        else:
                            st.markdown("_No strengths recorded_")

                    with col2:
                        st.markdown("**Areas for Improvement:**")
                        improvements = r.get('Improvements', '')
                        if improvements:
                            for i in str(improvements).split("|"):
                                if i.strip():
                                    st.markdown(f"- {i.strip()}")
                        else:
                            st.markdown("_No improvements recorded_")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Requirements Met:**")
                        req_met = r.get('Requirements Met') or r.get('Met', '')
                        if req_met:
                            for req in str(req_met).split("|"):
                                if req.strip():
                                    st.markdown(f"- {req.strip()}")
                        else:
                            st.markdown("_No requirements data_")

                    with col2:
                        st.markdown("**Requirements Missing:**")
                        req_missing = r.get('Requirements Missing') or r.get('Missing', '')
                        if req_missing:
                            for req in str(req_missing).split("|"):
                                if req.strip():
                                    st.markdown(f"- {req.strip()}")
                        else:
                            st.markdown("_None - All requirements met!_")

                    st.markdown("**Key Moments:**")
                    moments_raw = r.get('Key Moments') or r.get('Moments', '')
                    if moments_raw:
                        try:
                            moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
                            if moments and isinstance(moments, list):
                                for m in moments:
                                    time_str = m.get('time', '')
                                    note = m.get('note', '')
                                    moment_type = m.get('type', 'neutral')
                                    moment_icon = "+" if moment_type == 'positive' else "-" if moment_type == 'negative' else "o"
                                    st.markdown(f"[{moment_icon}] **{time_str}** - {note}")
                            else:
                                st.markdown("_No key moments recorded_")
                        except:
                            st.markdown(f"_{moments_raw}_")
                    else:
                        st.markdown("_No key moments recorded_")

                    st.markdown("**Detailed Feedback:**")
                    detailed_feedback = r.get('Detailed Feedback') or r.get('Feedback', '')
                    if detailed_feedback:
                        st.markdown(detailed_feedback)
                    else:
                        st.markdown("_No detailed feedback available_")

                    candidate_pdf = generate_candidate_pdf(r)
                    st.download_button(
                        "Download PDF Report",
                        candidate_pdf,
                        f"{r.get('Candidate', 'Unknown').replace(' ', '_')}_report.pdf",
                        "application/pdf",
                        key=f"hist_pdf_{r.get('Timestamp', '')}_{r.get('Candidate', '')}",
                        use_container_width=True
                    )

# ============== TAB 6: HIRING MANAGER VIEW (HR Only - for testing) ==============
if tab6 is not None:
    with tab6:
        st.markdown('<div class="section-header">Hiring Manager Evaluation Interface</div>', unsafe_allow_html=True)
        st.markdown("_This tab simulates the hiring manager view. Use it to test the simplified evaluation interface._")

        st.markdown("---")

        hm_col1, hm_col2 = st.columns([1, 1], gap="large")

        with hm_col1:
            st.markdown("**Assessment & Candidate**")
            hm_saved = get_saved_assessments()
            if hm_saved:
                hm_assessment = st.selectbox("Select Assessment", hm_saved, key="hm_assessment")
            else:
                hm_assessment = st.text_input("Assessment Name", key="hm_assessment_new", placeholder="e.g., Backend Engineer")

            hm_candidate = st.text_input("Candidate Name", key="hm_candidate", placeholder="e.g., John Smith")

            # Prominent prompt area
            st.markdown("---")
            st.markdown("**Evaluation Focus (What should we look for?)**")
            hm_default_prompt = ""
            if hm_assessment:
                hm_default_prompt = get_assessment_default_prompt(hm_assessment)
            hm_prompt = st.text_area(
                "Describe what you want to evaluate in plain English",
                value=hm_default_prompt,
                placeholder="e.g., 'I want to know if this candidate can build production-ready APIs. Focus on error handling, database design, and how they explain technical decisions. Also check if they handle edge cases.'",
                height=150,
                key="hm_prompt",
                label_visibility="collapsed"
            )

            # Optional KB toggle
            hm_use_kb = st.checkbox("Also use uploaded Knowledge Base documents", value=True, key="hm_use_kb")

        with hm_col2:
            st.markdown("**Video Input**")
            hm_input_method = st.radio("Input Method", ["Loom URL", "Upload File"], horizontal=True, key="hm_input_method")

            if hm_input_method == "Loom URL":
                hm_loom_url = st.text_input("Loom Share URL", key="hm_loom_url", placeholder="https://www.loom.com/share/...")
                if hm_loom_url and st.button("Preview", key="hm_preview"):
                    match = re.search(r'loom\.com/share/([a-zA-Z0-9]+)', hm_loom_url)
                    if match:
                        video_id = match.group(1)
                        st.markdown(f'<iframe src="https://www.loom.com/embed/{video_id}" width="100%" height="300" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
            else:
                hm_video = st.file_uploader("Upload Video", type=["mp4", "webm", "mov"], key="hm_video")
                if hm_video:
                    st.video(hm_video)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Start Evaluation", type="primary", use_container_width=True, key="hm_eval"):
            if not st.session_state.api_key:
                st.error("Please enter your Gemini API key")
            elif not hm_candidate:
                st.error("Please enter the candidate's name")
            elif not hm_assessment:
                st.error("Please select an assessment")
            elif hm_input_method == "Loom URL" and not hm_loom_url:
                st.error("Please enter a Loom URL")
            elif hm_input_method == "Upload File" and not hm_video:
                st.error("Please upload a video file")
            else:
                with st.status("Processing evaluation...", expanded=True) as status:
                    try:
                        kb = load_kb_for_assessment(hm_assessment) if hm_use_kb else {"job_description": "", "evaluation_criteria": "", "technical_requirements": "", "other": ""}
                        prompt_to_use = hm_prompt or hm_default_prompt
                        tmp_path = None

                        if hm_input_method == "Loom URL":
                            st.write("Attempting to download video from Loom...")
                            tmp_path = tempfile.mktemp(suffix=".mp4")
                            download_success = download_loom_video(hm_loom_url, tmp_path)

                            if download_success:
                                st.write("Uploading to Gemini for analysis...")
                                result = evaluate_video_with_gemini(tmp_path, hm_candidate, hm_assessment, kb, "", prompt_to_use)
                            else:
                                st.write("Analyzing via Loom URL directly...")
                                result = evaluate_loom_url_directly(hm_loom_url, hm_candidate, hm_assessment, kb, "", prompt_to_use)
                                tmp_path = None
                        else:
                            tmp_path = tempfile.mktemp(suffix=".mp4")
                            with open(tmp_path, 'wb') as f:
                                f.write(hm_video.read())
                            st.write("Uploading to Gemini for analysis...")
                            result = evaluate_video_with_gemini(tmp_path, hm_candidate, hm_assessment, kb, "", prompt_to_use)

                        st.write("Saving results...")
                        save_result(result, hm_candidate, hm_assessment, prompt_to_use, st.session_state.username)

                        if tmp_path and os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                        status.update(label="Evaluation Complete!", state="complete")

                        display_evaluation_results(result)

                    except Exception as e:
                        status.update(label="Evaluation Failed", state="error")
                        st.error(f"Error: {str(e)}")

# ============== TAB 7: MANAGE USERS (HR Only) ==============
if tab7 is not None:
    with tab7:
        st.markdown('<div class="section-header">Manage Hiring Managers</div>', unsafe_allow_html=True)
        st.markdown("Add, disable, or remove hiring manager accounts. Each manager gets their own login and evaluations are tracked per person.")

        # Add new hiring manager
        st.markdown("### Add New Hiring Manager")
        with st.form("add_manager_form"):
            am_col1, am_col2 = st.columns(2)
            with am_col1:
                new_display_name = st.text_input("Full Name", placeholder="e.g., Sarah Johnson")
                new_username = st.text_input("Username", placeholder="e.g., sarah.johnson")
            with am_col2:
                new_password = st.text_input("Password", type="password")
                new_password_confirm = st.text_input("Confirm Password", type="password")

            add_submitted = st.form_submit_button("Add Hiring Manager", use_container_width=True)
            if add_submitted:
                if not new_display_name or not new_username or not new_password:
                    st.error("All fields are required")
                elif new_password != new_password_confirm:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, msg = add_hiring_manager(new_username, new_password, new_display_name)
                    if success:
                        st.success(f"Added hiring manager: {new_display_name} ({new_username})")
                        st.rerun()
                    else:
                        st.error(f"Failed: {msg}")

        # List existing hiring managers
        st.markdown("---")
        st.markdown("### Existing Hiring Managers")
        managers = list_hiring_managers()

        if not managers:
            st.info("No hiring managers added yet. Use the form above to add one.")
        else:
            for mgr in managers:
                mgr_id = mgr["id"]
                name = mgr["display_name"]
                uname = mgr["username"]
                active = mgr["active"]
                created = str(mgr.get("created_at", ""))[:10]
                status_text = "Active" if active else "Disabled"
                status_color = "#10b981" if active else "#ef4444"

                st.markdown(f"""
                <div class="manager-card">
                    <div style="width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, #059669, #10b981); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 16px;">{name[0].upper()}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 15px; font-weight: 600; color: #fafafa;">{name}</div>
                        <div style="font-size: 12px; color: #71717a;">@{uname} &bull; Added {created} &bull; <span style="color: {status_color}; font-weight: 500;">{status_text}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if active:
                        if st.button(f"Disable {uname}", key=f"disable_{mgr_id}", use_container_width=True):
                            toggle_hiring_manager(mgr_id, False)
                            st.rerun()
                    else:
                        if st.button(f"Enable {uname}", key=f"enable_{mgr_id}", use_container_width=True):
                            toggle_hiring_manager(mgr_id, True)
                            st.rerun()
                with btn_col2:
                    if st.button(f"Delete {uname}", key=f"delete_{mgr_id}", use_container_width=True):
                        delete_hiring_manager(mgr_id)
                        st.rerun()

# Footer
st.markdown("""
<div class="app-footer">
    Powered by <strong>Google Gemini AI</strong> &bull; Built with <strong>Streamlit</strong> &bull;
    <a href="https://plivo.com" target="_blank">Plivo</a>
</div>
""", unsafe_allow_html=True)
