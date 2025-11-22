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
    initial_sidebar_state="expanded"
)
# Professional CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    .main {
        padding: 1rem 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main > div {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -2px;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.25rem;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.1);
    }
    
    .info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(33, 150, 243, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(255, 193, 7, 0.1);
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #f1f5f9;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #667eea;
        padding: 1rem;
    }
    
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        font-family: 'Monaco', monospace;
    }
    
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem 1rem;
    }
    
    .api-link {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .api-link:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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
# Header
st.markdown("<h1>📝 Smart Meeting Minutes</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your meeting recordings into actionable insights with AI</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔐 API Configuration")
    
    st.markdown("#### 🔑 OpenAI API Key")
    openai_api_key = st.text_input(
        "Enter OpenAI Key",
        type="password",
        help="For Whisper audio transcription",
        placeholder="sk-...",
        value=os.getenv("OPENAI_API_KEY", "")
    )
    if openai_api_key:
        st.success("✅ OpenAI key configured")
    else:
        st.markdown("""
        <div style='background: #fee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44336;'>
            <strong>⚠️ Required for audio transcription</strong><br/>
            <a href='https://platform.openai.com/api-keys' target='_blank' class='api-link'>
                🔗 Get OpenAI API Key
            </a>
        </div>
        """, unsafe_allow_html=True)
    #hello
    st.markdown("#### 🤖 Google Gemini API Key")
    gemini_api_key = st.text_input(
        "Enter Gemini Key",
        type="password",
        help="For generating meeting minutes",
        placeholder="AIza...",
        value=os.getenv("GEMINI_API_KEY", "")
    )
    
    if gemini_api_key:
        st.success("✅ Gemini key configured")
    else:
        st.markdown("""
        <div style='background: #fee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44336;'>
            <strong>⚠️ Required for minutes generation</strong><br/>
            <a href='https://aistudio.google.com/app/apikey' target='_blank' class='api-link'>
                🔗 Get Gemini API Key
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    if gemini_api_key and st.button("🧪 Test Gemini API", use_container_width=True):
        with st.spinner("Testing API..."):
            try:
                genai.configure(api_key=gemini_api_key)
                
                # Force the model directly
                working_model_name = 'gemini-2.5-flash'
                model = genai.GenerativeModel(working_model_name)
                response = model.generate_content("Say 'Test successful'")
                
                if response.text:
                    st.success(f"✅ API Working! Using: {working_model_name}")
                else:
                    raise Exception("No response from model")
                    
            except Exception as e:
                st.error(f"❌ API Test Failed: {str(e)}")
                st.info("Check your API key or create a new one at: https://aistudio.google.com/app/apikey")
    
    st.markdown("---")
    
    st.markdown("### 📚 Quick Guide")
    st.markdown("""
    **Step 1:** Get your API keys
    - OpenAI: For transcription
    - Gemini: For analysis
    
    **Step 2:** Upload audio or paste text
    
    **Step 3:** Generate minutes
    
    **Step 4:** Download results
    """)
    
    st.markdown("---")
    
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🎤 Audio transcription (Whisper)
    - 🤖 AI-powered analysis
    - ✅ Action items extraction
    - 👥 Participant tracking
    - 📥 Multiple export formats
    - 🎯 Decision highlights
    """)
    
    st.markdown("---")
    
    st.markdown("### 💰 Pricing Info")
    st.markdown("""
    **Gemini API (FREE Tier):**
    - ✅ 15 requests/min (FREE)
    - ✅ 1,500 requests/day (FREE)
    - ✅ 1 million tokens/day (FREE)
    
    **OpenAI Whisper:**
    - 💵 $0.006 per minute of audio
    - Example: 10 min meeting = $0.06
    
    **Total Cost per Meeting:**
    - ~$0.06 for 10-minute audio
    - Gemini analysis: FREE! ✨
    """)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎤 Upload Audio", "✍️ Paste Transcript", "📊 Results"])

# TAB 1: Upload Audio
with tab1:
    st.markdown("### 🎤 Upload Meeting Recording")
    
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
                    📁 {audio_file.name}<br/>
                    💾 Size: {file_size_mb:.2f} MB<br/>
                    🎵 Format: {audio_file.type}
                </div>
            """, unsafe_allow_html=True)
            
            st.audio(audio_file)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            if st.button("🚀 Transcribe Audio with AI", key="transcribe_btn", use_container_width=True):
                if not openai_api_key:
                    st.error("⚠️ Please enter your OpenAI API key in the sidebar first!")
                else:
                    with st.spinner("🎯 Transcribing audio with Whisper AI... Please wait..."):
                        try:
                            # Initialize OpenAI
                            client = OpenAI(api_key=openai_api_key)
                            
                            # Create temp file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                                tmp_file.write(audio_file.getvalue())
                                tmp_file_path = tmp_file.name
                            
                            # Transcribe
                            with open(tmp_file_path, "rb") as audio_data:
                                transcript_response = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_data,
                                    response_format="text"
                                )
                            
                            # Cleanup
                            os.unlink(tmp_file_path)
                            
                            # Store transcript
                            st.session_state.transcript = transcript_response
                            
                            st.success("✅ Transcription completed successfully!")
                            st.balloons()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Transcription failed: {str(e)}")
                            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                                os.unlink(tmp_file_path)
    
    with col2:
        st.markdown("""
            <div class='info-card'>
                <strong>💡 Tips for Best Results</strong><br/><br/>
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
                    <strong>⏱️ Processing Time</strong><br/>
                    Estimated: ~{est_time:.1f} min
                </div>
            """, unsafe_allow_html=True)

# TAB 2: Paste Transcript
with tab2:
    st.markdown("### ✍️ Manual Transcript Input")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        transcript_input = st.text_area(
            "Paste your meeting transcript here:",
            value=st.session_state.transcript,
            height=450,
            placeholder="Enter or paste your meeting transcript here...\n\nExample:\nJohn: Welcome everyone to today's meeting.\nSarah: Thanks John, let's start with the agenda...",
            help="You can paste an existing transcript if you already have one"
        )
    
    with col2:
        if st.button("💾 Save Transcript", key="save_transcript", use_container_width=True):
            if transcript_input.strip():
                st.session_state.transcript = transcript_input
                st.success("✅ Transcript saved!")
            else:
                st.warning("⚠️ Please enter some text first")
        
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
            st.success("✅ Demo transcript loaded!")
            st.rerun()

# TAB 3: Results
with tab3:
    if st.session_state.transcript:
        
        # Show transcript preview
        with st.expander("📄 View Original Transcript", expanded=False):
            st.text_area("Transcript Content", st.session_state.transcript, height=300, disabled=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Meeting Minutes with AI", key="generate_btn", use_container_width=True):
                if not gemini_api_key:
                    st.error("⚠️ Please enter your Gemini API key in the sidebar first!")
                else:
                    with st.spinner("🤖 Analyzing transcript and generating comprehensive meeting minutes..."):
                        try:
                            # Configure Gemini with correct API version
                            genai.configure(api_key=gemini_api_key)
                            
                            # List available models to debug
                            try:
                                available_models = [m.name for m in genai.list_models()]
                                st.info(f"🔍 Available models: {', '.join(available_models[:3])}")
                            except:
                                pass
                            
                            # Try multiple model names in order of preference
                            # Prioritizing the latest stable models
                            model_names = [
                                'gemini-2.5-flash',
                                'gemini-1.5-flash',
                                'models/gemini-2.5-flash',
                                'models/gemini-1.5-flash',
                                'models/gemini-1.5-pro-latest',
                                'models/gemini-2.5-pro'
                            ]
                            
                            model = None
                            working_model_name = None
                            
                            for model_name in model_names:
                                try:
                                    model = genai.GenerativeModel(model_name)
                                    # Test with a simple prompt
                                    test_response = model.generate_content("Say 'OK'")
                                    if test_response.text:
                                        working_model_name = model_name
                                        st.success(f"✅ Using model: {model_name}")
                                        break
                                except:
                                    continue
                            
                            # Temporary Debug: Force to use the most common model
                            working_model_name = 'gemini-2.5-flash'
                            model = genai.GenerativeModel(working_model_name)
                            st.success(f"✅ Using forced model: {working_model_name}")
                            
                            # Test the forced model first
                            try:
                                test_response = model.generate_content("Say 'OK'")
                                if not test_response.text:
                                    raise Exception("Model test failed")
                            except Exception as test_error:
                                st.error(f"❌ Forced model failed: {str(test_error)}")
                                st.info("💡 Try fallback models...")
                                
                                # Fallback to model list if forced model fails
                                model_names = [
                                    'gemini-1.5-flash',
                                    'models/gemini-2.5-flash',
                                    'models/gemini-1.5-flash'
                                ]
                                
                                for model_name in model_names:
                                    try:
                                        model = genai.GenerativeModel(model_name)
                                        test_response = model.generate_content("Say 'OK'")
                                        if test_response.text:
                                            working_model_name = model_name
                                            st.success(f"✅ Using fallback model: {model_name}")
                                            break
                                    except:
                                        continue
                                
                                if not working_model_name or working_model_name == 'gemini-2.5-flash':
                                    raise Exception("No working model found")
                            
                            # Prompt
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

                            response = model.generate_content(prompt)
                            
                            # Parse JSON
                            response_text = response.text.strip()
                            response_text = response_text.replace("```json", "").replace("```", "").strip()
                            
                            st.session_state.minutes = json.loads(response_text)
                            st.success("✅ Meeting minutes generated successfully!")
                            st.balloons()
                            st.rerun()
                            
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Failed to parse response as JSON: {str(e)}")
                            st.info("💡 The AI returned invalid JSON. Try again or use a different transcript.")
                        except Exception as e:
                            st.error(f"❌ Generation failed: {str(e)}")
                            st.info("💡 Troubleshooting steps:")
                            st.markdown("""
                            1. Verify your API key is correct
                            2. Check if Gemini API is enabled at: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
                            3. Try creating a new API key at: https://aistudio.google.com/app/apikey
                            4. Make sure your transcript is not empty
                            """)
        
        # Display Minutes
        if st.session_state.minutes:
            st.markdown("<br/><br/>", unsafe_allow_html=True)
            st.markdown("## 📋 Generated Meeting Minutes")
            st.markdown("---")
            
            minutes = st.session_state.minutes
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("""
                    <div class='metric-card' style='text-align: center;'>
                        <h3 style='color: #667eea; margin: 0;'>📅</h3>
                        <p style='margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #64748b;'>Date</p>
                        <p style='margin: 0; font-weight: 600; color: #1e293b;'>{}</p>
                    </div>
                """.format(minutes.get('date', 'N/A')), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class='metric-card' style='text-align: center;'>
                        <h3 style='color: #764ba2; margin: 0;'>👥</h3>
                        <p style='margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #64748b;'>Participants</p>
                        <p style='margin: 0; font-weight: 600; color: #1e293b;'>{}</p>
                    </div>
                """.format(len(minutes.get('participants', []))), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class='metric-card' style='text-align: center;'>
                        <h3 style='color: #667eea; margin: 0;'>✅</h3>
                        <p style='margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #64748b;'>Action Items</p>
                        <p style='margin: 0; font-weight: 600; color: #1e293b;'>{}</p>
                    </div>
                """.format(len(minutes.get('action_items', []))), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                    <div class='metric-card' style='text-align: center;'>
                        <h3 style='color: #764ba2; margin: 0;'>🎯</h3>
                        <p style='margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #64748b;'>Decisions</p>
                        <p style='margin: 0; font-weight: 600; color: #1e293b;'>{}</p>
                    </div>
                """.format(len(minutes.get('decisions', []))), unsafe_allow_html=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Two Column Layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Summary
                st.markdown("### 📋 Executive Summary")
                st.markdown(f"""
                    <div class='info-card'>
                        {minutes.get('summary', 'N/A')}
                    </div>
                """, unsafe_allow_html=True)
                
                # Participants
                st.markdown("### 👥 Participants")
                for p in minutes.get('participants', []):
                    st.markdown(f"• **{p}**")
                
                st.markdown("<br/>", unsafe_allow_html=True)
                
                # Key Points
                st.markdown("### 💡 Key Discussion Points")
                for i, point in enumerate(minutes.get('key_points', []), 1):
                    st.markdown(f"**{i}.** {point}")
            
            with col2:
                # Decisions
                st.markdown("### ✅ Decisions Made")
                for i, decision in enumerate(minutes.get('decisions', []), 1):
                    st.markdown(f"""
                        <div class='success-card'>
                            <strong>{i}.</strong> {decision}
                        </div>
                    """, unsafe_allow_html=True)
                
                # Next Meeting
                if minutes.get('next_meeting'):
                    st.markdown("### 📅 Next Meeting")
                    st.info(minutes.get('next_meeting'))
            
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
            
            # TXT Export
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
            
            # JSON Export
            with col2:
                st.download_button(
                    label="📊 Download JSON",
                    data=json.dumps(minutes, indent=2),
                    file_name=f"minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Markdown Export
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
            <div class='warning-card' style='text-align: center; padding: 3rem;'>
                <h2>👈 Get Started</h2>
                <p style='font-size: 1.1rem; margin-top: 1rem;'>
                    Upload an audio file or paste a transcript to generate meeting minutes
                </p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 0.5rem;'>
            Built with ❤️ using Streamlit, OpenAI Whisper & Google Gemini
        </p>
        <p style='color: #94a3b8;'>
            🚀 Transform meetings into actionable insights in seconds
        </p>
    </div>
""", unsafe_allow_html=True)

import time
import traceback

def exponential_backoff(fn, max_retries=4, initial_delay=1.0):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            msg = str(e).lower()
            # If rate-limited or quota exceeded, retry with backoff
            if '429' in msg or 'quota' in msg or 'rate limit' in msg or 'rate-limited' in msg or 'insufficient_quota' in msg:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise
            else:
                # not a rate/quota error -> rethrow
                raise

# The prompt format you want (same JSON structure)
minutes_prompt_template = f"""Analyze this meeting transcript and generate comprehensive meeting minutes in JSON format.

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

# Attempt Gemini first with retries/backoff
gemini_success = False
minutes_json = None

if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)

        # Try to get model list and pick candidates (safe defaults)
        try:
            candidates = [m.name for m in genai.list_models()]
        except Exception:
            # fallback candidate list
            candidates = [
                'models/gemini-2.5-flash',
                'models/gemini-1.5-flash',
                'gemini-2.5-flash',
                'gemini-1.5-flash'
            ]

        # ensure unique ordering and prefer modern models
        preferred_order = []
        for name in ['gemini-2.5-flash', 'models/gemini-2.5-flash', 'gemini-1.5-flash', 'models/gemini-1.5-flash']:
            if name in candidates and name not in preferred_order:
                preferred_order.append(name)
        # append any remaining
        for c in candidates:
            if c not in preferred_order:
                preferred_order.append(c)

        # Try models with exponential backoff for rate errors
        for model_name in preferred_order:
            def try_model():
                model = genai.GenerativeModel(model_name)
                resp = model.generate_content(minutes_prompt_template)
                # genai returns an object; check text
                txt = getattr(resp, 'text', None)
                if not txt:
                    raise Exception("Empty response from model")
                return txt

            try:
                response_text = exponential_backoff(try_model, max_retries=4, initial_delay=1.0)
                # Clean and parse
                response_text = response_text.strip().replace("```json", "").replace("```", "").strip()
                minutes_json = json.loads(response_text)
                gemini_success = True
                st.success(f"✅ Generated minutes using Gemini model: {model_name}")
                break
            except Exception as model_err:
                # If a quota error bubbled up, try next model; otherwise log and continue
                st.warning(f"Model {model_name} failed: {str(model_err)[:200]}")
                continue

    except Exception as e:
        st.info("Gemini attempt failed; will try fallback summarizers.")
        st.debug = getattr(st, "debug", lambda *a, **k: None)
        st.debug(traceback.format_exc())

# If Gemini failed, fallback to OpenAI Chat (if OpenAI key present)
if not gemini_success:
    st.warning("⚠️ Gemini unavailable or rate-limited. Falling back to OpenAI for minutes generation (if OpenAI key provided).")
    if openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            # Build chat prompt that instructs the model to return valid JSON only
            chat_prompt = [
                {"role": "system", "content": "You are a helpful assistant that MUST return ONLY valid JSON in the exact structure requested."},
                {"role": "user", "content": minutes_prompt_template}
            ]
            # Use gpt-4o or gpt-4 if available in your account; fall back to gpt-3.5-turbo
            chosen_model = "gpt-4o"  # try this; if not available, use gpt-4 or gpt-3.5-turbo
            try:
                chat_resp = client.chat.completions.create(model=chosen_model, messages=chat_prompt, temperature=0.0)
            except Exception:
                # fallback
                chat_resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=chat_prompt, temperature=0.0)

            text_out = chat_resp.choices[0].message["content"]
            text_out = text_out.strip().replace("```json", "").replace("```", "").strip()
            minutes_json = json.loads(text_out)
            st.success("✅ Generated minutes using OpenAI fallback")
        except json.JSONDecodeError as je:
            st.error(f"❌ OpenAI returned non-JSON or malformed JSON: {str(je)}")
            st.info("Try regenerating or edit the transcript to be shorter/cleaner.")
        except Exception as e:
            st.error(f"❌ OpenAI fallback failed: {str(e)}")
    else:
        st.error("❌ No working summarization API available (Gemini rate-limited and no OpenAI key provided). Please add an OpenAI key or resolve Gemini quota.")

# If minutes_json built, save to session_state and render as before
if minutes_json:
    st.session_state.minutes = minutes_json
    st.success("✅ Meeting minutes generated!")
    st.balloons()
    st.rerun()