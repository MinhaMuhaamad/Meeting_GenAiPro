import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from datetime import datetime
import json
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Smart Meeting Minutes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling - Black and Purple Theme with Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    html, body {
        background: #0a0a0a;
        color: #e0d5ff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #16213e 100%);
    }
    
    .main {
        padding: 0 !important;
    }
    
    .main > div {
        padding: 2rem !important;
    }
    
    section[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #16213e 100%);
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Main heading animation */
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    h1 {
        background: linear-gradient(135deg, #6F00FF, #E9B3FB, #6F00FF);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        animation: slideInDown 0.8s ease-out, gradientShift 3s ease-in-out infinite !important;
    }
    
    h2 {
        color: #e9b3fb !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        animation: fadeInUp 0.6s ease-out !important;
    }
    
    h3 {
        color: #b088ff !important;
        font-weight: 600 !important;
    }
    
    h4 {
        color: #d4a5ff !important;
        font-weight: 600 !important;
    }
    
    p, label, span {
        color: #e0d5ff !important;
    }
    
    .subtitle {
        text-align: center;
        color: #b088ff !important;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out 0.2s both !important;
    }
    
    /* Header section with image */
    .header-section {
        position: relative;
        height: 300px;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(111, 0, 255, 0.2);
        animation: fadeInUp 0.6s ease-out !important;
    }
    
    .header-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.7) contrast(1.1);
    }
    
    .header-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(111, 0, 255, 0.3), rgba(59, 2, 112, 0.5));
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .header-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: white !important;
        text-align: center;
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        animation: slideInDown 0.8s ease-out !important;
    }
    
    .header-subtitle {
        font-size: 1rem !important;
        color: #e9b3fb !important;
        text-align: center;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        margin-top: 0.5rem;
        animation: fadeInUp 0.8s ease-out 0.2s both !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6F00FF, #3B0270) !important;
        color: white !important;
        border: 2px solid #6F00FF !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 25px rgba(111, 0, 255, 0.5) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 35px rgba(111, 0, 255, 0.7) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(15, 15, 35, 0.6) !important;
        border: 2px solid rgba(111, 0, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #e0d5ff !important;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(15, 15, 35, 0.6) !important;
        border: 2px solid rgba(111, 0, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #e0d5ff !important;
        font-family: 'Monaco', monospace !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(26, 10, 46, 0.6) !important;
        border-radius: 12px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #9d88b8 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6F00FF, #3B0270) !important;
        color: white !important;
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(15, 200, 100, 0.15), rgba(15, 180, 80, 0.1)) !important;
        border-left: 4px solid #20c65e !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #90ee90 !important;
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(111, 0, 255, 0.15), rgba(59, 2, 112, 0.1)) !important;
        border-left: 4px solid #6F00FF !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #d4a5ff !important;
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.1)) !important;
        border-left: 4px solid #FFB74D !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #ffcc80 !important;
    }
    
    a {
        color: #6F00FF !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #e9b3fb !important;
    }
    </style>
