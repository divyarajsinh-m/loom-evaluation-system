"""
Loom Evaluation System - Plivo
With Loom URL support, Batch Processing, Ranking & Reports
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
from fpdf import FPDF

# Page config - must be first
st.set_page_config(
    page_title="Loom Evaluation System | Plivo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean minimal CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #0f0f0f;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #064e3b 0%, #047857 100%);
    padding-top: 0;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
    color: #ffffff !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5 {
    color: #ffffff !important;
}

[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: rgba(255,255,255,0.8) !important; }
[data-testid="stSidebar"] input { background: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.3) !important; color: #ffffff !important; }
[data-testid="stSidebar"] .stDownloadButton button { background: rgba(255,255,255,0.15) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.3) !important; }

.main .block-container { padding: 2rem 3rem; max-width: 1200px; }

.main h1 { color: #ffffff !important; font-weight: 700 !important; font-size: 2rem !important; }
.main h2 { color: #f1f5f9 !important; font-weight: 600 !important; font-size: 1.5rem !important; }
.main h3 { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 1.25rem !important; }
.main p, .main span, .main label, .main li { color: #cbd5e1 !important; }

.eval-card { background: #1a1a1a; border-radius: 16px; padding: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); border: 1px solid #2a2a2a; margin-bottom: 20px; }

.score-card { background: #1a1a1a; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border: 1px solid #2a2a2a; }
.score-value { font-size: 42px; font-weight: 700; line-height: 1; margin-bottom: 8px; }
.score-label { font-size: 13px; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.score-green { color: #059669; }
.score-yellow { color: #d97706; }
.score-red { color: #dc2626; }

.rank-card { background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); border-radius: 16px; padding: 20px; margin: 10px 0; border-left: 4px solid #059669; }
.rank-1 { border-left-color: #fbbf24; background: linear-gradient(135deg, #1a1a1a 0%, #2d2a1a 100%); }
.rank-2 { border-left-color: #9ca3af; background: linear-gradient(135deg, #1a1a1a 0%, #252525 100%); }
.rank-3 { border-left-color: #b45309; background: linear-gradient(135deg, #1a1a1a 0%, #2a2520 100%); }

.stTabs [data-baseweb="tab-list"] { background: #1a1a1a; border-radius: 12px; padding: 6px; gap: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); border: 1px solid #2a2a2a; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #94a3b8 !important; font-weight: 500; padding: 12px 24px; }
.stTabs [aria-selected="true"] { background: #059669 !important; color: #ffffff !important; }

.stButton > button { background: #059669 !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; padding: 12px 28px !important; font-size: 15px !important; transition: all 0.15s ease !important; }
.stButton > button:hover { background: #047857 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important; }

.stTextInput input, .stTextArea textarea { background: #1a1a1a !important; border: 2px solid #2a2a2a !important; border-radius: 10px !important; color: #ffffff !important; font-size: 15px !important; padding: 12px 16px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #059669 !important; box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.25) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 14px !important; margin-bottom: 6px !important; }

.stSelectbox > div > div { background: #1a1a1a !important; border: 2px solid #2a2a2a !important; border-radius: 10px !important; color: #ffffff !important; }

[data-testid="stFileUploader"] { background: #1a1a1a; border: 2px dashed #3a3a3a; border-radius: 12px; padding: 24px; }
[data-testid="stFileUploader"]:hover { border-color: #059669; background: #0a2018; }

.stRadio > div { background: #1a1a1a; border-radius: 10px; padding: 8px 12px; border: 1px solid #2a2a2a; }
.stRadio label { color: #e2e8f0 !important; }

.stSuccess { background: #052e16 !important; border-left: 4px solid #059669 !important; color: #86efac !important; }
.stInfo { background: #1e3a5f !important; border-left: 4px solid #3b82f6 !important; color: #93c5fd !important; }
.stWarning { background: #422006 !important; border-left: 4px solid #f59e0b !important; color: #fcd34d !important; }
.stError { background: #450a0a !important; border-left: 4px solid #ef4444 !important; color: #fca5a5 !important; }

.streamlit-expanderHeader { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; border-radius: 10px !important; font-weight: 500 !important; color: #e2e8f0 !important; }

[data-testid="stMetricValue"] { color: #ffffff !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }

.app-header { background: #1a1a1a; padding: 20px 28px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); border: 1px solid #2a2a2a; display: flex; align-items: center; gap: 16px; }
.app-title { font-size: 24px; font-weight: 700; color: #ffffff; margin: 0; }
.app-subtitle { font-size: 14px; color: #94a3b8; margin: 4px 0 0 0; }
.plivo-badge { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }

.section-header { font-size: 14px; font-weight: 700; color: #10b981; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #10b981; }

.app-footer { text-align: center; padding: 24px; color: #64748b; font-size: 13px; border-top: 1px solid #2a2a2a; margin-top: 40px; }
.app-footer a { color: #10b981; text-decoration: none; font-weight: 500; }

video { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# Constants
RESULTS_FILE = "evaluation_results.csv"
KB_DIR = "knowledge_base"
BATCH_DIR = "batch_videos"

os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(BATCH_DIR, exist_ok=True)


def download_loom_video(loom_url: str, output_path: str) -> bool:
    """Download video from Loom URL using yt-dlp"""
    try:
        # Clean the URL
        loom_url = loom_url.strip()
        if not loom_url:
            return False

        # Try different yt-dlp paths
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

        # Use yt-dlp to download
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


def evaluate_loom_url_directly(loom_url: str, candidate_name: str, assessment_name: str, knowledge_base: dict, additional_notes: str):
    """Evaluate Loom video directly from URL without downloading (using Gemini's web capabilities)"""
    client = genai.Client(api_key=st.session_state.api_key)

    # Extract video ID for embed
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

    prompt = f"""I need you to evaluate a candidate's Loom demo video.

The Loom video URL is: {loom_url}
Loom Video ID: {video_id}

**Assessment Type:** {assessment_name}
**Candidate:** {candidate_name}
{kb_context}
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
        model="models/gemini-2.5-flash",
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
        # Extract folder ID from URL
        # Formats:
        # https://drive.google.com/drive/folders/FOLDER_ID
        # https://drive.google.com/drive/u/0/folders/FOLDER_ID
        match = re.search(r'folders/([a-zA-Z0-9_-]+)', folder_url)
        if not match:
            return []

        folder_id = match.group(1)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Download entire folder using gdown
        gdown.download_folder(
            id=folder_id,
            output=output_dir,
            quiet=False,
            use_cookies=False
        )

        # Find all video files downloaded
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
        # Extract file ID from URL
        # Formats:
        # https://drive.google.com/file/d/FILE_ID/view
        # https://drive.google.com/open?id=FILE_ID
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


def save_kb_document(assessment_name: str, doc_name: str, doc_type: str, content: str):
    assessment_dir = os.path.join(KB_DIR, assessment_name.replace(" ", "_"))
    os.makedirs(assessment_dir, exist_ok=True)
    with open(os.path.join(assessment_dir, f"{doc_type}_{doc_name}.txt"), 'w') as f:
        f.write(content)


def load_kb_for_assessment(assessment_name: str) -> dict:
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


def get_saved_assessments() -> list:
    if not os.path.exists(KB_DIR):
        return []
    return [d.replace("_", " ") for d in os.listdir(KB_DIR) if os.path.isdir(os.path.join(KB_DIR, d))]


def evaluate_video_with_gemini(video_path, candidate_name, assessment_name, knowledge_base, additional_notes):
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

    prompt = f"""Evaluate this candidate's Loom demo video thoroughly.

**Assessment Type:** {assessment_name}
**Candidate:** {candidate_name}
{kb_context}
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
        model="models/gemini-2.5-flash",
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


def save_result(result, candidate_name, assessment_name):
    exists = os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Timestamp", "Candidate", "Assessment", "Score", "Demo", "Requirements",
                           "Communication", "Recommendation", "Summary", "Strengths", "Improvements",
                           "Met", "Missing", "Demo Working", "Demo Description", "Comm Clear",
                           "Comm Description", "Moments", "Feedback"])
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
            result.get("detailed_feedback")
        ])


