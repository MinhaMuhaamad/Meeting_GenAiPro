import streamlit as st
import google.generativeai as genai
import assemblyai as aai
from datetime import datetime
import json
import tempfile
import os
import time
import traceback
from dotenv import load_dotenv

load_dotenv()

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Smart Meeting Minutes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Premium CSS Design System
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    html, body {
        background: #f5f7fa;
        color: #1a202c;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main {
        padding: 0 !important;
    }
    
    .main > div {
        background: transparent;
        padding: 2rem 3rem !important;
    }
    
    /* Smooth Animations */
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
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    /* Header Styles */
    h1 {
        font-family: 'Poppins', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-align: center;
        margin: 0 0 0.5rem 0 !important;
        letter-spacing: -0.5px !important;
        animation: fadeInUp 0.6s ease-out !important;
        text-shadow: 0 2px 20px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        margin-bottom: 3rem !important;
        animation: fadeInUp 0.8s ease-out !important;
        letter-spacing: 0.3px !important;
    }
    
    h2 {
        color: #2d3748 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        margin: 2rem 0 1rem 0 !important;
    }
    
    h3 {
        color: #4a5568 !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin: 1.5rem 0 0.75rem 0 !important;
    }
    
    p, label, span {
        color: #4a5568 !important;
        line-height: 1.6 !important;
    }
    
    /* Card System */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Button Styles */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.4) !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Alert Cards */
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-left: 4px solid #28a745 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 !important;
        color: #155724 !important;
        animation: slideIn 0.4s ease-out !important;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.15) !important;
    }
    
    .info-card {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-left: 4px solid #17a2b8 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 !important;
        color: #0c5460 !important;
        animation: slideIn 0.4s ease-out !important;
        box-shadow: 0 2px 8px rgba(23, 162, 184, 0.15) !important;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border-left: 4px solid #ffc107 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 !important;
        color: #856404 !important;
        animation: slideIn 0.4s ease-out !important;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.15) !important;
    }
    
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-left: 4px solid #dc3545 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 !important;
        color: #721c24 !important;
        animation: slideIn 0.4s ease-out !important;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.15) !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.3) !important;
        border-color: #667eea !important;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: white;
        padding: 0.75rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 0.875rem 1.75rem;
        font-weight: 600 !important;
        color: #718096 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #2d3748 !important;
        transition: all 0.3s ease !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #cbd5e0 !important;
        padding: 1.5rem;
        background: #f7fafc !important;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: #667eea !important;
        background: #edf2f7 !important;
    }
    
    /* Expander */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] > div {
        background: white;
        padding: 2rem 1.5rem;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #2d3748 !important;
        font-size: 1.125rem !important;
        font-weight: 700 !important;
        margin: 1.5rem 0 1rem 0 !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] h4 {
        color: #4a5568 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin: 1.25rem 0 0.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li {
        color: #718096 !important;
        font-size: 0.875rem !important;
        line-height: 1.6 !important;
    }
    
    section[data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Links */
    .api-link {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 0.625rem 1.25rem;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .api-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
    }
    
    a {
        color: #667eea !important;
        text-decoration: none !important;
        font-weight: 500;
        transition: color 0.3s ease !important;
    }
    
    a:hover {
        color: #764ba2 !important;
    }
    
    /* Banner */
    .banner {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .banner h2 {
        margin: 0 0 0.5rem 0 !important;
        color: #2d3748 !important;
    }
    
    .banner p {
        margin: 0;
        color: #718096 !important;
        font-size: 1rem;
    }
    
    /* Loading Animation */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ''
if 'minutes' not in st.session_state:
    st.session_state.minutes = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Utility function for exponential backoff
def exponential_backoff(fn, max_retries=4, initial_delay=1.0):
    """Retry function with exponential backoff for rate limiting"""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            msg = str(e).lower()
            if '429' in msg or 'quota' in msg or 'rate limit' in msg or 'exceeded' in msg:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise
            else:
                raise

# Header
st.markdown("<h1>📝 Smart Meeting Minutes</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your meeting recordings into actionable insights with AI</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔐 API Configuration")
    st.markdown("Configure your API keys to unlock AI-powered features")
    
    st.markdown("---")
    
    # AssemblyAI Section
    st.markdown("#### 🔑 AssemblyAI API Key")
    st.caption("Required for audio transcription")
    assemblyai_api_key = st.text_input(
        "AssemblyAI API Key",
        type="password",
        placeholder="Enter your AssemblyAI API key",
        value=os.getenv("ASSEMBLYAI_API_KEY", "58e21640448c4658b483b99c076b9ab2"),
        key="assemblyai_key",
        label_visibility="collapsed"
    )
    
    if assemblyai_api_key:
        st.success("✅ AssemblyAI configured")
    else:
        st.warning("⚠️ AssemblyAI key required")
        st.markdown("""
        <a href='https://www.assemblyai.com/dashboard/signup' target='_blank' class='api-link'>
            Get API Key
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Gemini Section
    st.markdown("#### 🤖 Google Gemini API Key")
    st.caption("Required for generating meeting minutes")
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        value=os.getenv("GEMINI_API_KEY", ""),
        key="gemini_key",
        label_visibility="collapsed"
    )
    
    if gemini_api_key:
        st.success("✅ Gemini configured")
        
        if st.button("🧪 Test Connection", use_container_width=True):
            with st.spinner("Testing API..."):
                try:
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    response = model.generate_content("Say 'OK'")
                    
                    if response.text:
                        st.success(f"✅ Connected successfully!")
                    else:
                        raise Exception("No response")
                except Exception as e:
                    error_msg = str(e)
                    if '429' in error_msg or 'quota' in error_msg.lower():
                        st.error("❌ Quota exceeded. Try again later or check your billing.")
                    else:
                        st.error(f"❌ Connection failed: {error_msg[:50]}")
    else:
        st.warning("⚠️ Gemini key required")
        st.markdown("""
        <a href='https://aistudio.google.com/app/apikey' target='_blank' class='api-link'>
            Get API Key
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Guide
    st.markdown("### 📚 How It Works")
    st.markdown("""
    1. **Configure** your API keys above
    2. **Upload** audio or paste transcript
    3. **Generate** AI-powered minutes
    4. **Download** in multiple formats
    """)
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Key Features")
    st.markdown("""
    - 🎤 Audio transcription
    - 🤖 AI analysis
    - ✅ Action items
    - 👥 Participant tracking
    - 📥 Export options
    """)
    
    st.markdown("---")
    
    # Pricing
    st.markdown("### 💰 Pricing")
    st.markdown("**AssemblyAI:** $0.00025/sec (~$0.015/min)")
    st.markdown("**Gemini:** FREE (1M tokens/day)")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎤 Upload Audio", "✍️ Paste Transcript", "📊 Results"])

# TAB 1: Upload Audio
with tab1:
    st.markdown("""
        <div class='banner'>
            <h2>🎤 Upload Meeting Recording</h2>
            <p>Upload your audio file and let AI transcribe it automatically using AssemblyAI</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        audio_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'webm'],
            help="Supported formats: MP3, WAV, M4A, OGG, FLAC, WebM"
        )
        
        if audio_file:
            file_size_mb = audio_file.size / (1024 * 1024)
            st.markdown(f"""
                <div class='success-card'>
                    <strong>✅ File Uploaded Successfully</strong><br/>
                    📁 {audio_file.name}<br/>
                    💾 Size: {file_size_mb:.2f} MB
                </div>
            """, unsafe_allow_html=True)
            
            st.audio(audio_file)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            if st.button("🚀 Transcribe Audio", key="transcribe_btn", use_container_width=True):
                if not assemblyai_api_key:
                    st.error("⚠️ Please enter your AssemblyAI API key in the sidebar first!", icon="⚠️")
                else:
                    with st.spinner("🎯 Transcribing audio... Please wait..."):
                        try:
                            # Set AssemblyAI API key
                            aai.settings.api_key = assemblyai_api_key
                            
                            # Save audio file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                                tmp_file.write(audio_file.getvalue())
                                tmp_file_path = tmp_file.name
                            
                            # Configure transcription with universal speech model
                            config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal)
                            
                            # Transcribe audio file
                            transcript = aai.Transcriber(config=config).transcribe(tmp_file_path)
                            
                            # Check for errors
                            if transcript.status == "error":
                                raise RuntimeError(f"Transcription failed: {transcript.error}")
                            
                            # Clean up temp file
                            os.unlink(tmp_file_path)
                            
                            # Save transcript to session state
                            st.session_state.transcript = transcript.text
                            
                            st.success("✅ Transcription completed successfully!", icon="✅")
                            st.balloons()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Transcription failed: {str(e)}", icon="❌")
                            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                                os.unlink(tmp_file_path)
    
    with col2:
        st.markdown("""
            <div class='info-card'>
                <strong>💡 Best Practices</strong><br/><br/>
                ✓ Clear audio quality<br/>
                ✓ Minimal background noise<br/>
                ✓ Max file size: 25 MB<br/>
                ✓ Supported: MP3, WAV, M4A
            </div>
        """, unsafe_allow_html=True)
        
        if audio_file:
            est_time = (file_size_mb * 0.3)
            st.markdown(f"""
                <div class='warning-card'>
                    <strong>⏱️ Estimated Time</strong><br/>
                    Processing: ~{est_time:.1f} min
                </div>
            """, unsafe_allow_html=True)

# TAB 2: Paste Transcript
with tab2:
    st.markdown("""
        <div class='banner'>
            <h2>✍️ Manual Transcript Input</h2>
            <p>Already have a transcript? Paste it here and generate AI-powered meeting minutes</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        transcript_input = st.text_area(
            "Paste your meeting transcript",
            value=st.session_state.transcript,
            height=400,
            placeholder="Enter or paste your meeting transcript here...\n\nExample:\nJohn: Welcome everyone to today's meeting.\nSarah: Thanks John, let's start with the agenda...",
            help="Paste your existing transcript to skip audio transcription"
        )
    
    with col2:
        if st.button("💾 Save Transcript", key="save_transcript", use_container_width=True):
            if transcript_input.strip():
                st.session_state.transcript = transcript_input
                st.success("✅ Transcript saved!", icon="✅")
            else:
                st.warning("⚠️ Please enter some text first", icon="⚠️")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        if st.button("🧪 Load Demo", key="demo_btn", use_container_width=True):
            st.session_state.transcript = """Welcome everyone to today's product planning meeting. Let's start with our agenda.

John: Thanks for joining everyone. Today we need to discuss three main items: the Q1 product roadmap, the new feature requests from customers, and our sprint planning for the next two weeks.

Sarah: Great. On the roadmap side, we've received really positive feedback on the mobile app prototype. I think we should prioritize the push notification feature that users have been requesting.

Mike: I agree with Sarah. The analytics dashboard is also getting traction. However, I'm concerned about our backend infrastructure. We need to upgrade our servers before we can handle the increased load.

John: Good point Mike. Let's add infrastructure upgrades to the action items. Sarah, can you lead the push notification feature development?

Sarah: Absolutely. I'll need about 3 weeks for the full implementation. I'll coordinate with the design team this week.

Mike: I'll work on the infrastructure assessment and present options by next Monday.

Lisa: One more thing - we have 5 customer requests for the dark mode feature. Should we consider this for Q1?

John: Let's evaluate that. Lisa, can you compile the customer feedback and business case by Friday?

Lisa: Will do.

John: Perfect. To summarize: Sarah is leading push notifications, Mike is assessing infrastructure, and Lisa is preparing the dark mode business case. Let's reconvene next Tuesday. Thanks everyone!"""
            st.success("✅ Demo transcript loaded!", icon="✅")
            st.rerun()

# TAB 3: Results
with tab3:
    if st.session_state.transcript:
        
        with st.expander("📄 View Original Transcript", expanded=False):
            st.text_area("Transcript Content", st.session_state.transcript, height=300, disabled=True, label_visibility="collapsed")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Meeting Minutes", key="generate_btn", use_container_width=True):
                if not gemini_api_key:
                    st.error("⚠️ Please enter your Gemini API key in the sidebar first!", icon="⚠️")
                else:
                    with st.spinner("🤖 Generating comprehensive meeting minutes..."):
                        try:
                            genai.configure(api_key=gemini_api_key)
                            
                            prompt = f"""Analyze this meeting transcript and generate comprehensive meeting minutes in JSON format.

Transcript:
{st.session_state.transcript}

Return ONLY valid JSON in this exact structure:
{{
    "meeting_title": "Brief descriptive title",
    "date": "{datetime.now().strftime('%B %d, %Y')}",
    "participants": ["Name1", "Name2"],
    "summary": "2-3 sentence executive summary",
    "key_points": ["Point 1", "Point 2"],
    "decisions": ["Decision 1", "Decision 2"],
    "action_items": [
        {{
            "task": "Task description",
            "assignee": "Person name",
            "deadline": "Deadline or timeframe"
        }}
    ],
    "next_meeting": "Next meeting info or null"
}}"""
                            
                            model_names = [
                                'gemini-2.0-flash-exp',
                                'gemini-1.5-flash',
                                'gemini-1.5-pro',
                                'models/gemini-2.0-flash-exp',
                                'models/gemini-1.5-flash'
                            ]
                            
                            minutes_json = None
                            working_model_name = None
                            
                            for model_name in model_names:
                                try:
                                    def try_model():
                                        model = genai.GenerativeModel(model_name)
                                        resp = model.generate_content(prompt)
                                        txt = getattr(resp, 'text', None)
                                        if not txt:
                                            raise Exception("Empty response")
                                        return txt
                                    
                                    response_text = exponential_backoff(try_model, max_retries=3, initial_delay=2.0)
                                    response_text = response_text.strip().replace("```json", "").replace("```", "").strip()
                                    minutes_json = json.loads(response_text)
                                    working_model_name = model_name
                                    break
                                    
                                except Exception as model_err:
                                    error_msg = str(model_err).lower()
                                    if '429' in error_msg or 'quota' in error_msg or 'exceeded' in error_msg:
                                        st.warning(f"⚠️ {model_name}: Quota exceeded, trying next model...", icon="⚠️")
                                        continue
                                    else:
                                        continue
                            
                            if not minutes_json:
                                st.markdown("""
                                    <div class='error-card'>
                                        <strong>❌ All Gemini models are currently unavailable</strong><br/><br/>
                                        <strong>Possible reasons:</strong><br/>
                                        • API quota exceeded (429 error)<br/>
                                        • Rate limit reached<br/>
                                        • Billing issue<br/><br/>
                                        <strong>Solutions:</strong><br/>
                                        1. Wait a few minutes and try again<br/>
                                        2. Check your quota at <a href='https://aistudio.google.com' target='_blank'>Google AI Studio</a><br/>
                                        3. Verify billing is enabled<br/>
                                        4. Try using a different API key
                                    </div>
                                """, unsafe_allow_html=True)
                                st.stop()
                            
                            st.session_state.minutes = minutes_json
                            st.success(f"✅ Minutes generated using {working_model_name}!", icon="✅")
                            st.balloons()
                            st.rerun()
                            
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON response: {str(e)}", icon="❌")
                        except Exception as e:
                            error_msg = str(e)
                            if '429' in error_msg or 'quota' in error_msg.lower():
                                st.markdown("""
                                    <div class='error-card'>
                                        <strong>❌ API Quota Exceeded</strong><br/><br/>
                                        Your Gemini API quota has been exceeded. Please:<br/>
                                        1. Wait a few minutes and try again<br/>
                                        2. Check your quota at <a href='https://aistudio.google.com' target='_blank'>Google AI Studio</a><br/>
                                        3. Verify your API key is correct<br/>
                                        4. Ensure billing is enabled if using paid tier
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.error(f"❌ Generation failed: {error_msg}", icon="❌")
        
        if st.session_state.minutes:
            st.markdown("<br/><br/>", unsafe_allow_html=True)
            
            st.markdown("""
                <div class='banner'>
                    <h2>📋 Generated Meeting Minutes</h2>
                    <p>AI-powered analysis of your meeting transcript</p>
                </div>
            """, unsafe_allow_html=True)
            
            minutes = st.session_state.minutes
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size: 2rem;'>📅</div>
                        <div class='metric-label'>Date</div>
                        <div class='metric-value' style='font-size: 1rem; color: #4a5568;'>{minutes.get('date', 'N/A')}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size: 2rem;'>👥</div>
                        <div class='metric-label'>Participants</div>
                        <div class='metric-value'>{len(minutes.get('participants', []))}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size: 2rem;'>✅</div>
                        <div class='metric-label'>Action Items</div>
                        <div class='metric-value'>{len(minutes.get('action_items', []))}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div style='font-size: 2rem;'>🎯</div>
                        <div class='metric-label'>Decisions</div>
                        <div class='metric-value'>{len(minutes.get('decisions', []))}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Content Grid
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📋 Executive Summary")
                st.markdown(f"""
                    <div class='info-card'>
                        {minutes.get('summary', 'N/A')}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 👥 Participants")
                for p in minutes.get('participants', []):
                    st.markdown(f"• **{p}**")
                
                st.markdown("### 💡 Key Discussion Points")
                for i, point in enumerate(minutes.get('key_points', []), 1):
                    st.markdown(f"**{i}.** {point}")
            
            with col2:
                st.markdown("### ✅ Decisions Made")
                for i, decision in enumerate(minutes.get('decisions', []), 1):
                    st.markdown(f"""
                        <div class='success-card'>
                            <strong>{i}.</strong> {decision}
                        </div>
                    """, unsafe_allow_html=True)
                
                if minutes.get('next_meeting'):
                    st.markdown("### 📅 Next Meeting")
                    st.info(minutes.get('next_meeting'), icon="📅")
            
            # Action Items
            st.markdown("---")
            st.markdown("### 🎯 Action Items")
            
            for i, item in enumerate(minutes.get('action_items', []), 1):
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(f"**{i}. {item.get('task', 'N/A')}**")
                with col2:
                    st.markdown(f"👤 **{item.get('assignee', 'Unassigned')}**")
                with col3:
                    st.markdown(f"📅 **{item.get('deadline', 'No deadline')}**")
                st.markdown("---")
            
            # Export Section
            st.markdown("### 📥 Export Meeting Minutes")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                minutes_text = f"""MEETING MINUTES
{'=' * 60}

Meeting: {minutes.get('meeting_title', 'N/A')}
Date: {minutes.get('date', 'N/A')}

PARTICIPANTS
{'-' * 60}
{chr(10).join('• ' + p for p in minutes.get('participants', []))}

EXECUTIVE SUMMARY
{'-' * 60}
{minutes.get('summary', 'N/A')}

KEY DISCUSSION POINTS
{'-' * 60}
{chr(10).join(f'{i}. {p}' for i, p in enumerate(minutes.get('key_points', []), 1))}

DECISIONS MADE
{'-' * 60}
{chr(10).join(f'{i}. {d}' for i, d in enumerate(minutes.get('decisions', []), 1))}

ACTION ITEMS
{'-' * 60}
{chr(10).join(f'{i}. {item.get("task", "N/A")} - {item.get("assignee", "N/A")} - Due: {item.get("deadline", "N/A")}' for i, item in enumerate(minutes.get('action_items', []), 1))}

NEXT MEETING
{'-' * 60}
{minutes.get('next_meeting', 'N/A')}
"""
                st.download_button(
                    label="📄 Download TXT",
                    data=minutes_text,
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📊 Download JSON",
                    data=json.dumps(minutes, indent=2),
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                markdown_text = f"""# {minutes.get('meeting_title', 'Meeting Minutes')}

**Date:** {minutes.get('date', 'N/A')}

## 👥 Participants
{chr(10).join('- ' + p for p in minutes.get('participants', []))}

## 📋 Executive Summary
{minutes.get('summary', 'N/A')}

## 💡 Key Discussion Points
{chr(10).join(f'{i}. {p}' for i, p in enumerate(minutes.get('key_points', []), 1))}

## ✅ Decisions Made
{chr(10).join(f'{i}. {d}' for i, d in enumerate(minutes.get('decisions', []), 1))}

## 🎯 Action Items
{chr(10).join(f'- **{item.get("task", "N/A")}** - Assigned to: {item.get("assignee", "N/A")} - Due: {item.get("deadline", "N/A")}' for item in minutes.get('action_items', []))}

## 📅 Next Meeting
{minutes.get('next_meeting', 'N/A')}
"""
                st.download_button(
                    label="📝 Download MD",
                    data=markdown_text,
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    
    else:
        st.markdown("""
            <div class='banner' style='text-align: center; padding: 4rem 2rem;'>
                <h2>👈 Get Started</h2>
                <p style='font-size: 1.125rem; margin-top: 1rem;'>
                    Upload an audio file or paste a transcript to generate AI-powered meeting minutes
                </p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: white;'>
        <p style='font-size: 1.1rem; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);'>
            Built with ❤️ using Streamlit, OpenAI Whisper & Google Gemini
        </p>
        <p style='color: rgba(255,255,255,0.7);'>
            🚀 Transform meetings into actionable insights in seconds
        </p>
    </div>
""", unsafe_allow_html=True)