""", unsafe_allow_html=True)

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY", "")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

# Verify API keys are configured
if not openai_api_key or not gemini_api_key:
    st.error("⚠️ Missing API Keys! Please configure OPENAI_API_KEY and GEMINI_API_KEY environment variables.")
    st.stop()

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ''
if 'minutes' not in st.session_state:
    st.session_state.minutes = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Main Header
st.markdown("<h1>📝 Smart Meeting Minutes</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your meeting recordings into actionable insights with AI</p>", unsafe_allow_html=True)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎤 Upload Audio", "✍️ Paste Transcript", "📊 Results"])

with tab1:
    # Header with background image
    st.markdown("""
        <div class='header-section'>
            <img src='https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&h=400&fit=crop' class='header-image' alt='Audio Recording'>
            <div class='header-overlay'>
                <div class='header-title'>🎤 Upload Meeting Recording</div>
                <div class='header-subtitle'>Convert your audio files into transcriptions instantly</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        audio_file = st.file_uploader(
            "Drop your audio file here",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'webm'],
            help="Supported: MP3, WAV, M4A, OGG, FLAC, WebM"
        )
        
        if audio_file:
            file_size_mb = audio_file.size / (1024 * 1024)
            st.markdown(f"""
                <div class='success-card'>
                    <strong>✅ File Uploaded Successfully</strong><br/>
                    📁 {audio_file.name} | 💾 {file_size_mb:.2f} MB
                </div>
            """, unsafe_allow_html=True)
            
            st.audio(audio_file)
            
            if st.button("🚀 Transcribe Audio with AI", key="transcribe_btn", use_container_width=True):
                with st.spinner("🎯 Transcribing audio... Please wait..."):
                    try:
                        client = OpenAI(api_key=openai_api_key)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                            tmp_file.write(audio_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        with open(tmp_file_path, "rb") as audio_data:
                            transcript_response = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_data,
                                response_format="text"
                            )
                        
                        os.unlink(tmp_file_path)
                        st.session_state.transcript = transcript_response
                        st.markdown('<div class="success-card"><strong>✅ Transcription completed!</strong></div>', unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f'<div class="warning-card"><strong>❌ Transcription failed: {str(e)[:100]}</strong></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='info-card'>
                <strong>💡 Tips</strong><br/><br/>
                ✓ Clear audio quality<br/>
                ✓ Low background noise<br/>
                ✓ Max: 25 MB<br/>
                ✓ MP3, WAV, M4A
            </div>
        """, unsafe_allow_html=True)

with tab2:
    # Header with background image
    st.markdown("""
        <div class='header-section'>
            <img src='https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=1200&h=400&fit=crop' class='header-image' alt='Transcript'>
            <div class='header-overlay'>
                <div class='header-title'>✍️ Paste Meeting Transcript</div>
                <div class='header-subtitle'>Enter your meeting transcript and generate AI-powered minutes</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        transcript_input = st.text_area(
            "Paste your meeting transcript here:",
            value=st.session_state.transcript,
            height=400,
            placeholder="Enter or paste your meeting transcript here..."
        )
    
    with col2:
        if st.button("💾 Save Transcript", key="save_transcript", use_container_width=True):
            if transcript_input.strip():
                st.session_state.transcript = transcript_input
                st.markdown('<div class="success-card"><strong>✅ Saved!</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-card"><strong>⚠️ Enter text first</strong></div>', unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        if st.button("🧪 Load Demo", key="demo_btn", use_container_width=True):
            st.session_state.transcript = """Welcome everyone to today's product planning meeting.

John: Thanks for joining. Today we discuss Q1 roadmap, customer feature requests, and sprint planning.

Sarah: The mobile app prototype got great feedback. We should prioritize push notifications - customers have requested it.

Mike: Agreed on Sarah's point. Analytics dashboard is gaining traction too. But we need infrastructure upgrades for increased load.

John: Good point Mike. Add infrastructure to action items. Sarah, lead push notifications?

Sarah: Absolutely. 3 weeks needed. I'll coordinate with design this week.

Mike: I'll assess infrastructure and present options by Monday.

Lisa: We have 5 requests for dark mode. Should we include this in Q1?

John: Let's evaluate. Lisa, compile feedback and business case by Friday?

Lisa: Will do.

John: Summary: Sarah on push notifications, Mike on infrastructure, Lisa on dark mode case. Meet Tuesday. Thanks!"""
            st.markdown('<div class="success-card"><strong>✅ Demo loaded!</strong></div>', unsafe_allow_html=True)
            st.rerun()

# TAB 3: Results
with tab3:
    if st.session_state.transcript:
        
        with st.expander("📄 View Original Transcript", expanded=False):
            st.text_area("Transcript Content", st.session_state.transcript, height=300, disabled=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Meeting Minutes with AI", key="generate_btn", use_container_width=True):
                with st.spinner("🤖 Generating minutes..."):
                    try:
                        genai.configure(api_key=gemini_api_key)
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        prompt = f"""Analyze this meeting transcript and generate comprehensive meeting minutes:

MEETING SUMMARY
===============
[2-3 sentence overview]

KEY DISCUSSION POINTS
====================
- Point 1
- Point 2
- Point 3

ACTION ITEMS
============
[ ] Owner: Task - Due date
[ ] Owner: Task - Due date

DECISIONS MADE
==============
- Decision 1
- Decision 2

PARTICIPANTS
============
[List of people]

NEXT STEPS
==========
[Key follow-ups]

Transcript:
{st.session_state.transcript}"""
                        
                        response = model.generate_content(prompt)
                        st.session_state.minutes = response.text
                        
                        st.markdown('<div class="success-card"><strong>✅ Minutes generated!</strong></div>', unsafe_allow_html=True)
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f'<div class="warning-card"><strong>❌ Failed: {str(e)[:80]}</strong></div>', unsafe_allow_html=True)
        
        if st.session_state.minutes:
            st.markdown("---")
            st.markdown("### 📋 Generated Meeting Minutes")
            st.markdown(st.session_state.minutes)
            
            col1, col2 = st.columns(2)
            with col1:
                txt_data = st.session_state.minutes
                st.download_button(
                    label="📥 Download as TXT",
                    data=txt_data,
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                json_data = {
                    "timestamp": datetime.now().isoformat(),
                    "transcript": st.session_state.transcript,
                    "minutes": st.session_state.minutes
                }
                st.download_button(
                    label="📥 Download as JSON",
                    data=json.dumps(json_data, indent=2),
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.markdown("""
            <div class='info-card'>
                <strong>📝 No transcript yet</strong><br/><br/>
                1. Upload audio or paste transcript<br/>
                2. Click "Generate Minutes"<br/>
                3. Download results
            </div>
        """, unsafe_allow_html=True)