def load_results():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, 'r') as f:
        return list(csv.DictReader(f))


def get_rankings(assessment_filter="All"):
    """Get candidates ranked by score for an assessment"""
    results = load_results()
    if assessment_filter != "All":
        results = [r for r in results if r.get("Assessment") == assessment_filter]

    # Sort by score descending
    ranked = sorted(results, key=lambda x: int(x.get("Score") or x.get("Overall Score") or 0), reverse=True)
    return ranked


def generate_assessment_pdf(assessment_name: str, results: list) -> bytes:
    """Generate PDF report for an assessment with all candidates"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

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
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, f'Average Score: {avg_score:.1f}', ln=True)
        pdf.ln(5)

    # Rankings table header
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(12, 8, 'Rank', border=1)
    pdf.cell(45, 8, 'Candidate', border=1)
    pdf.cell(20, 8, 'Score', border=1)
    pdf.cell(30, 8, 'Recommend', border=1)
    pdf.cell(83, 8, 'Summary', border=1)
    pdf.ln()

    pdf.set_font('Helvetica', '', 8)
    for idx, r in enumerate(results[:20], 1):  # Limit to 20 for table
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
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Detailed Candidate Reports', ln=True)
    pdf.ln(5)

    for idx, r in enumerate(results, 1):
        # Check if need new page
        if pdf.get_y() > 240:
            pdf.add_page()

        pdf.set_font('Helvetica', 'B', 11)
        candidate_name = str(r.get("Candidate", "Unknown"))
        pdf.cell(0, 7, f'{idx}. {candidate_name}', ln=True)

        pdf.set_font('Helvetica', '', 9)
        score_val = r.get("Score") or r.get("Overall Score") or "-"
        rec_val = r.get("Recommendation", "-")
        pdf.cell(0, 5, f'Score: {score_val} | Recommendation: {rec_val}', ln=True)

        demo_val = r.get("Demo Score") or r.get("Demo") or "-"
        req_val = r.get("Requirements Score") or r.get("Requirements") or "-"
        comm_val = r.get("Communication Score") or r.get("Communication") or "-"
        pdf.cell(0, 5, f'Demo: {demo_val} | Requirements: {req_val} | Communication: {comm_val}', ln=True)

        # Summary
        summary_text = str(r.get("Summary", "No summary") or "No summary")[:500]
        pdf.set_font('Helvetica', 'I', 8)
        pdf.multi_cell(190, 4, f'Summary: {summary_text}')

        # Strengths
        strengths = r.get("Strengths", "")
        if strengths:
            strengths_text = str(strengths).replace("|", ", ")[:300]
            pdf.set_font('Helvetica', '', 8)
            pdf.multi_cell(190, 4, f'Strengths: {strengths_text}')

        # Improvements
        improvements = r.get("Improvements", "")
        if improvements:
            improvements_text = str(improvements).replace("|", ", ")[:300]
            pdf.multi_cell(190, 4, f'Improvements: {improvements_text}')

        pdf.ln(4)

    return bytes(pdf.output())


def generate_candidate_pdf(result: dict) -> bytes:
    """Generate PDF report for a single candidate"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # Header
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Candidate Evaluation Report', ln=True, align='C')
    pdf.ln(5)

    # Candidate info
    candidate_name = str(result.get("Candidate", "Unknown"))
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, f'Candidate: {candidate_name}', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f'Assessment: {result.get("Assessment", "-")}', ln=True)
    timestamp = str(result.get("Timestamp", ""))[:10] if result.get("Timestamp") else "-"
    pdf.cell(0, 6, f'Date: {timestamp}', ln=True)
    pdf.ln(8)

    # Scores box
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, 'SCORES', ln=True)
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
        demo_desc_text = str(demo_desc)[:1500]
        pdf.multi_cell(190, 5, demo_desc_text)
        pdf.ln(5)

    # Communication Description
    comm_desc = result.get("Comm Description") or result.get("Communication Description", "")
    if comm_desc:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'COMMUNICATION DESCRIPTION', ln=True)
        pdf.set_font('Helvetica', '', 9)
        comm_desc_text = str(comm_desc)[:1500]
        pdf.multi_cell(190, 5, comm_desc_text)
        pdf.ln(5)

    # Strengths
    strengths = result.get("Strengths", "")
    if strengths:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'STRENGTHS', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for s in str(strengths).split("|"):
            if s.strip():
                pdf.cell(0, 5, f'  - {s.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Improvements
    improvements = result.get("Improvements", "")
    if improvements:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'AREAS FOR IMPROVEMENT', ln=True)
        pdf.set_font('Helvetica', '', 9)
        for i in str(improvements).split("|"):
            if i.strip():
                pdf.cell(0, 5, f'  - {i.strip()[:100]}', ln=True)
        pdf.ln(5)

    # Detailed feedback
    feedback = result.get("Detailed Feedback") or result.get("Feedback") or ""
    if feedback:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, 'DETAILED FEEDBACK', ln=True)
        pdf.set_font('Helvetica', '', 9)
        feedback_text = str(feedback)[:2000]
        pdf.multi_cell(190, 5, feedback_text)

    return bytes(pdf.output())


def generate_assessment_csv(results: list) -> str:
    """Generate CSV for assessment results"""
    output = io.StringIO()
    if results:
        fieldnames = ["Rank", "Candidate", "Overall Score", "Demo Score", "Requirements Score", "Communication Score",
                     "Recommendation", "Demo Working", "Demo Description", "Communication Clear", "Communication Description",
                     "Summary", "Strengths", "Improvements", "Requirements Met", "Requirements Missing", "Detailed Feedback"]
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
                "Detailed Feedback": r.get("Detailed Feedback") or r.get("Feedback") or ""
            })
    return output.getvalue()


# Initialize session state
if 'api_key' not in st.session_state:
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
        Loom Evaluation System
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password",
                           help="Enter your Google Gemini API key")
    if api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown("##### 📊 Statistics")

    col1, col2 = st.columns(2)
    col1.metric("Evaluations", len(load_results()))
    col2.metric("Assessments", len(get_saved_assessments()))

    if os.path.exists(RESULTS_FILE):
        st.markdown("---")
        with open(RESULTS_FILE, 'r') as f:
            st.download_button("📥 Export All Results", f.read(), "evaluations.csv", "text/csv",
                             use_container_width=True)

# ============== MAIN CONTENT ==============

# Header
st.markdown("""
<div class="app-header">
    <div style="flex: 1;">
        <h1 class="app-title">🎯 Loom Evaluation System</h1>
        <p class="app-subtitle">AI-powered technical demo evaluation for hiring</p>
    </div>
    <div class="plivo-badge">PLIVO</div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📹 Single Evaluation", "📦 Batch Processing", "🏆 Rankings", "📚 Knowledge Base", "📊 History"])

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
                            height=100)

        if assessment_name:
            kb = load_kb_for_assessment(assessment_name)
            if any(kb.values()):
                st.success(f"✅ Knowledge base loaded for **{assessment_name}**")
            else:
                st.info("💡 No evaluation criteria uploaded. Add documents in the Knowledge Base tab.")

    with col2:
        st.markdown('<div class="section-header">Video Input</div>', unsafe_allow_html=True)

        input_method = st.radio("Input Method", ["🔗 Loom URL", "📁 Upload File"], horizontal=True)

        video_path = None

        if input_method == "🔗 Loom URL":
            loom_url = st.text_input("Loom Share URL", placeholder="https://www.loom.com/share/...")
            if loom_url and st.button("🔍 Preview Video"):
                # Extract video ID and show embed
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

    # Evaluate button
    if st.button("🚀 Start Evaluation", type="primary", use_container_width=True, key="single_eval"):
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Gemini API key in the sidebar")
        elif not candidate_name:
            st.error("⚠️ Please enter the candidate's name")
        elif not assessment_name:
            st.error("⚠️ Please enter or select an assessment")
        elif input_method == "🔗 Loom URL" and not loom_url:
            st.error("⚠️ Please enter a Loom URL")
        elif input_method == "📁 Upload File" and not video:
            st.error("⚠️ Please upload a video file")
        else:
            with st.status("🔄 Processing...", expanded=True) as status:
                try:
                    kb = load_kb_for_assessment(assessment_name)
                    tmp_path = None

                    if input_method == "🔗 Loom URL":
                        st.write("📥 Attempting to download video from Loom...")
                        tmp_path = tempfile.mktemp(suffix=".mp4")
                        download_success = download_loom_video(loom_url, tmp_path)

                        if download_success:
                            st.write("📤 Uploading to Gemini for analysis...")
                            result = evaluate_video_with_gemini(tmp_path, candidate_name, assessment_name, kb, notes)
                        else:
                            st.write("⚠️ Download not available, analyzing via Loom URL directly...")
                            st.write("🔍 Gemini is analyzing the Loom recording...")
                            result = evaluate_loom_url_directly(loom_url, candidate_name, assessment_name, kb, notes)
                            tmp_path = None  # No file to delete
                    else:
                        tmp_path = tempfile.mktemp(suffix=".mp4")
                        with open(tmp_path, 'wb') as f:
                            f.write(video.read())
                        st.write("📤 Uploading to Gemini for analysis...")
                        result = evaluate_video_with_gemini(tmp_path, candidate_name, assessment_name, kb, notes)

                    st.write("💾 Saving results...")
                    save_result(result, candidate_name, assessment_name)

                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    status.update(label="✅ Evaluation Complete!", state="complete")

                    # Display results
                    st.markdown("---")
                    st.markdown("## 📋 Evaluation Results")

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
                    c1.metric("🎬 Demo Score", f"{result.get('demo_score') or '-'}/100")
                    c2.metric("📋 Requirements", f"{result.get('requirements_score') or '-'}/100")
                    c3.metric("🗣️ Communication", f"{result.get('communication_score') or '-'}/100")

                    st.markdown("### 📝 Summary")
                    st.info(result.get("summary", "No summary available"))

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### 💪 Strengths")
                        for s in result.get("strengths", []):
                            st.markdown(f"✅ {s}")
                    with c2:
                        st.markdown("### 📈 Areas for Improvement")
                        for i in result.get("improvements", []):
                            st.markdown(f"🔸 {i}")

                except Exception as e:
                    status.update(label="❌ Evaluation Failed", state="error")
                    st.error(f"Error: {str(e)}")

# ============== TAB 2: BATCH PROCESSING ==============
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
            st.write(f"• {candidate}")

    if st.button("🚀 Start Batch Evaluation", type="primary", use_container_width=True, key="batch_eval"):
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Gemini API key")
        elif not batch_assessment or batch_assessment == "No assessments - create one first":
            st.error("⚠️ Please select or create an assessment first")
        elif not batch_videos:
            st.error("⚠️ Please upload video files")
        else:
            kb = load_kb_for_assessment(batch_assessment)
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

                            result = evaluate_video_with_gemini(tmp_path, item["candidate"], batch_assessment, kb, "")
                            save_result(result, item["candidate"], batch_assessment)

                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)

                            score = result.get("score", 0)
                            rec = result.get("recommendation", "MAYBE")
                            status.update(label=f"✅ {item['candidate']}: Score {score}, {rec}", state="complete")

                        except Exception as e:
                            status.update(label=f"❌ {item['candidate']}: Failed - {str(e)}", state="error")

                    progress.progress((idx + 1) / len(batch_items))

                st.success(f"✅ Batch processing complete! Check the Rankings tab to see results.")

# ============== TAB 3: RANKINGS ==============
with tab3:
    st.markdown('<div class="section-header">Candidate Rankings</div>', unsafe_allow_html=True)

    assessments = list(set(r.get("Assessment", "") for r in load_results() if r.get("Assessment")))
    rank_assessment = st.selectbox("Filter by Assessment", ["All"] + assessments, key="rank_filter")

    ranked = get_rankings(rank_assessment)

    if not ranked:
        st.info("📭 No evaluations yet. Complete some evaluations to see rankings!")
    else:
        # Export buttons
        st.markdown(f"### 🏆 Top Candidates ({len(ranked)} total)")

        c1, c2, c3 = st.columns([2, 1, 1])
        with c2:
            # PDF Export
            pdf_data = generate_assessment_pdf(rank_assessment, ranked)
            st.download_button(
                "📄 Export PDF",
                pdf_data,
                f"assessment_report_{rank_assessment.replace(' ', '_')}.pdf",
                "application/pdf",
                use_container_width=True
            )
        with c3:
            # CSV Export
            csv_data = generate_assessment_csv(ranked)
            st.download_button(
                "📊 Export CSV",
                csv_data,
                f"assessment_results_{rank_assessment.replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        for idx, r in enumerate(ranked[:20], 1):  # Show top 20
            score = r.get('Score') or r.get('Overall Score') or 0
            rec = r.get('Recommendation', '')
            candidate = r.get('Candidate', 'Unknown')
            assessment = r.get('Assessment', '')

            # Determine rank class
            rank_class = f"rank-{idx}" if idx <= 3 else ""

            # Medal for top 3
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"

            # Recommendation color
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
                # Scores row
                c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
                c1.metric("Demo", r.get('Demo Score') or r.get('Demo') or '-')
                c2.metric("Requirements", r.get('Requirements Score') or r.get('Requirements') or '-')
                c3.metric("Communication", r.get('Communication Score') or r.get('Communication') or '-')

                # Demo Working & Communication Clear
                demo_working = r.get('Demo Working', '')
                demo_working_text = "✅ Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "❌ No" if demo_working else "-"
                c4.metric("Demo Working", demo_working_text)

                comm_clear = r.get('Communication Clear') or r.get('Comm Clear', '')
                comm_clear_text = "✅ Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "❌ No" if comm_clear else "-"
                c5.metric("Comm Clear", comm_clear_text)

                # PDF Download
                candidate_pdf = generate_candidate_pdf(r)
                st.download_button(
                    "📄 Download PDF Report",
                    candidate_pdf,
                    f"{candidate.replace(' ', '_')}_report.pdf",
                    "application/pdf",
                    key=f"pdf_{idx}_{candidate}",
                    use_container_width=True
                )

                st.markdown("---")

                # Summary
                st.markdown(f"**📝 Summary:**")
                st.info(r.get('Summary', 'N/A'))

                # Demo and Communication Descriptions
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🎬 Demo Description:**")
                    demo_desc = r.get('Demo Description', '')
                    if demo_desc:
                        st.markdown(demo_desc)
                    else:
                        st.markdown("_No demo description available_")

                with col2:
                    st.markdown("**🗣️ Communication Description:**")
                    comm_desc = r.get('Comm Description') or r.get('Communication Description', '')
                    if comm_desc:
                        st.markdown(comm_desc)
                    else:
                        st.markdown("_No communication description available_")

                # Strengths and Improvements side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**💪 Strengths:**")
                    strengths = r.get('Strengths', '')
                    if strengths:
                        for s in str(strengths).split("|"):
                            if s.strip():
                                st.markdown(f"✅ {s.strip()}")
                    else:
                        st.markdown("_No strengths recorded_")

                with col2:
                    st.markdown("**📈 Areas for Improvement:**")
                    improvements = r.get('Improvements', '')
                    if improvements:
                        for i in str(improvements).split("|"):
                            if i.strip():
                                st.markdown(f"🔸 {i.strip()}")
                    else:
                        st.markdown("_No improvements recorded_")

                # Requirements Met and Missing
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Requirements Met:**")
                    req_met = r.get('Requirements Met') or r.get('Met', '')
                    if req_met:
                        for req in str(req_met).split("|"):
                            if req.strip():
                                st.markdown(f"• {req.strip()}")
                    else:
                        st.markdown("_No requirements data_")

                with col2:
                    st.markdown("**❌ Requirements Missing:**")
                    req_missing = r.get('Requirements Missing') or r.get('Missing', '')
                    if req_missing:
                        for req in str(req_missing).split("|"):
                            if req.strip():
                                st.markdown(f"• {req.strip()}")
                    else:
                        st.markdown("_None - All requirements met!_")

                # Key Moments
                st.markdown("**⏱️ Key Moments:**")
                moments_raw = r.get('Key Moments') or r.get('Moments', '')
                if moments_raw:
                    try:
                        moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
                        if moments and isinstance(moments, list):
                            for m in moments:
                                time_str = m.get('time', '')
                                note = m.get('note', '')
                                moment_type = m.get('type', 'neutral')
                                icon = "🟢" if moment_type == 'positive' else "🔴" if moment_type == 'negative' else "⚪"
                                st.markdown(f"{icon} **{time_str}** - {note}")
                        else:
                            st.markdown("_No key moments recorded_")
                    except:
                        st.markdown(f"_{moments_raw}_")
                else:
                    st.markdown("_No key moments recorded_")

                # Detailed Feedback
                st.markdown("**📋 Detailed Feedback:**")
                detailed_feedback = r.get('Detailed Feedback') or r.get('Feedback', '')
                if detailed_feedback:
                    st.markdown(detailed_feedback)
                else:
                    st.markdown("_No detailed feedback available_")

# ============== TAB 4: KNOWLEDGE BASE ==============
with tab4:
    st.markdown('<div class="section-header">Knowledge Base Management</div>', unsafe_allow_html=True)
    st.markdown("Upload evaluation criteria, job descriptions, and requirements for each assessment type.")

    kb_name = st.text_input("Assessment Name", key="kb_assessment", placeholder="e.g., Backend Engineer Q1 2024")

    if kb_name:
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown("**📄 Job Description**")
            jd = st.file_uploader("Upload JD document", ["pdf", "txt", "docx", "md"], key="jd")
            if jd:
                save_kb_document(kb_name, jd.name, "jd", extract_text_from_file(jd))
                st.success("✅ Job description saved!")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**📋 Evaluation Criteria**")
            crit = st.file_uploader("Upload criteria document", ["pdf", "txt", "docx", "md"], key="crit")
            if crit:
                save_kb_document(kb_name, crit.name, "criteria", extract_text_from_file(crit))
                st.success("✅ Evaluation criteria saved!")

        with c2:
            st.markdown("**⚙️ Technical Requirements**")
            tech = st.file_uploader("Upload requirements document", ["pdf", "txt", "docx", "md"], key="tech")
            if tech:
                save_kb_document(kb_name, tech.name, "tech", extract_text_from_file(tech))
                st.success("✅ Technical requirements saved!")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**📎 Other Documents**")
            other = st.file_uploader("Upload other documents", ["pdf", "txt", "docx", "md"], key="other")
            if other:
                save_kb_document(kb_name, other.name, "other", extract_text_from_file(other))
                st.success("✅ Document saved!")

        st.markdown("---")
        saved_assessments = get_saved_assessments()
        if saved_assessments:
            st.markdown("### 📁 Existing Assessments")
            for a in saved_assessments:
                st.markdown(f"• **{a}**")

# ============== TAB 5: HISTORY ==============
with tab5:
    results = load_results()

    if not results:
        st.info("📭 No evaluations yet. Complete your first evaluation to see results here!")
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
            icon = "🟢" if rec in ["STRONG_YES", "YES"] else "🟡" if rec == "MAYBE" else "🔴"
            score = r.get('Score') or r.get('Overall Score') or '-'

            with st.expander(f"{icon} **{r.get('Candidate', 'Unknown')}** — {r.get('Assessment', '')} — Score: {score}"):
                # Date and recommendation row
                c1, c2 = st.columns(2)
                c1.markdown(f"**📅 Date:** {r.get('Timestamp', '')[:10]}")
                c2.markdown(f"**🎯 Recommendation:** {rec}")

                # Scores row
                c1, c2, c3, c4, c5 = st.columns(5)
                demo_s = r.get('Demo Score') or r.get('Demo') or '-'
                req_s = r.get('Requirements Score') or r.get('Requirements') or '-'
                comm_s = r.get('Communication Score') or r.get('Communication') or '-'
                c1.metric("Demo", demo_s)
                c2.metric("Requirements", req_s)
                c3.metric("Communication", comm_s)

                # Demo Working & Communication Clear
                demo_working = r.get('Demo Working', '')
                demo_working_text = "✅ Yes" if str(demo_working).lower() in ['true', 'yes', '1'] else "❌ No" if demo_working else "-"
                c4.metric("Demo Working", demo_working_text)

                comm_clear = r.get('Communication Clear') or r.get('Comm Clear', '')
                comm_clear_text = "✅ Yes" if str(comm_clear).lower() in ['true', 'yes', '1'] else "❌ No" if comm_clear else "-"
                c5.metric("Comm Clear", comm_clear_text)

                st.markdown("---")

                # Summary
                st.markdown(f"**📝 Summary:**")
                st.info(r.get('Summary', 'N/A'))

                # Demo and Communication Descriptions
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🎬 Demo Description:**")
                    demo_desc = r.get('Demo Description', '')
                    if demo_desc:
                        st.markdown(demo_desc)
                    else:
                        st.markdown("_No demo description available_")

                with col2:
                    st.markdown("**🗣️ Communication Description:**")
                    comm_desc = r.get('Comm Description') or r.get('Communication Description', '')
                    if comm_desc:
                        st.markdown(comm_desc)
                    else:
                        st.markdown("_No communication description available_")

                # Strengths and Improvements
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**💪 Strengths:**")
                    strengths = r.get('Strengths', '')
                    if strengths:
                        for s in str(strengths).split("|"):
                            if s.strip():
                                st.markdown(f"✅ {s.strip()}")
                    else:
                        st.markdown("_No strengths recorded_")

                with col2:
                    st.markdown("**📈 Areas for Improvement:**")
                    improvements = r.get('Improvements', '')
                    if improvements:
                        for i in str(improvements).split("|"):
                            if i.strip():
                                st.markdown(f"🔸 {i.strip()}")
                    else:
                        st.markdown("_No improvements recorded_")

                # Requirements Met and Missing
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Requirements Met:**")
                    req_met = r.get('Requirements Met') or r.get('Met', '')
                    if req_met:
                        for req in str(req_met).split("|"):
                            if req.strip():
                                st.markdown(f"• {req.strip()}")
                    else:
                        st.markdown("_No requirements data_")

                with col2:
                    st.markdown("**❌ Requirements Missing:**")
                    req_missing = r.get('Requirements Missing') or r.get('Missing', '')
                    if req_missing:
                        for req in str(req_missing).split("|"):
                            if req.strip():
                                st.markdown(f"• {req.strip()}")
                    else:
                        st.markdown("_None - All requirements met!_")

                # Key Moments
                st.markdown("**⏱️ Key Moments:**")
                moments_raw = r.get('Key Moments') or r.get('Moments', '')
                if moments_raw:
                    try:
                        moments = json.loads(moments_raw) if isinstance(moments_raw, str) else moments_raw
                        if moments and isinstance(moments, list):
                            for m in moments:
                                time_str = m.get('time', '')
                                note = m.get('note', '')
                                moment_type = m.get('type', 'neutral')
                                moment_icon = "🟢" if moment_type == 'positive' else "🔴" if moment_type == 'negative' else "⚪"
                                st.markdown(f"{moment_icon} **{time_str}** - {note}")
                        else:
                            st.markdown("_No key moments recorded_")
                    except:
                        st.markdown(f"_{moments_raw}_")
                else:
                    st.markdown("_No key moments recorded_")

                # Detailed Feedback
                st.markdown("**📋 Detailed Feedback:**")
                detailed_feedback = r.get('Detailed Feedback') or r.get('Feedback', '')
                if detailed_feedback:
                    st.markdown(detailed_feedback)
                else:
                    st.markdown("_No detailed feedback available_")

                # Download PDF button
                candidate_pdf = generate_candidate_pdf(r)
                st.download_button(
                    "📄 Download PDF Report",
                    candidate_pdf,
                    f"{r.get('Candidate', 'Unknown').replace(' ', '_')}_report.pdf",
                    "application/pdf",
                    key=f"hist_pdf_{r.get('Timestamp', '')}_{r.get('Candidate', '')}",
                    use_container_width=True
                )

# Footer
st.markdown("""
<div class="app-footer">
    Powered by <strong>Google Gemini AI</strong> • Built with <strong>Streamlit</strong> •
    <a href="https://plivo.com" target="_blank">Plivo</a>
</div>
""", unsafe_allow_html=True)
