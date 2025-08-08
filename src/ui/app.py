"""
Enhanced PII Detection Prototype - Clean Version
Simplified workflow: Database → AI Discovery → PII Analysis → Data Encryption → Results Display
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import time
import secrets
import hashlib
import base64
import json
import re
import difflib
import PyPDF2
from typing import List, Dict, Optional

def create_enhanced_dataframe(data, column_mappings=None, format_columns=None, style_columns=None):
    """Create an enhanced, styled DataFrame for better display"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Apply column mappings if provided
    if column_mappings:
        df = df.rename(columns=column_mappings)
    
    # Apply formatting if provided
    if format_columns:
        for col, formatter in format_columns.items():
            if col in df.columns:
                df[col] = df[col].apply(formatter)
    
    # Apply styling if provided
    styled_df = df
    if style_columns:
        def apply_style(val, col_styles):
            for pattern, style in col_styles.items():
                if pattern in str(val):
                    return style
            return ''
        
        for col, styles in style_columns.items():
            if col in df.columns:
                styled_df = styled_df.style.applymap(lambda x: apply_style(x, styles), subset=[col])
    
    return styled_df

def get_priority_style(val):
    """Get styling for priority/type values"""
    if val in ['HIGH', 'NAME']:
        return 'background-color: #ffcdd2; color: #d32f2f; font-weight: bold;'
    elif val == 'MEDIUM':
        return 'background-color: #fff3e0; color: #f57c00; font-weight: bold;'
    elif val == 'LOW':
        return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold;'
    else:
        return 'color: #333; font-weight: normal;'

# Import our enhanced modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import DatabaseManager
from database.real_database_manager import RealDatabaseManager
from database.vscode_sql_manager import VSCodeSQLManager
from database.multi_database_manager import MultiDatabaseManager
from core.pii_detector import PIIDetector
from core.ai_assistant import AIAssistant, ai_assistant
from core.results_manager import ResultsManager, results_manager, PiiDetectionResult
from core.encryption_manager import EncryptionManager, encryption_manager, data_protection
from core.utils import setup_logging, format_risk_score, mask_pii_value
from core.config import DATABASE_PROFILES, PII_PATTERNS
from core.env_config import env_config

# Setup
st.set_page_config(
    page_title=env_config.page_title,
    page_icon=env_config.page_icon,
    layout=env_config.layout,
    initial_sidebar_state="expanded"
)

# Initialize logging
logger = setup_logging()

# Initialize session state
if 'multi_db_manager' not in st.session_state:
    st.session_state.multi_db_manager = MultiDatabaseManager(use_real_data=True)
    
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = RealDatabaseManager()
        st.session_state.connection_type = "ODBC"
    except Exception as e:
        st.session_state.db_manager = VSCodeSQLManager() 
        st.session_state.connection_type = "VSCode"
    
if 'pii_detector' not in st.session_state:
    st.session_state.pii_detector = PIIDetector()

if 'ai_assistant' not in st.session_state:
    st.session_state.ai_assistant = ai_assistant
    
if 'results_manager' not in st.session_state:
    st.session_state.results_manager = results_manager
    
if 'encryption_manager' not in st.session_state:
    st.session_state.encryption_manager = encryption_manager
    
if 'current_connection' not in st.session_state:
    st.session_state.current_connection = None
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
    
if 'ai_table_recommendations' not in st.session_state:
    st.session_state.ai_table_recommendations = []
    
if 'use_real_data' not in st.session_state:
    st.session_state.use_real_data = True
    
if 'ai_api_key' not in st.session_state:
    st.session_state.ai_api_key = env_config.anthropic_api_key or ''

if 'logger' not in st.session_state:
    st.session_state.logger = logger

# Import utility functions for regulations processing
def make_prompt(system_message, user_message):
    """Create a prompt structure for AI interaction"""
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

def ask_ai_with_claude(prompt):
    """Use Claude AI for regulation processing"""
    try:
        if st.session_state.ai_assistant and st.session_state.ai_assistant.is_available():
            # Create a simple text prompt from the structured prompt
            system_msg = prompt[0]["content"] if len(prompt) > 0 else ""
            user_msg = prompt[1]["content"] if len(prompt) > 1 else ""
            
            # Use the existing AI assistant
            response = st.session_state.ai_assistant.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=4000,
                system=system_msg,
                messages=[{"role": "user", "content": user_msg}]
            )
            return response.content[0].text
        else:
            return "AI assistant not available. Please configure your Claude API key."
    except Exception as e:
        return f"Error processing with AI: {str(e)}"

def read_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""
    return text

def get_personal_data_definition(pdf_text):
    """Extract personal data definitions from PDF text using AI"""
    system_prompt = """You are an expert in laws and regulations. Based on the input text, generate a comprehensive list of attributes that denote personal data according to the regulation.

    Please provide:
    1. A list of personal data attributes mentioned in the text
    2. Brief definitions for each attribute
    3. The regulation's name and key details

    Format the output as a clean JSON structure with:
    - regulation_name: string
    - description: brief description of the regulation
    - personal_data_attributes: array of objects with "attribute" and "definition" fields
    - key_requirements: array of key compliance requirements
    - effective_date: if mentioned
    
    Do not make assumptions beyond what's explicitly stated in the document."""
    
    prompt = make_prompt(system_prompt, pdf_text)
    response = ask_ai_with_claude(prompt)
    
    try:
        # Try to parse as JSON
        json_response = json.loads(response)
        return json_response
    except json.JSONDecodeError:
        # If not valid JSON, return a structured response
        return {
            "regulation_name": "Unknown Regulation",
            "description": "Regulation document processed",
            "personal_data_attributes": response.split(",") if "," in response else [response],
            "key_requirements": ["See full document for details"],
            "processing_note": "Raw AI response (not structured JSON)",
            "raw_response": response
        }

def main():
    # Clean sidebar navigation with logo
    try:
        # Display logo in sidebar
        logo_path = os.path.join(os.path.dirname(__file__), "logo2.png")
        if os.path.exists(logo_path):
            st.sidebar.image(logo_path, width=200)
        else:
            st.sidebar.title("📋 Navigation")
    except Exception:
        # Fallback to text if logo fails to load
        st.sidebar.title("📋 Navigation")
    
    # AI Configuration - simplified
    st.sidebar.subheader("🤖 AI Configuration")
    ai_api_key = st.sidebar.text_input(
        "Claude API Key (Optional)", 
        value=st.session_state.ai_api_key,
        type="password",
        help="Required for enhanced AI discovery features"
    )
    if ai_api_key != st.session_state.ai_api_key:
        st.session_state.ai_api_key = ai_api_key
        st.session_state.ai_assistant = AIAssistant(api_key=ai_api_key)
    
    # Clean AI status indicator
    ai_status = "✅ Ready" if st.session_state.ai_assistant.is_available() else "⚠️ Limited Mode"
    st.sidebar.caption(f"AI Status: {ai_status}")
    
    # Workflow progress - cleaner format
    st.sidebar.subheader("📊 Progress")
    
    # Check progress
    has_connection = st.session_state.current_connection is not None
    has_recommendations = len(st.session_state.ai_table_recommendations) > 0
    has_encryption_data = st.session_state.get('encryption_preparation_results') is not None
    
    # Clean progress indicators
    progress_items = [
        ("Database", has_connection),
        ("Discovery", has_recommendations), 
        ("Encryption", has_encryption_data),
        ("Results", has_encryption_data)
    ]
    
    for step, completed in progress_items:
        if completed:
            st.sidebar.success(f"✅ {step}")
        else:
            st.sidebar.info(f"⏳ {step}")
    
    # Clean page selection
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Get the index of the current page for the selectbox
    page_options = [
        "Dashboard",
        "1. Connect to Database", 
        "2. AI Discovery", 
        "3. Encryption Preparation",
        "4. Results Display",
        "5. Check Results Table",
        "6. Upload Regulations"
    ]
    
    try:
        current_index = page_options.index(st.session_state.current_page)
    except ValueError:
        current_index = 0
        st.session_state.current_page = "Dashboard"
    
    page = st.sidebar.selectbox(
        "🧭 Navigate:",
        page_options,
        index=current_index
    )
    
    # Only update current_page if the selectbox selection actually changed
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # Route to pages based on current_page in session state
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        show_dashboard()
    elif current_page == "1. Connect to Database":
        show_connect_database()
    elif current_page == "2. AI Discovery":
        show_ai_discovery()
    elif current_page == "3. Encryption Preparation":
        show_encryption_preparation()
    elif current_page == "4. Results Display":
        show_results_display()
    elif current_page == "5. Check Results Table":
        show_check_results_table()
    elif current_page == "6. Upload Regulations":
        show_upload_regulations()

def show_dashboard():
    """Clean and professional dashboard with workflow overview"""
    st.title("🔒 Enhanced PII Detection Prototype")
    st.markdown("Database → AI Discovery → Data Encryption → Results Display")
    
    st.header("🎯 PII Detection and Encryption Dashboard")
    st.markdown("Follow the workflow below:")
    
    # Progress indicator
    has_connection = st.session_state.current_connection is not None
    has_recommendations = len(st.session_state.ai_table_recommendations) > 0
    has_encryption_data = st.session_state.get('encryption_preparation_results') is not None
    
    progress = 0
    if has_connection: progress += 1
    if has_recommendations: progress += 1
    if has_encryption_data: progress += 1
    
    # Clean progress display
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1:
        st.progress(progress / 4.0)
    with progress_col2:
        st.caption(f"Progress: {progress}/4 steps completed")
    
    # Workflow steps - cleaner layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not has_connection:
            st.error("**Step 1: Connect Database** ❌")
            if st.button("🔗 Connect", use_container_width=True):
                st.session_state.current_page = "1. Connect to Database"
                st.rerun()
        else:
            st.success("**Step 1: Connected** ✅")
            st.caption(f"Database: {st.session_state.current_connection}")
    
    with col2:
        if not has_connection:
            st.info("**Step 2: AI Discovery** ⏳")
            st.caption("Requires database")
        elif not has_recommendations:
            st.warning("**Step 2: AI Discovery** 🤖")
            if st.button("🔍 Discover", use_container_width=True):
                st.session_state.current_page = "2. AI Discovery"
                st.rerun()
        else:
            st.success("**Step 2: Discovered** ✅")
            st.caption(f"Tables: {len(st.session_state.ai_table_recommendations)}")
    
    with col3:
        if not has_connection:
            st.info("**Step 3: Encryption Prep** ⏳")
            st.caption("Requires database")
        elif not has_encryption_data:
            st.warning("**Step 3: Encryption Prep** 🛡️")
            if st.button("� Prepare", use_container_width=True):
                st.session_state.current_page = "3. Encryption Preparation"
                st.rerun()
        else:
            st.success("**Step 3: Prepared** ✅")
            st.caption("Encryption ready")
    
    with col4:
        if not has_encryption_data:
            st.info("**Step 4: Results** ⏳")
            st.caption("Requires preparation")
        else:
            st.warning("**Step 4: Results** 📊")
            if st.button("📋 View Results", use_container_width=True):
                st.session_state.current_page = "4. Results Display"
                st.rerun()
    
    # Clean next step recommendation
    st.markdown("---")
    
    # Status summary box
    if not has_connection:
        st.info("👉 **Next Step**: Connect to your database to begin PII detection")
    elif not has_recommendations:
        st.info("👉 **Next Step**: Use AI Discovery to find tables with PII")
    elif not has_encryption_data:
        st.info("👉 **Next Step**: Prepare encryption keys for discovered name columns")
    else:
        st.success("🎉 **Workflow Complete!** You can now view the encryption results.")
        
        # Show quick stats when complete
        if st.session_state.get('encryption_preparation_results'):
            results = st.session_state.encryption_preparation_results
            name_records = len([r for r in results if r.get('Column_Type') == 'NAME'])
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            with stats_col1:
                st.metric("Total Records", f"{len(results):,}")
            with stats_col2:
                st.metric("Name Records", f"{name_records:,}")
            with stats_col3:
                st.metric("Tables Processed", len(st.session_state.ai_table_recommendations))

def show_connect_database():
    """Step 1: Connect to Database - Clean Customer-Friendly UI"""
    # Step 1 Header
    st.header("🔗 Step 1: Connect to Database")
    
    # Filter out Results database for analysis - it's only for storing results later
    analysis_databases = {k: v for k, v in DATABASE_PROFILES.items() if k != 'Results'}
    
    # Select Your Database - Dropdown Section
    st.subheader("🎯 Select Your Database")
    selected_profile = st.selectbox(
        "Choose the database you want to analyze:",
        [""] + list(analysis_databases.keys()),
        help="Select the database to scan for personally identifiable information",
        label_visibility="visible"
    )
    
    # Active Connection Status (when connected)
    if st.session_state.current_connection:
        st.markdown("---")
        st.subheader("✅ Active Connection")
        
        # Clean connection status card
        st.markdown(f"""
        <div style='border: 2px solid #4CAF50; border-radius: 12px; padding: 20px; margin: 16px 0; background: linear-gradient(135deg, #E8F5E8 0%, #F1F8E9 100%); box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1;'>
                    <h3 style='color: #2E7D32; margin: 0 0 8px 0;'>🗄️ {st.session_state.current_connection}</h3>
                    <p style='color: #388E3C; margin: 4px 0; font-size: 14px;'>Connected • Ready for PII Analysis</p>
                </div>
                <div style='text-align: center;'>
                    <div style='background: #4CAF50; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;'>
                        🟢 ONLINE
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Connection management
        with st.expander("⚙️ Connection Management", expanded=False):
            st.warning("**Warning**: Disconnecting will clear all analysis data.")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔌 Disconnect", help="Safely disconnect from database", use_container_width=True):
                    # Clear all connection data
                    st.session_state.current_connection = None
                    st.session_state.ai_table_recommendations = []
                    st.session_state.analysis_results = None
                    if 'encryption_preparation_results' in st.session_state:
                        del st.session_state.encryption_preparation_results
                    st.success("� Successfully disconnected.")
                    st.rerun()
    
    # Connection Section (only show if database is selected but not connected)
    if selected_profile and not st.session_state.current_connection:
        st.markdown("---")
        st.subheader(f"🎯 Ready to Connect: **{selected_profile}**")
        
        # Create a clean, modern connection preview card
        st.markdown(f"""
        <div style='border: 2px solid #1976D2; border-radius: 12px; padding: 20px; margin: 16px 0; background: linear-gradient(135deg, #E3F2FD 0%, #F8FDF8 100%); box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1;'>
                    <h3 style='color: #1565C0; margin: 0 0 8px 0;'>🗄️ {selected_profile}</h3>
                    <p style='color: #424242; margin: 4px 0; font-size: 14px;'>Ready for secure PII analysis</p>
                </div>
                <div style='text-align: center;'>
                    <div style='background: #1976D2; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;'>
                        ✅ Ready
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Connection features in a clean layout
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success("🔒 **Secure**")
            st.caption("Encrypted connection")
        with col2:
            st.info("� **Read-Only**")
            st.caption("Safe analysis mode")
        with col3:
            st.success("⚡ **Optimized**")
            st.caption("High performance")
        
        # Move technical details to collapsed section
        with st.expander("🔧 Technical Connection Details", expanded=False):
            st.markdown("### 🔗 Connection Information")
            col1, col2 = st.columns(2)
            with col1:
                # Enhanced connection experience
                progress_container = st.container()
                with progress_container:
                    st.markdown("### 🔄 Establishing Connection...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate realistic connection steps
                    status_text.text("🔍 Validating database credentials...")
                    time.sleep(0.5)
                    progress_bar.progress(0.2)
                    
                    status_text.text("🔐 Establishing secure tunnel...")
                    time.sleep(0.5)
                    progress_bar.progress(0.5)
                    
                    status_text.text("📊 Verifying database accessibility...")
                    time.sleep(0.5)
                    progress_bar.progress(0.8)
                    
                    status_text.text("✅ Connection established!")
                    progress_bar.progress(1.0)
                    time.sleep(0.5)
                    
                    # Clear the progress and show success
                    progress_container.empty()
                    
                    # Store connection and show success
                    st.session_state.current_connection = selected_profile
                    
                    # Success celebration
                    # st.balloons()
                    st.success(f"🎉 Successfully connected to **{selected_profile}**!")
                    st.success("🔒 Secure connection established for PII analysis")
                    st.info("🚀 **Ready for AI Discovery!** Proceeding to table analysis...")
                    
                    # Auto-navigate to next step
                    time.sleep(1)
                    st.session_state.current_page = "2. AI Discovery"
                    st.rerun()
                    
    # Navigation Buttons
    st.markdown("---")
    st.subheader("🧭 Navigation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Back to Dashboard", use_container_width=True, help="Return to main dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    with col2:
        next_enabled = st.session_state.current_connection is not None
        button_text = "Next: AI Discovery →" if next_enabled else "Connect Database First"
        
        if st.button(
            button_text,
            type="primary" if next_enabled else "secondary",
            disabled=not next_enabled,
            use_container_width=True,
            help="Proceed to AI-powered table discovery" if next_enabled else "Please connect to a database first"
        ):
            st.session_state.current_page = "2. AI Discovery"
            st.rerun()
    
    # Database Detailed Information with Visual Tiles
    st.markdown("---")
    
    # Detailed database information in expandable section
    with st.expander("ℹ️ Detailed Database Information", expanded=False):
        st.subheader("Database Details & Visual Overview")
    
        # Create visual database tiles in a clean grid layout
        cols = st.columns(2)
        db_names = list(analysis_databases.keys())
        
        for i, db_name in enumerate(db_names):
            with cols[i % 2]:
                # Create clean, modern database cards with better colors
                with st.container():
                    if db_name == 'AdventureWorks2019':
                        st.markdown("""
                        <div style='border: 2px solid #1E88E5; border-radius: 12px; padding: 16px; margin: 8px 0; background: linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%);'>
                            <h4 style='color: #1565C0; margin: 0 0 8px 0;'>🏢 AdventureWorks2019</h4>
                            <p style='color: #424242; margin: 4px 0; font-size: 14px;'><strong>Microsoft Sample Database</strong></p>
                            <p style='color: #666; margin: 2px 0; font-size: 13px;'>HR, Sales & Product Data • ~70 tables</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif db_name == 'ECC60jkl_HACK':
                        st.markdown("""
                        <div style='border: 2px solid #FB8C00; border-radius: 12px; padding: 16px; margin: 8px 0; background: linear-gradient(135deg, #FFF3E0 0%, #FCE4EC 100%);'>
                            <h4 style='color: #E65100; margin: 0 0 8px 0;'>🔧 ECC60jkl_HACK</h4>
                            <p style='color: #424242; margin: 4px 0; font-size: 14px;'><strong>SAP ECC System</strong></p>
                            <p style='color: #666; margin: 2px 0; font-size: 13px;'>Enterprise Resource Planning • Complex data</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif db_name == 'Jde920_demo':
                        st.markdown("""
                        <div style='border: 2px solid #8E24AA; border-radius: 12px; padding: 16px; margin: 8px 0; background: linear-gradient(135deg, #F3E5F5 0%, #E8F5E8 100%);'>
                            <h4 style='color: #6A1B9A; margin: 0 0 8px 0;'>⚡ Jde920_demo</h4>
                            <p style='color: #424242; margin: 4px 0; font-size: 14px;'><strong>JD Edwards Demo</strong></p>
                            <p style='color: #666; margin: 2px 0; font-size: 13px;'>ERP Demo Environment • Business apps</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif db_name == 'ORACLE_EBS_HACK':
                        st.markdown("""
                        <div style='border: 2px solid #D32F2F; border-radius: 12px; padding: 16px; margin: 8px 0; background: linear-gradient(135deg, #FFEBEE 0%, #FFF3E0 100%);'>
                            <h4 style='color: #C62828; margin: 0 0 8px 0;'>🏛️ ORACLE_EBS_HACK</h4>
                            <p style='color: #424242; margin: 4px 0; font-size: 14px;'><strong>Oracle E-Business Suite</strong></p>
                            <p style='color: #666; margin: 2px 0; font-size: 13px;'>Enterprise business data • EBS modules</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.markdown(f"""
                        <div style='border: 2px solid #546E7A; border-radius: 12px; padding: 16px; margin: 8px 0; background: linear-gradient(135deg, #ECEFF1 0%, #F5F5F5 100%);'>
                            <h4 style='color: #37474F; margin: 0 0 8px 0;'>🗄️ {db_name}</h4>
                            <p style='color: #424242; margin: 4px 0; font-size: 14px;'><strong>Enterprise Database</strong></p>
                            <p style='color: #666; margin: 2px 0; font-size: 13px;'>Business data • Various structures</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
        st.markdown("### 📋 Complete Database Information")
        for db_name in analysis_databases.keys():
            if db_name == 'AdventureWorks2019':
                st.write(f"**🏢 {db_name}**")
                st.write("- Microsoft's official sample database for SQL Server")
                st.write("- Contains realistic HR, Sales, Manufacturing, and Product data")
                st.write("- Approximately 70 tables with rich PII content")
                st.write("- Best for: Complete PII analysis demonstration")
                st.write("")
            elif db_name == 'ECC60jkl_HACK':
                st.write(f"**🔧 {db_name}**")
                st.write("- SAP ECC (Enterprise Central Component) system database")
                st.write("- Enterprise Resource Planning data structures")
                st.write("- Complex multi-module enterprise data")
                st.write("- Best for: SAP-specific PII analysis and compliance")
                st.write("")
            elif db_name == 'Jde920_demo':
                st.write(f"**⚡ {db_name}**")
                st.write("- JD Edwards EnterpriseOne demo environment")
                st.write("- ERP demonstration data with business applications")
                st.write("- Financial, HR, and operational data structures")
                st.write("- Best for: JDE-specific PII testing scenarios")
                st.write("")
            elif db_name == 'ORACLE_EBS_HACK':
                st.write(f"**🏛️ {db_name}**")
                st.write("- Oracle E-Business Suite database")
                st.write("- Comprehensive enterprise business application data")
                st.write("- Multiple EBS modules and data relationships")
                st.write("- Best for: Oracle EBS PII scanning and analysis")
                st.write("")
        
        st.info("💡 **Note**: All databases are configured for read-only access to ensure safe PII analysis. Results are stored separately in a dedicated Results database.")
    
    # # Enhanced Connection Status Section
    # if st.session_state.current_connection:
    #     st.markdown("---")
    #     st.subheader("� Active Connection")
        
    #     # Beautiful status card
    #     st.markdown(f"""
    #     <div style='border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 10px 0; background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);'>
    #         <div style='display: flex; justify-content: space-between; align-items: center;'>
    #             <div>
    #                 <h4 style='color: #2E7D32; margin: 0;'>✅ Connected to {st.session_state.current_connection}</h4>
    #                 <p style='color: #388E3C; margin: 5px 0;'>Mode: PII Analysis • Status: Active • Security: Encrypted</p>
    #             </div>
    #             <div style='text-align: center;'>
    #                 <div style='background: #4CAF50; color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px;'>
    #                     🟢 ONLINE
    #                 </div>
    #             </div>
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)
        
    #     # Move connection management to collapsed section
    #     with st.expander("⚙️ Connection Management", expanded=False):
    #         st.markdown("### 🔌 Disconnect Options")
    #         st.warning("**Warning**: Disconnecting will clear all analysis data including discovered tables and encryption results.")
            
    #         col1, col2, col3 = st.columns([1, 1, 1])
    #         with col2:
    #             if st.button("🔌 Disconnect Database", help="Safely disconnect from current database", use_container_width=True):
    #                 # Clear all connection data
    #                 st.session_state.current_connection = None
    #                 st.session_state.ai_table_recommendations = []
    #                 st.session_state.analysis_results = None
    #                 if 'encryption_preparation_results' in st.session_state:
    #                     del st.session_state.encryption_preparation_results
                    
    #                 st.success("🔌 Successfully disconnected from database.")
    #                 st.info("All analysis data has been cleared for security.")
    #                 time.sleep(1)
    #                 st.rerun()
    
    # # Clean Navigation
    # st.markdown("---")
    # st.markdown("### 🧭 Navigation")
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("🏠 Back to Dashboard", use_container_width=True, help="Return to main dashboard"):
    #         st.session_state.current_page = "Dashboard"
    #         st.rerun()
    # with col2:
    #     next_enabled = st.session_state.current_connection is not None
    #     button_text = "Next: AI Discovery →" if next_enabled else "Connect Database First"
        
    #     if st.button(
    #         button_text,
    #         type="primary" if next_enabled else "secondary",
    #         disabled=not next_enabled,
    #         use_container_width=True,
    #         help="Proceed to AI-powered table discovery" if next_enabled else "Please connect to a database first"
    #     ):
    #         st.session_state.current_page = "2. AI Discovery"
    #         st.rerun()

def show_ai_discovery():
    """Step 2: AI Discovery"""
    st.header("🤖 Step 2: AI Discovery")
    st.markdown("AI analyzes database schema, table names, column names, and sample data to identify PII-likely tables and columns")
    
    if not st.session_state.current_connection:
        st.error("❌ No database connected. Please go back to Step 1.")
        if st.button("← Go to Step 1"):
            st.session_state.current_page = "1. Connect to Database"
            st.rerun()
        return
    
    # Show current analysis target
    database_name = st.session_state.current_connection
    st.success(f"🎯 **Target Database:** {database_name}")
    
    # Check AI availability
    ai_available = st.session_state.ai_assistant.is_available()
    # if ai_available:
    #     st.success("🤖 **AI Assistant:** Available for intelligent analysis")
    #     st.info("🔍 **Analysis Method:** Claude AI-powered schema analysis + sample data inspection")
    # else:
    #     st.warning("🤖 **AI Assistant:** Not available - using rule-based analysis")
    #     st.info("🔍 **Analysis Method:** Rule-based pattern matching for PII detection")
    
    # Discovery configuration
    st.subheader("🔧 Discovery Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        confidence_threshold = st.slider("Minimum confidence threshold:", 0.0, 1.0, 0.6, 0.1)
        max_tables_to_analyze = st.slider("Max tables to analyze:", 10, 100, 50, 5, 
                                         help="Limit the number of tables to analyze for better performance")
    
    with col2:
        include_system_tables = st.checkbox("Include system/metadata tables", value=False)
        analyze_column_data = st.checkbox("Analyze column sample data", value=True)
    
    if st.button("🔍 Start AI Table & Column Discovery", type="primary"):
        with st.spinner(f"AI analyzing {database_name} schema and sample data..."):
            progress_bar = st.progress(0)
            
            try:
                # Step 1: Connect to database and get connection ID
                # st.write("🔄 Step 1: Establishing database connection...")
                progress_bar.progress(0.1)
                
                connection_id = st.session_state.db_manager.connect_to_database(database_name)
                time.sleep(0.5)
                
                # Step 2: Get tables from database
                # st.write("🔄 Step 2: Scanning database schema...")
                progress_bar.progress(0.3)
                
                tables_info = st.session_state.db_manager.get_tables(connection_id)
                
                # Database-specific table prioritization for ECC60jkl_HACK (SAP ECC)
                if database_name == "ECC60jkl_HACK":
                    priority_tables = []
                    other_tables = []
                    
                    for table in tables_info:
                        table_name = table.get('table', table.get('name', '')).upper()
                        schema_name = table.get('schema', '').lower()
                        
                        # Prioritize dbo.KNA1 (Customer Master) and dbo.P* tables (Personnel/HR tables in SAP)
                        if schema_name == 'dbo' and (table_name == 'KNA1' or table_name.startswith('P')):
                            priority_tables.append(table)
                        else:
                            other_tables.append(table)
                    
                    # Combine priority tables first, then others
                    tables_info = priority_tables + other_tables
                    
                    # if priority_tables:
                    #     st.info(f"🎯 **SAP ECC Analysis**: Prioritizing {len(priority_tables)} key tables (dbo.KNA1 + dbo.P* tables) for PII detection")
                    #     st.write("**Priority tables:**")
                    #     for table in priority_tables[:10]:  # Show first 10 priority tables
                    #         schema = table.get('schema', 'unknown')
                    #         name = table.get('table', table.get('name', 'unknown'))
                    #         st.write(f"  • {schema}.{name}")
                    #     if len(priority_tables) > 10:
                    #         st.write(f"  ... and {len(priority_tables) - 10} more priority tables")
                
                # Limit the number of tables to analyze based on user configuration
                original_table_count = len(tables_info)
                if len(tables_info) > max_tables_to_analyze:
                    tables_info = tables_info[:max_tables_to_analyze]
                    st.info(f"📋 Limited analysis to first {max_tables_to_analyze} tables (out of {original_table_count} total)")
                else:
                    st.write(f"📋 Found {len(tables_info)} tables to analyze")
                
                # DEBUG: Show what tables we found (first few)
                # if len(tables_info) > 0:
                #     st.write("**Sample tables found:**")
                #     for i, table in enumerate(tables_info[:10]):
                #         schema = table.get('schema', 'unknown')
                #         name = table.get('table', table.get('name', 'unknown'))
                #         st.write(f"  - {schema}.{name}")
                #         if i >= 9 and len(tables_info) > 10:
                #             st.write(f"  ... and {len(tables_info) - 10} more tables")
                #             break
                
                time.sleep(0.5)
                
                # Step 3: Get detailed table information
                # st.write("🔄 Step 3: Analyzing table structures and columns...")
                progress_bar.progress(0.5)
                
                detailed_tables = []
                skipped_tables = []
                
                for table_info in tables_info:  # ANALYZE ALL TABLES - no limit!
                    table_name = table_info.get('table', table_info.get('name', ''))
                    schema_name = table_info.get('schema', database_name)
                    
                    # ENHANCED: Skip tables that start with 'dbo' - these are typically system/utility tables
                    # But log them so we can see what we're skipping
                    # if schema_name.lower() == 'dbo':
                    #     skipped_tables.append(f"{schema_name}.{table_name}")
                    #     st.session_state.logger.info(f"Skipping dbo table: {schema_name}.{table_name}")
                    #     continue
                    
                    # Get column information
                    try:
                        columns = st.session_state.db_manager.get_table_columns(connection_id, schema_name, table_name)
                        row_count = st.session_state.db_manager.get_table_row_count(connection_id, schema_name, table_name)
                        
                        detailed_table = {
                            'table': table_name,
                            'schema': schema_name,
                            'columns': columns,
                            'row_count': row_count
                        }
                        detailed_tables.append(detailed_table)
                        
                    except Exception as e:
                        st.session_state.logger.warning(f"Could not get details for table {table_name}: {e}")
                        continue
                
                time.sleep(0.5)
                
                # Step 4: Sample data analysis (if enabled) - ASYNC VERSION
                if analyze_column_data:
                    # st.write("� Step 4: Concurrent table sampling for PII patterns...")
                    progress_bar.progress(0.7)
                    
                    # **NEW ASYNC APPROACH: Sample all tables concurrently**
                    tables_to_sample = [
                        {'schema': table['schema'], 'table': table['table']} 
                        for table in detailed_tables
                    ]
                    
                    # Use async concurrent sampling for much better performance
                    start_time = time.time()
                    sample_results = st.session_state.db_manager.sample_multiple_tables_sync(
                        connection_id, 
                        tables_to_sample, 
                        limit=10  # Optimized sample size
                    )
                    end_time = time.time()
                    
                    # st.success(f"✅ Sampled {len(tables_to_sample)} tables concurrently in {end_time - start_time:.2f} seconds!")
                    
                    # Map async results back to detailed_tables
                    for table in detailed_tables:
                        table_key = f"{table['schema']}.{table['table']}"
                        if table_key in sample_results:
                            df = sample_results[table_key]
                            if not df.empty and 'Error' not in df.columns:
                                # Convert DataFrame to list of dicts for compatibility
                                table['sample_data'] = df.to_dict('records')
                                st.session_state.logger.info(f"✅ Sampled {len(df)} rows from {table_key}")
                            else:
                                table['sample_data'] = None
                                st.session_state.logger.warning(f"⚠️ No valid data from {table_key}")
                        else:
                            table['sample_data'] = None
                            st.session_state.logger.warning(f"⚠️ No results for {table_key}")
                    
                    time.sleep(0.2)  # Reduced wait time since we're much faster now
                
                # Step 5: AI Analysis
                st.write("🔄 AI analysis and recommendations...")
                progress_bar.progress(0.9)
                
                # Use AI assistant to analyze tables
                if ai_available:
                    try:
                        # Use async AI analysis
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        ai_recommendations = loop.run_until_complete(
                            st.session_state.ai_assistant.analyze_tables_for_pii(detailed_tables)
                        )
                        loop.close()
                        
                        # Convert AI recommendations to our format
                        formatted_recommendations = []
                        for ai_rec in ai_recommendations:
                            # Get the table details for additional info
                            table_details = next((t for t in detailed_tables if t['table'] == ai_rec.table_name), {})
                            
                            formatted_rec = {
                                "table_name": ai_rec.table_name,
                                "schema": table_details.get('schema', ai_rec.schema or database_name),
                                "priority": ai_rec.priority,
                                "confidence": ai_rec.confidence_score,
                                "reason": ai_rec.reasoning,
                                "pii_columns": []
                            }
                            
                            # Create PII columns info from AI estimated types and actual columns
                            if table_details.get('columns'):
                                # Get actual column names for this table
                                actual_columns = [col.get('column_name', col.get('name', '')) for col in table_details['columns']]
                                
                                # For each estimated PII type, try to find matching columns
                                for pii_type in ai_rec.estimated_pii_types:
                                    # Find columns that match this PII type
                                    matching_columns = find_columns_for_pii_type(actual_columns, pii_type)
                                    
                                    if matching_columns:
                                        # Add each matching column
                                        for col_name in matching_columns:
                                            sample = get_sample_data_for_column(col_name, pii_type, table_details.get('sample_data'))
                                            formatted_rec["pii_columns"].append({
                                                "column": col_name,
                                                "type": pii_type,
                                                "confidence": min(ai_rec.confidence_score + 0.1, 1.0),
                                                "sample": sample
                                            })
                                    else:
                                        # If no exact match, try a more flexible approach
                                        for col in table_details['columns']:
                                            col_name = col.get('column_name', col.get('name', ''))
                                            if should_column_match_pii_type(col_name.lower(), pii_type):
                                                sample = get_sample_data_for_column(col_name, pii_type, table_details.get('sample_data'))
                                                formatted_rec["pii_columns"].append({
                                                    "column": col_name,
                                                    "type": pii_type,
                                                    "confidence": min(ai_rec.confidence_score + 0.1, 1.0),
                                                    "sample": sample
                                                })
                                                break  # Only add one column per PII type to avoid duplicates
                            
                            # If we still don't have any columns, add generic ones based on PII types
                            if not formatted_rec["pii_columns"] and ai_rec.estimated_pii_types:
                                for pii_type in ai_rec.estimated_pii_types:
                                    formatted_rec["pii_columns"].append({
                                        "column": f"suspected_{pii_type.lower()}_column",
                                        "type": pii_type,
                                        "confidence": ai_rec.confidence_score,
                                        "sample": get_sample_data_for_column(f"suspected_{pii_type.lower()}", pii_type, None)
                                    })
                            
                            formatted_recommendations.append(formatted_rec)
                        
                    except Exception as e:
                        st.warning(f"AI analysis failed, using fallback: {str(e)}")
                        # Fall back to rule-based analysis
                        ai_recommendations = st.session_state.ai_assistant._fallback_table_analysis(detailed_tables)
                        formatted_recommendations = convert_ai_recommendations_to_format(ai_recommendations, database_name)
                
                else:
                    # Use fallback rule-based analysis
                    ai_recommendations = st.session_state.ai_assistant._fallback_table_analysis(detailed_tables)
                    formatted_recommendations = convert_ai_recommendations_to_format(ai_recommendations, database_name)
                
                progress_bar.progress(1.0)
                time.sleep(0.5)
                
                # Filter by confidence threshold
                filtered_recommendations = [r for r in formatted_recommendations if r["confidence"] >= confidence_threshold]
                
                st.session_state.ai_table_recommendations = filtered_recommendations
                st.success(f"✅ AI Analysis complete! Found {len(filtered_recommendations)} tables with potential personal information (threshold: {confidence_threshold})")
                
                if len(formatted_recommendations) > len(filtered_recommendations):
                    st.info(f"💡 {len(formatted_recommendations) - len(filtered_recommendations)} additional tables found below confidence threshold")
                
            except Exception as e:
                st.error(f"❌ Discovery failed: {str(e)}")
                st.error("🔧 Please check your database connection and try again")
                return
    
    # Show detailed recommendations
    if st.session_state.ai_table_recommendations:
        st.subheader("🎯 AI Discovery Results")
        
        # Summary metrics
        high_priority = [r for r in st.session_state.ai_table_recommendations if r["priority"] == "HIGH"]
        medium_priority = [r for r in st.session_state.ai_table_recommendations if r["priority"] == "MEDIUM"]
        low_priority = [r for r in st.session_state.ai_table_recommendations if r["priority"] == "LOW"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 High Priority", len(high_priority))
        with col2:
            st.metric("🟡 Medium Priority", len(medium_priority))
        with col3:
            st.metric("🟢 Low Priority", len(low_priority))
        with col4:
            st.metric("📊 Total Tables", len(st.session_state.ai_table_recommendations))
        
        # Detailed recommendations with columns
        with st.expander("🔍 View Detailed Recommendations", expanded=False):    
            st.subheader("📋 Detailed Table & Column Analysis")
        
            # Create tabs for different priorities
            tab1, tab2, tab3 = st.tabs([
                f"🔴 High Priority ({len(high_priority)})",
                f"🟡 Medium Priority ({len(medium_priority)})", 
                f"🟢 Low Priority ({len(low_priority)})"
            ])
        
            with tab1:
                display_priority_recommendations(high_priority, database_name, "HIGH")
            
            with tab2:
                display_priority_recommendations(medium_priority, database_name, "MEDIUM")
                
            with tab3:
                display_priority_recommendations(low_priority, database_name, "LOW")
    
    # Navigation section for AI Discovery  
    if st.session_state.ai_table_recommendations:
        st.markdown("---")
        st.subheader("🚀 Ready for Encryption")
        
        selected_tables = [rec for rec in st.session_state.ai_table_recommendations 
                          if rec["priority"] in ["HIGH", "MEDIUM"]]
        
        st.info(f"📊 **{len(selected_tables)} high/medium priority tables** are pre-selected for the next step")
        st.success("✅ **Discovery Complete!** Proceed to analyze the selected tables.")
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back: Connect Database"):
            st.session_state.current_page = "1. Connect to Database"
            st.rerun()
    with col2:
        if st.button("Next: Encryption Preparation →", type="primary", disabled=not st.session_state.ai_table_recommendations):
            st.session_state.current_page = "3. Encryption Preparation"
            st.rerun()

def should_column_match_pii_type(column_name: str, pii_type: str) -> bool:
    """Check if a column name should match a specific PII type"""
    pii_patterns = {
        # CRITICAL: Enhanced name patterns - these need 100% encryption priority
        'FULL_NAME': ['name', 'full_name', 'fullname', 'person_name', 'personname', 'customer_name', 
                     'employee_name', 'user_name', 'display_name', 'legal_name', 'party_name'],
        'FIRST_NAME': ['first_name', 'firstname', 'fname', 'given_name', 'givenname', 'forename'],
        'LAST_NAME': ['last_name', 'lastname', 'lname', 'surname', 'family_name', 'familyname'],
        'PERSONAL_NAME': ['name', 'person', 'customer_name', 'user_name', 'personname', 'party_name'],
        
        # Other high-priority PII
        'EMAIL': ['email', 'mail', 'e_mail', 'electronic_mail', 'email_address', 'emailaddress'],
        'PHONE': ['phone', 'telephone', 'mobile', 'cell', 'tel', 'phone_number', 'contact_number'],
        'ADDRESS': ['address', 'addr', 'street', 'location', 'home_address', 'mailing_address'],
        'SSN': ['ssn', 'social_security', 'national_id', 'tax_id', 'social_security_number'],
        'DATE_OF_BIRTH': ['birth_date', 'birthdate', 'dob', 'date_of_birth', 'birth'],
        'NATIONAL_ID': ['national_id', 'id_number', 'employee_id', 'person_id', 'personnel_number'],
        'LOGIN_ID': ['login', 'username', 'user_id', 'login_id', 'userid', 'account_name'],
        'ACCOUNT_NUMBER': ['account', 'account_number', 'acct_no', 'account_no'],
        'POSTAL_CODE': ['postal', 'zip', 'postcode', 'zip_code', 'postal_code'],
        'CITY': ['city', 'town', 'municipality', 'locality'],
        'PERSONNEL_NUMBER': ['personnel', 'employee_number', 'emp_no', 'staff_number'],
        'PARTY_NUMBER': ['party_number', 'party_no', 'trading_no', 'party_id']
    }
    
    patterns = pii_patterns.get(pii_type, [])
    
    # Enhanced matching: exact match OR contains pattern
    column_lower = column_name.lower()
    return any(pattern == column_lower or pattern in column_lower for pattern in patterns)

def get_sample_data_for_column(column_name: str, pii_type: str, sample_data: any) -> str:
    """Generate or extract sample data for a column based on PII type"""
    # If we have actual sample data, try to use it (but mask it for privacy)
    if sample_data and isinstance(sample_data, (list, tuple)) and len(sample_data) > 0:
        try:
            # Get first few non-null values and mask them
            samples = []
            for row in sample_data[:3]:
                if isinstance(row, dict) and column_name in row:
                    value = str(row[column_name])[:10]  # Limit length
                    if value and value.lower() not in ['null', 'none', '']:
                        # Mask the value for privacy
                        if len(value) > 3:
                            masked = value[:2] + '*' * (len(value) - 4) + value[-2:]
                        else:
                            masked = '*' * len(value)
                        samples.append(masked)
            
            if samples:
                return ', '.join(samples)
        except:
            pass
    
    # Fallback to generated sample data based on PII type
    sample_patterns = {
        'EMAIL': 'john***@company.com, mary***@demo.org',
        'FULL_NAME': 'John***Smith, Mary***Johnson', 
        'FIRST_NAME': 'John, Mary, Robert',
        'LAST_NAME': 'Sm***, Joh***son, Br***',
        'PHONE': '555-***-1234, 555-***-5678',
        'ADDRESS': '123 Main St***, 456 Oak Ave***',
        'SSN': '***-**-1234, ***-**-5678',
        'DATE_OF_BIRTH': '1985-**-**, 1990-**-**',
        'PERSONAL_NAME': 'John S***, Mary J***',
        'NATIONAL_ID': '29584***4, 50964***4',
        'LOGIN_ID': 'jsmith***, mjohn***',
        'ACCOUNT_NUMBER': 'ACC***001, ACC***002',
        'POSTAL_CODE': '980**, 981**, 982**',
        'CITY': 'Seattle, Denver, Austin',
        'PERSONNEL_NUMBER': '0000***1, 0000***2',
        'PARTY_NAME': 'ABC Corp***, XYZ Ltd***',
        'PARTY_NUMBER': 'PARTY-***1, PARTY-***2'
    }
    
    return sample_patterns.get(pii_type, f'sample_{pii_type.lower()}_data')

def convert_ai_recommendations_to_format(ai_recommendations, database_name: str) -> list:
    """Convert AI assistant recommendations to our display format with REAL column names"""
    formatted_recommendations = []
    
    # Get database manager for schema lookup
    if hasattr(st.session_state, 'db_manager') and st.session_state.db_manager:
        db_manager = st.session_state.db_manager
        connection_id = db_manager.connect_to_database(database_name)
    else:
        db_manager = None
        connection_id = None
    
    for ai_rec in ai_recommendations:
        # Use the actual schema from the AI recommendation, fallback to database_name
        actual_schema = ai_rec.schema if hasattr(ai_rec, 'schema') and ai_rec.schema else database_name
        
        formatted_rec = {
            "table_name": ai_rec.table_name,
            "schema": actual_schema,
            "priority": ai_rec.priority,
            "confidence": ai_rec.confidence_score,
            "reason": ai_rec.reasoning,
            "pii_columns": []
        }
        
        # Get REAL column names for this table using the proper schema
        real_columns = []
        if db_manager and connection_id:
            try:
                table_columns = db_manager.get_table_columns(connection_id, actual_schema, ai_rec.table_name)
                # Fix: Use correct column field name from database manager
                real_columns = [col.get('column', '') for col in table_columns]
            except Exception as e:
                st.warning(f"Could not get columns for {actual_schema}.{ai_rec.table_name}: {str(e)}")
        
        # Map estimated PII types to REAL column names using enhanced matching
        for pii_type in ai_rec.estimated_pii_types:
            # Find matching real columns for this PII type using our comprehensive patterns
            matching_columns = find_columns_for_pii_type(real_columns, pii_type)
            
            if matching_columns:
                # Add all matching columns with the correct PII type
                for col_name in matching_columns:
                    # Avoid duplicates - check if column already added with different type
                    existing_column = next((pii_col for pii_col in formatted_rec["pii_columns"] 
                                          if pii_col["column"] == col_name), None)
                    if not existing_column:
                        formatted_rec["pii_columns"].append({
                            "column": col_name,  # REAL column name from database
                            "type": pii_type,
                            "confidence": ai_rec.confidence_score,
                            "sample": get_sample_data_for_column(col_name, pii_type, None)
                        })
        
        # If no columns found through pattern matching, don't add placeholders - let pattern-based fallback handle it
        # This prevents the "suspected_" column issue that causes matching failures
        
        formatted_recommendations.append(formatted_rec)
    
    return formatted_recommendations

def find_columns_for_pii_type(column_names: List[str], pii_type: str) -> List[str]:
    """Find actual column names that match a PII type"""
    matching_columns = []
    
    # PII type to column name patterns mapping - ENHANCED for comprehensive detection
    pii_patterns = {
        # CRITICAL: Name columns - highest priority for encryption
        'FULL_NAME': ['name', 'fullname', 'full_name', 'person_name', 'personname', 'customer_name',
                     'employee_name', 'user_name', 'display_name', 'legal_name', 'party_name',
                     'trading_name', 'business_name', 'company_name'],
        'FIRST_NAME': ['firstname', 'first_name', 'fname', 'given_name', 'givenname', 'forename', 'name_first'],
        'LAST_NAME': ['lastname', 'last_name', 'lname', 'surname', 'family_name', 'familyname', 'name_last'],
        'MIDDLE_NAME': ['middlename', 'middle_name', 'mname', 'middle', 'secondname', 'second_name'],
        'PERSONAL_NAME': ['name', 'person', 'customer_name', 'user_name', 'personname', 'party_name',
                         'contact_name', 'individual_name'],
        'PERSONAL_TITLE': ['title', 'name_title', 'prefix', 'suffix', 'honorific'],
        'REVIEWER_NAME': ['reviewername', 'reviewer_name', 'reviewer', 'name'],
        'VENDOR_NAME': ['name', 'vendor_name', 'vendorname', 'supplier_name'],
        'STORE_NAME': ['name', 'store_name', 'storename', 'shop_name'],
                         
        # Contact information
        'EMAIL': ['email', 'emailaddress', 'email_address', 'mail', 'e_mail', 'electronic_mail', 'contact_email'],
        'EMAIL_ADDRESS': ['emailaddress', 'email_address', 'email', 'mail', 'e_mail'],
        'PHONE': ['phone', 'telephone', 'mobile', 'cell', 'contact', 'phonenumber', 'phone_number', 'tel'],
        'PHONE_NUMBER': ['phonenumber', 'phone_number', 'phone', 'telephone', 'mobile', 'cell'],
        
        # Address information
        'ADDRESS': ['address', 'street', 'location', 'home_address', 'mailing_address', 'street_address', 'addr'],
        'STREET_ADDRESS': ['addressline1', 'address_line1', 'street', 'street_address', 'address'],
        'CITY': ['city', 'town', 'municipality', 'locality'],
        'POSTAL_CODE': ['postalcode', 'postal_code', 'zip', 'zipcode', 'zip_code', 'postcode'],
        'GEOGRAPHIC_LOCATION': ['city', 'state', 'province', 'location', 'geography'],
        
        # Personal information
        'DATE_OF_BIRTH': ['birthdate', 'birth_date', 'dob', 'date_of_birth', 'birth', 'born'],
        'SSN': ['ssn', 'social', 'social_security', 'social_security_number'],
        'NATIONAL_ID': ['nationalidnumber', 'national_id', 'id_number', 'employee_id', 'person_id'],
        'LOGIN_ID': ['loginid', 'login_id', 'user', 'login', 'username', 'userid', 'user_id', 'account'],
        'ACCOUNT_NUMBER': ['account', 'account_number', 'acct_no', 'account_no', 'accountnumber'],
        
        # Financial information
        'CREDIT_CARD': ['creditcard', 'credit_card', 'card', 'payment', 'cc', 'card_number'],
        'CREDIT_CARD_NUMBER': ['cardnumber', 'card_number', 'creditcardnumber', 'credit_card_number'],
        'CARD_TYPE': ['cardtype', 'card_type', 'type'],
        'EXPIRATION_DATE': ['expiry', 'exp_date', 'expiration', 'expiration_date'],
        
        # Work-related
        'JOB_TITLE': ['title', 'job_title', 'jobtitle', 'position', 'role'],
        'SALARY_RATE': ['salary', 'rate', 'pay', 'wage', 'compensation'],
        'PAY_FREQUENCY': ['frequency', 'pay_frequency', 'payfrequency'],
        
        # Security
        'PASSWORD': ['password', 'pwd', 'pass', 'passwd', 'secret', 'pin'],
        'PASSWORD_HASH': ['passwordhash', 'password_hash', 'hash'],
        'PASSWORD_SALT': ['passwordsalt', 'password_salt', 'salt'],
        
        # Demographics
        'GENDER': ['gender', 'sex'],
        'MARITAL_STATUS': ['marital', 'maritalstatus', 'marital_status'],
        'DEMOGRAPHICS': ['demographics', 'demographic'],
        'BUSINESS_DEMOGRAPHICS': ['demographics', 'demographic', 'business_demographics'],
        
        # Comments and text
        'PERSONAL_COMMENTS': ['comment', 'comments', 'notes', 'remarks', 'description'],
        'RESUME_DATA': ['resume', 'cv', 'curriculum'],
        'WORK_HISTORY': ['history', 'employment', 'experience'],
        'PERSONAL_INFORMATION': ['info', 'information', 'details', 'data'],
        
        # Associations and relationships
        'BUSINESS_RELATIONSHIP': ['relationship', 'association', 'contact'],
        'CONTACT_ASSOCIATION': ['contact', 'association', 'relationship'],
        'ADDRESS_ASSOCIATION': ['address', 'location', 'association'],
        'LOCATION_RELATIONSHIP': ['location', 'address', 'relationship'],
        'FINANCIAL_ASSOCIATION': ['financial', 'payment', 'credit'],
        'PAYMENT_RELATIONSHIP': ['payment', 'financial', 'credit'],
        'CUSTOMER_ACCOUNT': ['customer', 'account'],
        'PERSON_ASSOCIATION': ['person', 'individual', 'contact'],
        'CUSTOMER_ASSOCIATION': ['customer', 'client'],
        'PURCHASE_BEHAVIOR': ['purchase', 'order', 'sales'],
        'EMPLOYMENT_HISTORY': ['employment', 'history', 'career'],
        'CAREER_PROGRESSION': ['career', 'progression', 'history'],
        'SALES_PERFORMANCE': ['sales', 'performance'],
        'COMPENSATION_DATA': ['compensation', 'salary', 'pay']
    }
    
    patterns = pii_patterns.get(pii_type, [pii_type.lower().replace('_', '')])
    
    for col_name in column_names:
        col_lower = col_name.lower()
        for pattern in patterns:
            # Enhanced matching: exact match OR contains pattern
            if pattern == col_lower or pattern in col_lower:
                matching_columns.append(col_name)
                break
    
    return matching_columns

def display_priority_recommendations(recommendations, database_name, priority_level):
    """Display recommendations for a specific priority level with detailed column info"""
    if not recommendations:
        st.info(f"No {priority_level.lower()} priority tables found.")
        return
    
    for i, rec in enumerate(recommendations):
        # Use actual schema.table format instead of database.table
        schema_name = rec.get('schema', database_name)
        full_table_name = f"{schema_name}.{rec['table_name']}"
        
        with st.expander(f"📊 {full_table_name} (Confidence: {rec['confidence']:.2f})", expanded=True):
            
            # Table summary
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**📋 Table**: `{full_table_name}`")
                st.write(f"**🎯 Priority**: {rec['priority']}")
                st.write(f"**💡 Reason**: {rec['reason']}")
            
            with col2:
                st.metric("Confidence", f"{rec['confidence']:.2f}")
                st.metric("PII Columns", len(rec['pii_columns']))
            
            # PII Columns details
            st.write("**🔍 Detected PII Columns:**")
            
            # Check if this table has name columns (critical)
            name_columns = [col for col in rec['pii_columns'] 
                          if any(name_type in col['type'] for name_type in ["FULL_NAME", "FIRST_NAME", "LAST_NAME", "PERSONAL_NAME"])]
            
            if name_columns:
                st.warning(f"🚨 **CRITICAL**: This table contains {len(name_columns)} NAME column(s) requiring immediate encryption!")
            
            for col_info in rec['pii_columns']:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 3])
                
                with col1:
                    # Highlight name columns with special formatting
                    if any(name_type in col_info['type'] for name_type in ["FULL_NAME", "FIRST_NAME", "LAST_NAME", "PERSONAL_NAME"]):
                        st.write(f"🚨 **`{col_info['column']}`** (NAME)")
                    else:
                        st.write(f"📄 `{col_info['column']}`")
                
                with col2:
                    pii_type_color = get_pii_type_color(col_info['type'])
                    st.write(f"{pii_type_color} {col_info['type']}")
                
                with col3:
                    confidence_color = "🟢" if col_info['confidence'] > 0.9 else "🟡" if col_info['confidence'] > 0.7 else "🔴"
                    st.write(f"{confidence_color} {col_info['confidence']:.2f}")
                
                with col4:
                    st.write(f"💾 Sample: `{col_info['sample']}`")
            
            # Selection for analysis
            st.write("**⚙️ Analysis Selection:**")
            select_table = st.checkbox(
                f"Include {rec['table_name']} in PII analysis", 
                value=(priority_level in ["HIGH", "MEDIUM"]),
                key=f"select_{rec['table_name']}_{i}"
            )
            
            if select_table:
                st.success(f"✅ {rec['table_name']} will be included in PII analysis")
            else:
                st.info(f"⏭️ {rec['table_name']} will be skipped")

def get_pii_type_color(pii_type):
    """Get color emoji for PII type"""
    # CRITICAL: Name columns get special red alert status
    critical_name_types = ["FULL_NAME", "FIRST_NAME", "LAST_NAME", "PERSONAL_NAME"]
    high_risk = ["EMAIL", "SSN", "DATE_OF_BIRTH", "NATIONAL_ID", "PHONE", "CREDIT_CARD"]
    medium_risk = ["ADDRESS", "LOGIN_ID", "ACCOUNT_NUMBER", "POSTAL_CODE"]
    
    if any(name_type in pii_type for name_type in critical_name_types):
        return "🔴🚨"  # Double red alert for name columns
    elif any(risk in pii_type for risk in high_risk):
        return "🔴"
    elif any(risk in pii_type for risk in medium_risk):
        return "🟡"
    else:
        return "🟢"
    
    # Navigation section for AI Discovery
    if st.session_state.ai_table_recommendations:
        st.markdown("---")
        st.subheader("🚀 Ready for PII Analysis")
        
        selected_tables = [rec for rec in st.session_state.ai_table_recommendations 
                          if rec["priority"] in ["HIGH", "MEDIUM"]]
        
        st.info(f"📊 **{len(selected_tables)} high/medium priority tables** are pre-selected for PII analysis")
        st.success("✅ **Discovery Complete!** Proceed to analyze the selected tables for PII.")
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back: Connect Database"):
            st.session_state.current_page = "1. Connect to Database"
            st.rerun()
    with col2:
        if st.button("Next: Encryption Preparation →", type="primary", disabled=not st.session_state.ai_table_recommendations):
            st.session_state.current_page = "3. Encryption Preparation"
            st.rerun()

def show_encryption_preparation():
    """Step 3: Encryption Preparation - Scan all rows and create encryption keys"""
    st.header("🔐 Step 3: Encryption Preparation")
    st.markdown("Scanning ALL rows from discovered tables and creating encryption keys for name-related data")
    
    # Check if we have discovery results
    if 'ai_table_recommendations' not in st.session_state or not st.session_state.ai_table_recommendations:
        st.warning("⚠️ Please complete the AI Discovery phase first.")
        if st.button("← Go to AI Discovery"):
            st.session_state.current_page = "2. AI Discovery"
            st.rerun()
        return
    
    # Show current analysis target
    database_name = st.session_state.current_connection
    st.success(f"🎯 **Target Database:** {database_name}")
    
    # Show discovered tables summary
    name_priority_tables = [t for t in st.session_state.ai_table_recommendations if 'name' in str(t.get('reason', '')).lower()]
    st.info(f"📊 **Discovered Tables:** {len(st.session_state.ai_table_recommendations)} total, {len(name_priority_tables)} with name columns")
    
    # Configuration
    st.subheader("⚙️ Encryption Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        include_all_tables = st.checkbox("Include all discovered tables", value=True, help="Scan all tables found by AI Discovery")
        # batch_size = st.selectbox("Batch size for processing:", [100, 500, 1000, 5000], index=2, help="Number of rows to process at once")
    
    with col2:
        focus_name_columns = st.checkbox("Focus on name columns only", value=True, help="Only process columns containing names")
        generate_keys = st.checkbox("Generate encryption keys", value=True, help="Create unique encryption keys for each value")
    
    # Show what will be processed
    tables_to_process = st.session_state.ai_table_recommendations if include_all_tables else name_priority_tables
    
    with st.expander(f"📋 Tables to be processed ({len(tables_to_process)} tables)", expanded=False):
        for table in tables_to_process:
            schema = table.get('schema', database_name)
            table_name = table['table_name']
            pii_columns = len(table.get('pii_columns', []))
            st.write(f"• **{schema}.{table_name}** - {pii_columns} columns - Priority: {table.get('priority', 'MEDIUM')}")
    
    if st.button("🚀 Start Full Database Scan & Encryption Preparation", type="primary"):
        with st.spinner("🔍 Scanning ALL rows from discovered tables and generating encryption keys..."):
            
            # Initialize results storage
            if 'encryption_preparation_results' not in st.session_state:
                st.session_state.encryption_preparation_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Get database connection
                db_manager = st.session_state.db_manager
                connection_id = db_manager.connect_to_database(database_name)
                
                total_tables = len(tables_to_process)
                encryption_data = []
                total_rows_processed = 0
                
                # Import required libraries for efficient processing
                import pandas as pd
                import hashlib
                import secrets
                import base64
                import time
                from cryptography.fernet import Fernet
                
                def generate_encryption_key(value: str) -> str:
                    """Generate a unique encryption key for a specific value - FAST VERSION"""
                    try:
                        if pd.isna(value) or str(value).strip() == '':
                            return ""
                        # Fast hash-based key generation (instead of slow PBKDF2)
                        key_hash = hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:32]
                        return f"ENC_{key_hash}"
                    except:
                        return "KEY_GENERATION_FAILED"
                
                def get_primary_key_columns(connection_id: str, schema: str, table: str) -> List[str]:
                    """Get primary key columns for a table"""
                    try:
                        cursor = db_manager.connections[connection_id]['connection'].cursor()
                        cursor.execute(f"""
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? 
                        AND CONSTRAINT_NAME LIKE 'PK_%'
                        ORDER BY ORDINAL_POSITION
                        """, (schema, table))
                        
                        pk_columns = [row[0] for row in cursor.fetchall()]
                        cursor.close()
                        
                        # If no primary key found, try to find the first column that looks like an ID
                        if not pk_columns:
                            all_columns = db_manager.get_table_columns(connection_id, schema, table)
                            for col in all_columns:
                                col_name = col.get('column', '')
                                if col_name.lower().endswith('id') or col_name.lower() in ['id', 'key']:
                                    pk_columns = [col_name]
                                    break
                            
                            # Final fallback: use the first column
                            if not pk_columns and all_columns:
                                pk_columns = [all_columns[0].get('column', 'RowNum')]
                        
                        return pk_columns if pk_columns else ['RowNum']
                    except:
                        return ['RowNum']
                
                # Process all tables efficiently
                all_encryption_data = []
                
                for table_idx, table in enumerate(tables_to_process):
                    schema = table.get('schema', database_name)
                    table_name = table['table_name']
                    
                    status_text.text(f"Processing table {table_idx + 1}/{total_tables}: {schema}.{table_name}")
                    
                    try:
                        # Get primary key columns
                        pk_columns = get_primary_key_columns(connection_id, schema, table_name)
                        
                        # Get all table columns to identify target columns
                        all_columns = db_manager.get_table_columns(connection_id, schema, table_name)
                        column_names = [col.get('column', '') for col in all_columns]
                        
                        # Identify name-related columns (exclude NameStyle)
                        name_patterns = ['name', 'firstname', 'first_name', 'lastname', 'last_name', 
                                       'fullname', 'full_name', 'personname', 'person_name', 
                                       'customer_name', 'employee_name', 'user_name', 'display_name']
                        
                        # Exclusion patterns - columns to skip even if they match name patterns
                        exclude_patterns = ['namestyle', 'name_style']
                        
                        name_related_columns = [col for col in column_names 
                                              if any(pattern in col.lower() for pattern in name_patterns)
                                              and not any(exclude in col.lower() for exclude in exclude_patterns)]
                        
                        if focus_name_columns and not name_related_columns:
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - no name columns found")
                            continue
                        
                        columns_to_process = []
                        if focus_name_columns:
                            columns_to_process = name_related_columns
                        else:
                            # When not focusing on names only, try to get PII columns from recommendations
                            recommended_columns = []
                            pii_columns_info = table.get('pii_columns', [])
                            
                            # st.write(f"  🤖 AI recommendations for {schema}.{table_name}: {len(pii_columns_info)} PII columns")
                            
                            if pii_columns_info:
                                # Extract PII types from AI recommendations and map to actual columns
                                ai_pii_types = []
                                for pii_col in pii_columns_info:
                                    if isinstance(pii_col, dict):
                                        pii_type = pii_col.get('type', 'UNKNOWN')
                                        ai_pii_types.append(pii_type)
                                        # st.write(f"    📋 Found AI PII type: {pii_type}")
                                    elif isinstance(pii_col, str):
                                        ai_pii_types.append(pii_col)
                                        # st.write(f"    📋 Found AI PII type: {pii_col}")
                                
                                # Map AI PII types to actual database column names
                                for pii_type in ai_pii_types:
                                    matching_columns = find_columns_for_pii_type(column_names, pii_type)
                                    recommended_columns.extend(matching_columns)
                                    # if matching_columns:
                                    #     st.write(f"    🎯 Mapped {pii_type} to: {matching_columns}")
                                
                                # Remove duplicates
                                recommended_columns = list(set(recommended_columns))
                                columns_to_process = recommended_columns
                                # st.write(f"    ✅ Final AI-mapped columns: {columns_to_process}")
                            
                            # If no matches from AI recommendations, fall back to pattern-based detection
                            if not columns_to_process:
                                # st.write(f"    🔍 No AI mappings found, using pattern-based detection...")
                                # Look for common PII patterns in all columns
                                pii_patterns = ['name', 'email', 'phone', 'address', 'ssn', 'birth', 'id', 
                                              'login', 'user', 'person', 'customer', 'employee', 'contact',
                                              'mobile', 'tel', 'mail', 'zip', 'postal', 'city', 'state']
                                
                                columns_to_process = [col for col in column_names 
                                                    if any(pattern in col.lower() for pattern in pii_patterns)
                                                    and not any(exclude in col.lower() for exclude in exclude_patterns)]
                                # st.write(f"    🎯 Pattern-matched columns: {columns_to_process}")
                            
                            # If still nothing, include name columns as minimum
                            if not columns_to_process:
                                # st.write(f"    🚨 No pattern matches, falling back to name columns...")
                                columns_to_process = name_related_columns
                        
                        if not columns_to_process:
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - no target columns found")
                            # st.write(f"    🔍 Available columns: {column_names[:10]}...")  # Show first 10 columns
                            # if not focus_name_columns:
                                # st.write(f"    📋 AI recommended columns: {[pii_col.get('column', str(pii_col)) if isinstance(pii_col, dict) else str(pii_col) for pii_col in table.get('pii_columns', [])]}")
                            continue
                        
                        # st.write(f"  🔍 Processing columns in {schema}.{table_name}: {', '.join(columns_to_process)}")
                        
                        # **SMART APPROACH: Pull ALL data at once into pandas DataFrame**
                        target_columns_str = ', '.join([f"[{col}]" for col in columns_to_process])
                        
                        # Build the WHERE clause more carefully to avoid NULL issues
                        non_null_conditions = []
                        for col in columns_to_process:
                            non_null_conditions.append(f"[{col}] IS NOT NULL AND [{col}] != ''")
                        where_clause = ' OR '.join(non_null_conditions) if non_null_conditions else "1=1"
                        
                        # Build query dynamically - always include primary key if available
                        if pk_columns and pk_columns[0] != 'RowNum':
                            pk_columns_str = ', '.join([f"[{col}]" for col in pk_columns])
                            query = f"""
                            SELECT {pk_columns_str}, {target_columns_str}
                            FROM [{schema}].[{table_name}]
                            WHERE ({where_clause})
                            ORDER BY {pk_columns_str}
                            """
                        else:
                            # No reliable primary key, use ROW_NUMBER()
                            query = f"""
                            SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as RowNum, {target_columns_str}
                            FROM [{schema}].[{table_name}]
                            WHERE ({where_clause})
                            ORDER BY RowNum
                            """
                            pk_columns = ['RowNum']
                        
                        cursor = db_manager.connections[connection_id]['connection'].cursor()
                        
                        # **SAFE QUERY EXECUTION: Handle ODBC data type errors**
                        try:
                            cursor.execute(query)
                        except Exception as query_error:
                            cursor.close()
                            # Skip table silently if query execution fails (e.g., unsupported ODBC data types)
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - unsupported data types")
                            continue
                        
                        # Get column descriptions to understand what we actually got back
                        column_descriptions = [desc[0] for desc in cursor.description]
                        
                        # Fetch data efficiently
                        all_rows = []
                        row_count = 0
                        while True:
                            row = cursor.fetchone()
                            if row is None:
                                break
                            
                            # Convert pyodbc.Row to individual column values
                            if hasattr(row, '__getitem__'):
                                # pyodbc.Row object - extract individual values by index
                                row_values = [row[i] for i in range(len(row))]
                            else:
                                # Single value, wrap in list
                                row_values = [row]
                            
                            all_rows.append(row_values)
                            row_count += 1
                        
                        cursor.close()
                        
                        if not all_rows:
                            # st.write(f"  ⏭️ No data found in {schema}.{table_name}")
                            continue
                        
                        # st.write(f"  📊 Found {len(all_rows):,} rows with PII data")
                        
                        # Ensure we have the right number of columns
                        expected_cols = len(column_descriptions)
                        actual_cols = len(all_rows[0]) if all_rows else 0
                        
                        if expected_cols != actual_cols:
                            # Adjust column descriptions to match actual data
                            if actual_cols < expected_cols:
                                column_descriptions = column_descriptions[:actual_cols]
                            elif actual_cols > expected_cols:
                                # Add generic column names for extra columns
                                for i in range(expected_cols, actual_cols):
                                    column_descriptions.append(f"Column_{i+1}")
                        
                        # Create DataFrame with matching columns
                        try:
                            df = pd.DataFrame(all_rows, columns=column_descriptions)
                        except Exception as df_error:
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - data processing error")
                            continue
                        
                        # st.write(f"  📊 Created DataFrame with {len(df):,} rows and {len(df.columns)} columns")
                        
                        # Identify which columns are primary keys and which are target columns
                        actual_pk_columns = [col for col in df.columns if col in pk_columns or col == 'RowNum']
                        actual_target_columns = [col for col in df.columns if col not in actual_pk_columns]
                        
                        if not actual_target_columns:
                            st.write(f"  ⏭️ No target columns found in returned data for {schema}.{table_name}")
                            continue
                        
                        # **VECTORIZED PROCESSING: Create primary key column**
                        if actual_pk_columns:
                            if len(actual_pk_columns) == 1:
                                df['Primary_Key'] = df[actual_pk_columns[0]].astype(str)
                            else:
                                df['Primary_Key'] = df[actual_pk_columns].astype(str).apply(lambda x: '|'.join(x), axis=1)
                        else:
                            df['Primary_Key'] = df.index.astype(str)
                        
                        # **SMART NAME CONSOLIDATION: Merge FirstName, MiddleName, LastName into FullName**
                        name_columns = ['FirstName', 'MiddleName', 'LastName']
                        available_name_cols = [col for col in name_columns if col in actual_target_columns]
                        
                        if len(available_name_cols) >= 2:  # If we have at least FirstName + LastName
                            # st.write(f"  🔗 Consolidating name fields: {', '.join(available_name_cols)}")
                            
                            # Create FullName by concatenating available name parts
                            name_parts = []
                            for col in available_name_cols:
                                # Only add non-null, non-empty values
                                name_parts.append(df[col].fillna('').astype(str).replace('', pd.NA))
                            
                            # Combine name parts with space separator, removing NaN/empty parts
                            df['FullName'] = name_parts[0].fillna('')
                            for part in name_parts[1:]:
                                df['FullName'] = df['FullName'] + ' ' + part.fillna('')
                            
                            # Clean up extra spaces and empty entries
                            df['FullName'] = df['FullName'].str.strip().str.replace(r'\s+', ' ', regex=True)
                            df['FullName'] = df['FullName'].replace('', pd.NA)
                            
                            # Remove individual name columns from target and add FullName
                            actual_target_columns = [col for col in actual_target_columns if col not in available_name_cols]
                            actual_target_columns.append('FullName')
                        
                        # **CHECK: Ensure all target columns exist in DataFrame**
                        missing_columns = [col for col in actual_target_columns if col not in df.columns]
                        if missing_columns:
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - missing required columns")
                            continue
                        
                        # **MELT DataFrame to get one row per column value**
                        # Only melt the target columns (actual columns returned from DB)
                        if not actual_target_columns:
                            st.write(f"  ⏭️ No target columns to process for {schema}.{table_name}")
                            continue
                        
                        # **SAFE MELTING: Handle DataFrame melting with error protection**
                        try:
                            melted_df = pd.melt(df, 
                                              id_vars=actual_pk_columns + ['Primary_Key'], 
                                              value_vars=actual_target_columns,
                                              var_name='Column_Name', 
                                              value_name='Name')
                        except Exception as melt_error:
                            # Skip table silently if melting fails - don't show error to user
                            # st.write(f"  ⏭️ Skipping {schema}.{table_name} - data structure incompatible")
                            continue
                        
                        # **FILTER: Remove null/empty values**
                        melted_df = melted_df.dropna(subset=['Name'])
                        melted_df = melted_df[melted_df['Name'].astype(str).str.strip() != '']
                        melted_df = melted_df[~melted_df['Name'].astype(str).str.lower().isin(['null', 'none', ''])]
                        
                        if melted_df.empty:
                            st.write(f"  ⏭️ No valid data after filtering in {schema}.{table_name}")
                            continue
                        
                        # **VECTORIZED: Add metadata columns**
                        melted_df['Schema'] = f"{database_name}.{schema}.{table_name}"
                        melted_df['AI_Confidence'] = table.get('confidence', 0.0)
                        melted_df['Priority'] = table.get('priority', 'MEDIUM')
                        melted_df['Column_Type'] = melted_df['Column_Name'].apply(
                            lambda col: 'NAME' if any(pattern in col.lower() 
                                                     for pattern in ['name', 'firstname', 'lastname']) 
                                                else 'PII'
                        )
                        
                        # **VECTORIZED: Generate encryption keys using apply - FAST VERSION**
                        if generate_keys:
                            st.write(f"  🔐 Generating {len(melted_df):,} encryption keys...")
                            # Use vectorized string operations for much faster processing
                            melted_df['Encryption_Key'] = 'ENC_' + melted_df['Name'].astype(str).apply(
                                lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest()[:32] if x and str(x).strip() else ""
                            )
                        else:
                            melted_df['Encryption_Key'] = ""
                        
                        # Select final columns in the required format
                        final_df = melted_df[['Name', 'Primary_Key', 'Schema', 'AI_Confidence', 'Encryption_Key', 'Column_Type', 'Priority']].rename(columns={'Primary_Key': 'Key'})
                        
                        # Convert to list of dictionaries for consistency with existing code
                        table_encryption_data = final_df.to_dict('records')
                        all_encryption_data.extend(table_encryption_data)
                        
                        # st.write(f"  ✅ Processed {len(table_encryption_data):,} records from {schema}.{table_name}")
                        total_rows_processed += len(table_encryption_data)
                        
                    except Exception as table_error:
                        # st.write(f"  ⏭️ Skipped {schema}.{table_name}: {str(table_error)}")
                        continue
                    
                    # Update progress
                    progress_bar.progress((table_idx + 1) / total_tables)
                
                # Store results
                st.session_state.encryption_preparation_results = all_encryption_data
                
                # **SAVE TO RESULTS DATABASE - ROBUST BULK INSERT WITH DETAILED LOGGING**
                if all_encryption_data:
                    with st.spinner("Saving results to database..."):
                        try:
                            # st.write("🔌 **Step 1**: Connecting to Results database...")
                            
                            # Connect to Results database
                            results_connection_id = db_manager.connect_to_database('Results')
                            results_cursor = db_manager.connections[results_connection_id]['connection'].cursor()
                            # st.success(f"✅ Connected to Results database (Connection ID: {results_connection_id})")
                            
                            logger.info(f"Connected to Results database (Connection ID: {results_connection_id})")
                            # st.write("🧹 **Step 2**: Clearing existing results for this database...")
                            logger.info(f"Clearing existing results for database '{database_name}'")
                            
                            # Always delete results before new insert
                            # delete_count = results_cursor.execute("DELETE FROM dbo.identified_names_team_epsilon").rowcount
                            # Clear existing results for this database to avoid duplicates
                            delete_count = results_cursor.execute("DELETE FROM dbo.identified_names_team_epsilon WHERE source LIKE ?", (f"{database_name}.%",)).rowcount
                            # st.info(f"🗑️ Cleared {delete_count} existing records for database '{database_name}'")
                            logger.info(f"Cleared {delete_count} existing records for database '{database_name}'")
                            
                            # st.write("📋 **Step 3**: Preparing data for bulk insert...")
                            logger.info(f"Preparing {len(all_encryption_data):,} records for bulk insert")
                            
                            # **ULTRA-FAST WHOLE INSERT: Create pandas DataFrame and use bulk insert**
                            total_records = len(all_encryption_data)
                            # st.write(f"  💾 Total records to process: {total_records:,}")
                            logger.info(f"Total records to process: {total_records:,}")
                            
                            # Convert all data to DataFrame for fastest possible insert
                            insert_data = []
                            conversion_errors = 0
                            
                            for i, record in enumerate(all_encryption_data):
                                try:
                                    # Validate and convert each record
                                    converted_record = {
                                        'name': str(record['Name'])[:255] if record['Name'] else '',  # Truncate to avoid SQL errors
                                        'source': str(record['Schema'])[:500] if record['Schema'] else '',
                                        'probability': float(record['AI_Confidence']) * 100 if record['AI_Confidence'] else 0.0,
                                        'key': str(record['Key'])[:500] if record['Key'] else '',  # Increased from 100 to 500
                                        'encrypt_key': str(record['Encryption_Key'])[:255] if record['Encryption_Key'] else ''
                                    }
                                    
                                    # Additional validation
                                    if not converted_record['name'].strip():
                                        continue  # Skip empty names
                                    
                                    insert_data.append(converted_record)
                                    
                                    # Show progress for large datasets
                                    # if i > 0 and i % 10000 == 0:
                                        # st.write(f"    📊 Processed {i:,}/{total_records:,} records for conversion...")
                                        
                                except Exception as conversion_error:
                                    conversion_errors += 1
                                    if conversion_errors <= 5:  # Show first 5 conversion errors
                                        st.warning(f"⚠️ Record conversion error #{conversion_errors}: {str(conversion_error)}")
                                    continue  # Skip malformed records
                            
                            st.success(f"✅ Data preparation complete: {len(insert_data):,} valid records prepared ({conversion_errors} conversion errors)")
                            
                            if insert_data:
                                # Execute bulk database insert
                                insert_sql = """
                                INSERT INTO dbo.identified_names_team_epsilon (name, source, probability, [key], encrypt_key)
                                VALUES (?, ?, ?, ?, ?)
                                """
                                
                                # Prepare data as tuples for executemany
                                insert_tuples = []
                                for record in insert_data:
                                    try:
                                        tuple_data = (
                                            record['name'],
                                            record['source'], 
                                            record['probability'],
                                            record['key'],
                                            record['encrypt_key']
                                        )
                                        insert_tuples.append(tuple_data)
                                    except Exception:
                                        continue  # Skip malformed tuples
                                
                                # st.info(f"📊 Ready to insert {len(insert_tuples):,} records")
                                
                                if insert_tuples:
                                    # Process in batches for memory management
                                    batch_size = 5000
                                    insert_count = 0
                                    failed_batches = 0
                                    total_batches = len(insert_tuples) // batch_size + (1 if len(insert_tuples) % batch_size else 0)
                                    
                                    # Create progress tracking
                                    batch_progress = st.progress(0)
                                    batch_status = st.empty()
                                    
                                    for batch_num in range(total_batches):
                                        start_idx = batch_num * batch_size
                                        end_idx = min((batch_num + 1) * batch_size, len(insert_tuples))
                                        batch_data = insert_tuples[start_idx:end_idx]
                                        
                                        batch_status.text(f"Processing batch {batch_num + 1}/{total_batches}")
                                        
                                        try:
                                            # Execute batch insert with timing
                                            batch_start = time.time()
                                            
                                            # Use fast_executemany for reliable bulk insert
                                            results_cursor.fast_executemany = True
                                            results_cursor.executemany(insert_sql, batch_data)
                                            insert_count += len(batch_data)
                                            
                                            batch_end = time.time()
                                            batch_time = batch_end - batch_start
                                            
                                            # Update progress
                                            batch_progress.progress((batch_num + 1) / total_batches)
                                            
                                            # Show progress every 5 batches to reduce output
                                            if (batch_num + 1) % 5 == 0 or batch_num == total_batches - 1:
                                                st.write(f"    ✅ Batch {batch_num + 1}/{total_batches}: {len(batch_data):,} records in {batch_time:.2f}s (Total: {insert_count:,})")
                                                
                                        except Exception as batch_error:
                                            failed_batches += 1
                                            st.error(f"❌ Batch {batch_num + 1} failed: {str(batch_error)}")
                                            continue
                                    
                                    # Clear progress indicators
                                    batch_progress.empty()
                                    batch_status.empty()
                                    
                                    # Commit the transaction
                                    try:
                                        db_manager.connections[results_connection_id]['connection'].commit()
                                        # st.success(f"✅ Successfully saved {insert_count:,} records to database!")
                                        
                                        if failed_batches > 0:
                                            st.warning(f"⚠️ {failed_batches} out of {total_batches} batches failed")
                                            
                                    except Exception as commit_error:
                                        st.error(f"❌ Commit failed: {str(commit_error)}")
                                        try:
                                            db_manager.connections[results_connection_id]['connection'].rollback()
                                            st.warning("Transaction rolled back")
                                        except:
                                            st.error("Rollback failed")
                                            
                                else:
                                    st.warning("⚠️ No data prepared for insert")
                            else:
                                st.warning("⚠️ No valid data after preparation")
                            
                            results_cursor.close()
                            
                        except Exception as db_save_error:
                            st.error(f"❌ Database save error: {str(db_save_error)}")
                            st.info("💡 Results are still available for download as CSV")
                
                progress_bar.progress(1.0)
                status_text.text("✅ Encryption preparation complete!")
                
                # Summary
                st.success(f"🎉 **Scan Complete!** Processed {total_rows_processed:,} records from {len(tables_to_process)} tables")
                # st.info(f"📊 **Encryption Records Created:** {len(all_encryption_data):,}")
                
                # Database save status
                # if all_encryption_data:
                #     st.info(f"💾 **Database Status:** Results saved to Results database for future reference")
                
                # Show breakdown by type
                name_records = len([r for r in all_encryption_data if r['Column_Type'] == 'NAME'])
                pii_records = len(all_encryption_data) - name_records
                st.metric("🚨 NAME Records (Critical)", f"{name_records:,}")
                st.metric("📄 Other PII Records", f"{pii_records:,}")
                
            except Exception as e:
                st.error(f"❌ Encryption preparation failed: {str(e)}")
                return
    
    # Show results preview if available
    if st.session_state.get('encryption_preparation_results'):
        st.subheader("📊 Encryption Preparation Results")
        
        results = st.session_state.encryption_preparation_results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{len(results):,}")
        with col2:
            name_count = len([r for r in results if r['Column_Type'] == 'NAME'])
            st.metric("🚨 NAME Records", f"{name_count:,}")
        with col3:
            high_priority = len([r for r in results if r['Priority'] == 'HIGH'])
            st.metric("🔴 High Priority", f"{high_priority:,}")
        with col4:
            unique_tables = len(set([r['Schema'].split('.')[1] + '.' + r['Schema'].split('.')[2] for r in results]))
            st.metric("📋 Tables", unique_tables)
        
        # Preview table
        st.subheader("🔍 Sample Encryption Records")
        import pandas as pd
        
        # Show first 20 records
        preview_data = results[:20]
        if preview_data:
            df = pd.DataFrame(preview_data)
            
            # Prepare enhanced display
            display_df = df[['Name', 'Key', 'Schema', 'AI_Confidence', 'Encryption_Key', 'Column_Type', 'Priority']]
            
            # Enhanced column names with emojis
            column_mapping = {
                'Name': '👤 Name',
                'Key': '🔑 Primary Key',
                'Schema': '📍 Schema Location',
                'AI_Confidence': '🎯 AI Confidence',
                'Encryption_Key': '🔐 Encryption Key',
                'Column_Type': '📊 Type',
                'Priority': '⭐ Priority'
            }
            display_df = display_df.rename(columns=column_mapping)
            
            # Format confidence properly (it's already a decimal)
            if '🎯 AI Confidence' in display_df.columns:
                display_df['🎯 AI Confidence'] = display_df['🎯 AI Confidence'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
            
            # Truncate long values for display
            if '🔐 Encryption Key' in display_df.columns:
                display_df['🔐 Encryption Key'] = display_df['🔐 Encryption Key'].apply(lambda x: f"{str(x)[:15]}..." if pd.notnull(x) and len(str(x)) > 15 else str(x))
            
            if '📍 Schema Location' in display_df.columns:
                display_df['📍 Schema Location'] = display_df['📍 Schema Location'].apply(lambda x: '.'.join(str(x).split('.')[-2:]) if '.' in str(x) else str(x))
            
            # Color-code priority and type
            def style_priority(val):
                if val == 'HIGH':
                    return 'background-color: #ffcdd2; color: #d32f2f; font-weight: bold;'
                elif val == 'MEDIUM':
                    return 'background-color: #fff3e0; color: #f57c00; font-weight: bold;'
                elif val == 'NAME':
                    return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
                else:
                    return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold;'
            
            # Apply styling
            styled_df = display_df.style.applymap(style_priority, subset=['⭐ Priority', '📊 Type'])
            
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "👤 Name": st.column_config.TextColumn("👤 Name", width="medium"),
                    "🔑 Primary Key": st.column_config.TextColumn("🔑 Primary Key", width="small"),
                    "📍 Schema Location": st.column_config.TextColumn("📍 Schema Location", width="medium"),
                    "🎯 AI Confidence": st.column_config.TextColumn("🎯 AI Confidence", width="small"),
                    "🔐 Encryption Key": st.column_config.TextColumn("🔐 Encryption Key", width="medium"),
                    "📊 Type": st.column_config.TextColumn("📊 Type", width="small"),
                    "⭐ Priority": st.column_config.TextColumn("⭐ Priority", width="small"),
                },
                hide_index=True
            )
            
            if len(results) > 20:
                st.info(f"Showing first 20 records out of {len(results):,} total records")
        
        # Download option
        if st.button("💾 Download Full Encryption Table (CSV)"):
            # Convert to CSV
            df_full = pd.DataFrame(results)
            csv = df_full.to_csv(index=False)
            st.download_button(
                label="📥 Download encryption-table.csv",
                data=csv,
                file_name=f"encryption-table-{database_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back: AI Discovery"):
            st.session_state.current_page = "2. AI Discovery"
            st.rerun()
    with col2:
        if st.button("Next: View Results →", type="primary", disabled=not st.session_state.get('encryption_preparation_results')):
            st.session_state.current_page = "4. Results Display"
            st.rerun()

def show_results_display():
    """Step 4: Results Display"""
    st.header("📊 Step 4: Results Display")
    st.markdown("View encryption preparation results and final analysis")
    
    if not st.session_state.get('encryption_preparation_results'):
        st.warning("⚠️ No encryption results to display. Please complete the Encryption Preparation step.")
        if st.button("← Go to Encryption Preparation"):
            st.session_state.current_page = "3. Encryption Preparation"
            st.rerun()
        return
    
    results = st.session_state.encryption_preparation_results
    database_name = st.session_state.current_connection
    
    st.success(f"✅ **Analysis Complete - {len(results):,} encryption records ready**")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{len(results):,}")
    with col2:
        name_records = len([r for r in results if r['Column_Type'] == 'NAME'])
        st.metric("🚨 NAME Records", f"{name_records:,}")
    with col3:
        high_priority = len([r for r in results if r['Priority'] == 'HIGH'])
        st.metric("🔴 High Priority", f"{high_priority:,}")
    with col4:
        unique_tables = len(set([r['Schema'].split('.')[1] + '.' + r['Schema'].split('.')[2] for r in results]))
        st.metric("📋 Tables Processed", unique_tables)
    
    # Detailed breakdown
    st.subheader("🔍 Encryption Records Breakdown")
    
    # Group by table
    table_groups = {}
    for record in results:
        schema_parts = record['Schema'].split('.')
        if len(schema_parts) >= 3:
            table_key = f"{schema_parts[1]}.{schema_parts[2]}"
            if table_key not in table_groups:
                table_groups[table_key] = []
            table_groups[table_key].append(record)
    
    # Display by table
    for table_name, table_records in table_groups.items():
        with st.expander(f"📋 **{table_name}** ({len(table_records)} records)", expanded=False):
            # Show summary for this table
            name_count = len([r for r in table_records if r['Column_Type'] == 'NAME'])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Records", len(table_records))
                st.metric("NAME Records", name_count)
            with col2:
                columns = set([r['Schema'].split('.')[-1] for r in table_records])
                st.metric("Columns", len(columns))
                avg_confidence = sum([r['AI_Confidence'] for r in table_records]) / len(table_records)
                st.metric("Avg AI Confidence", f"{avg_confidence:.2f}")
            
            # Show sample records
            st.write("**📋 Sample Records:**")
            import pandas as pd
            df = pd.DataFrame(table_records[:10])
            if not df.empty:
                # Prepare enhanced display
                display_df = df[['Name', 'Key', 'Column_Type', 'AI_Confidence', 'Encryption_Key', 'Priority']]
                
                # Enhanced column names with emojis
                column_mapping = {
                    'Name': '👤 Name',
                    'Key': '🔑 Primary Key',
                    'Column_Type': '📊 Type',
                    'AI_Confidence': '🎯 AI Confidence',
                    'Encryption_Key': '🔐 Encryption Key',
                    'Priority': '⭐ Priority'
                }
                display_df = display_df.rename(columns=column_mapping)
                
                # Format confidence properly (it's already a decimal)
                if '🎯 AI Confidence' in display_df.columns:
                    display_df['🎯 AI Confidence'] = display_df['🎯 AI Confidence'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                
                # Truncate long encryption keys for display
                if '🔐 Encryption Key' in display_df.columns:
                    display_df['🔐 Encryption Key'] = display_df['🔐 Encryption Key'].apply(lambda x: f"{str(x)[:15]}..." if pd.notnull(x) and len(str(x)) > 15 else str(x))
                
                # Color-code priority and type
                def style_priority(val):
                    if val == 'HIGH':
                        return 'background-color: #ffcdd2; color: #d32f2f; font-weight: bold;'
                    elif val == 'MEDIUM':
                        return 'background-color: #fff3e0; color: #f57c00; font-weight: bold;'
                    elif val == 'NAME':
                        return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
                    else:
                        return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold;'
                
                # Apply styling and display
                styled_df = display_df.style.applymap(style_priority, subset=['⭐ Priority', '📊 Type'])
                
                st.dataframe(
                    styled_df, 
                    use_container_width=True,
                    column_config={
                        "👤 Name": st.column_config.TextColumn("👤 Name", width="medium"),
                        "🔑 Primary Key": st.column_config.TextColumn("🔑 Primary Key", width="small"),
                        "📊 Type": st.column_config.TextColumn("📊 Type", width="small"),
                        "🎯 AI Confidence": st.column_config.TextColumn("🎯 AI Confidence", width="small"),
                        "🔐 Encryption Key": st.column_config.TextColumn("🔐 Encryption Key", width="medium"),
                        "⭐ Priority": st.column_config.TextColumn("⭐ Priority", width="small"),
                    },
                    hide_index=True
                )
    
    # Download options
    st.subheader("💾 Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Full Results (CSV)"):
            import pandas as pd
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV File",
                data=csv,
                file_name=f"pii_encryption_results_{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Generate Summary Report"):
            # Create summary report
            summary_data = {
                'database': database_name,
                'total_records': len(results),
                'name_records': len([r for r in results if r['Column_Type'] == 'NAME']),
                'tables_processed': len(table_groups),
                'high_priority_records': len([r for r in results if r['Priority'] == 'HIGH']),
                'generated_at': datetime.now().isoformat()
            }
            
            import json
            report_json = json.dumps(summary_data, indent=2)
            st.download_button(
                label="📥 Download Summary Report",
                data=report_json,
                file_name=f"pii_summary_report_{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back: Encryption Preparation"):
            st.session_state.current_page = "3. Encryption Preparation"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Dashboard"):
            st.session_state.current_page = "1. Dashboard"
            st.rerun()

def show_upload_regulations():
    """Simple page for uploading regulation documents and generating JSON"""
    st.header("📄 Upload Regulation Document")
    st.markdown("Upload a PDF document and get structured JSON data using AI")
    
    # Simple file upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your regulation or compliance document",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.success(f"✅ **{uploaded_file.name}** uploaded successfully")
        
        # Simple process button
        if st.button("🤖 Process with AI", type="primary", use_container_width=True):
            try:
                # Extract text
                with st.spinner("� Reading PDF..."):
                    pdf_text = read_pdf_text(uploaded_file)
                    
                    if not pdf_text.strip():
                        st.error("❌ Could not extract text from PDF. Please ensure the PDF contains readable text.")
                        return
                
                # Process with AI
                with st.spinner("🤖 Analyzing with AI..."):
                    regulation_data = get_personal_data_definition(pdf_text)
                    
                    if not regulation_data:
                        st.error("❌ Failed to process document with AI. Please try again.")
                        return
                
                # Simple success message
                st.success("✅ **Processing Complete!**")
                
                # Display JSON cleanly
                if isinstance(regulation_data, dict):
                    st.subheader("📄 Regulation Data (JSON)")
                    
                    # Clean JSON display options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        pretty_print = st.checkbox("Pretty Format", value=True)
                    
                    if pretty_print:
                        json_str = json.dumps(regulation_data, indent=2)
                    else:
                        json_str = json.dumps(regulation_data)
                    
                    # Display JSON
                    st.code(json_str, language='json')
                    
                    # Simple download
                    filename = uploaded_file.name.replace('.pdf', '_regulation.json')
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_str,
                        file_name=filename,
                        mime="application/json",
                        use_container_width=True
                    )
                    
                else:
                    # Fallback display
                    st.subheader("📄 AI Response")
                    st.write(regulation_data)
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:
        # Simple help text when no file uploaded
        st.info("👆 Upload a PDF regulation document to get started")
        
        # Minimal examples
        with st.expander("� Supported Documents", expanded=False):
            st.markdown("""
            - **GDPR** - General Data Protection Regulation
            - **CCPA** - California Consumer Privacy Act  
            - **HIPAA** - Health Insurance Portability
            - **Custom** - Privacy policies and data regulations
            """)
    
    # Simple navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    with col2:
        if st.button("� Results Table"):
            st.session_state.current_page = "5. Check Results Table"
            st.rerun()

def show_check_results_table():
    """New page to check and search the identified_names_team_epsilon table"""
    st.header("🔍 Check Results Table")
    st.markdown("Search and browse the identified PII names from the results database.")
    
    # Input field for name search
    search_name = st.text_input("🔎 Enter name to search for:", placeholder="e.g., Robert D. Junior")
    
    # Similarity threshold slider
    similarity_threshold = st.slider(
        "Similarity threshold (for finding similar names)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.8, 
        step=0.1,
        help="Higher values = more strict matching. Lower values = find more variations."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        exact_search = st.button("🎯 Exact Match Search", type="primary")
    
    with col2:
        similar_search = st.button("🔗 Similar Names Search", type="secondary")
    
    # Display results
    if exact_search or similar_search:
        try:
            # Get results from the database
            if exact_search:
                results = search_exact_names(search_name)
                st.subheader(f"Exact matches for: '{search_name}'")
            else:
                results = search_similar_names(search_name, similarity_threshold)
                st.subheader(f"Similar names to: '{search_name}' (threshold: {similarity_threshold})")
            
            if results:
                # Convert to DataFrame for enhanced display
                df = pd.DataFrame(results)
                
                # Show count with enhanced styling
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%); 
                            padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                    <h3 style='color: white; margin: 0; font-weight: bold;'>
                        ✅ Found {len(results)} matching record{'s' if len(results) != 1 else ''}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Add similarity score column if doing similar search
                if similar_search and 'similarity_score' in df.columns:
                    df = df.sort_values('similarity_score', ascending=False)
                
                # Enhance column names for better display
                column_mapping = {
                    'id': 'ID',
                    'name': '👤 Name',
                    'source': '📍 Source',
                    'probability': '📊 Probability',
                    'key': '🔑 Key',
                    'encrypt_key': '🔐 Encryption Key',
                    'similarity_score': '🎯 Similarity Score'
                }
                
                # Rename columns for better display
                display_df = df.rename(columns=column_mapping)
                
                # Format probability and similarity columns properly
                if '📊 Probability' in display_df.columns:
                    display_df['📊 Probability'] = display_df['📊 Probability'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                
                if '🎯 Similarity Score' in display_df.columns:
                    display_df['🎯 Similarity Score'] = display_df['🎯 Similarity Score'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                
                # Truncate long encryption keys for display
                if '🔐 Encryption Key' in display_df.columns:
                    display_df['🔐 Encryption Key'] = display_df['🔐 Encryption Key'].apply(lambda x: f"{str(x)[:20]}..." if pd.notnull(x) and len(str(x)) > 20 else str(x))
                
                # Display the enhanced results table with column configuration
                st.dataframe(
                    display_df, 
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "👤 Name": st.column_config.TextColumn("👤 Name", width="medium"),
                        "📍 Source": st.column_config.TextColumn("📍 Source", width="large"),
                        "📊 Probability": st.column_config.TextColumn("📊 Probability", width="small"),
                        "🔑 Key": st.column_config.TextColumn("🔑 Key", width="medium"),
                        "🔐 Encryption Key": st.column_config.TextColumn("🔐 Encryption Key", width="medium"),
                        "🎯 Similarity Score": st.column_config.TextColumn("🎯 Similarity Score", width="small"),
                    },
                    hide_index=True
                )
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"pii_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.warning(f"No matching records found for: '{search_name}'")
                
        except Exception as e:
            st.error(f"Error searching database: {str(e)}")
    
    # Show some statistics about the table
    st.markdown("---")
    st.subheader("📊 Table Statistics")
    
    try:
        stats = get_results_table_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", stats.get('total_records', 0))
            with col2:
                st.metric("Unique Names", stats.get('unique_names', 0))
            with col3:
                st.metric("Unique Sources", stats.get('unique_sources', 0))
                
            # Show recent additions if any
            recent_records = get_recent_records(limit=5)
            if recent_records:
                st.subheader("🕒 Recent Additions")
                recent_df = pd.DataFrame(recent_records)
                
                # Enhanced column names
                column_mapping = {
                    'name': '👤 Name',
                    'source': '📍 Source',
                    'probability': '📊 Probability'
                }
                recent_df = recent_df.rename(columns=column_mapping)
                
                # Format probability properly (it's already in percentage)
                if '📊 Probability' in recent_df.columns:
                    recent_df['📊 Probability'] = recent_df['📊 Probability'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                
                st.dataframe(
                    recent_df, 
                    use_container_width=True,
                    column_config={
                        "👤 Name": st.column_config.TextColumn("👤 Name", width="medium"),
                        "📍 Source": st.column_config.TextColumn("📍 Source", width="large"),
                        "📊 Probability": st.column_config.TextColumn("📊 Probability", width="small"),
                    },
                    hide_index=True
                )
        else:
            st.info("No data available in the results table yet.")
    except Exception as e:
        st.warning(f"Unable to load table statistics: {str(e)}")
    
    # Navigation
    st.markdown("---")
    if st.button("🏠 Back to Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

def normalize_name(name: str) -> str:
    """Normalize a name for better matching by removing periods, extra spaces, etc."""
    if not name:
        return ""
    
    # Convert to lowercase and strip
    normalized = name.lower().strip()
    
    # Remove periods
    normalized = normalized.replace('.', '')
    
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove common suffixes that might vary (Jr, Jr., Senior, Sr, Sr., etc.)
    # This makes "Robert D Junior" match "Robert D. Junior" 
    suffixes = [' jr', ' junior', ' sr', ' senior', ' iii', ' ii', ' iv']
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
            break
    
    return normalized

def search_exact_names(search_name: str) -> List[Dict]:
    """Search for exact matches in the identified_names_team_epsilon table"""
    try:
        # Connect to the Results database
        connection_id = st.session_state.db_manager.connect_to_database("Results")
        
        # Query the table directly
        query = """
        SELECT id, name, source, probability, [key], encrypt_key
        FROM [dbo].[identified_names_team_epsilon]
        """
        
        df = st.session_state.db_manager.execute_query(connection_id, query)
        
        if df.empty:
            return []
        
        # Convert DataFrame to list of dictionaries
        results = df.to_dict('records')
        
        # Filter for exact matches (case-insensitive with normalization)
        exact_matches = []
        search_name_normalized = normalize_name(search_name)
        
        for result in results:
            result_name_normalized = normalize_name(result.get('name', ''))
            if result_name_normalized == search_name_normalized:
                exact_matches.append({
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'source': result.get('source'),
                    'probability': result.get('probability'),
                    'key': result.get('key'),
                    'encrypt_key': result.get('encrypt_key')
                })
        
        return exact_matches
    except Exception as e:
        st.error(f"Error in exact search: {str(e)}")
        return []

def search_similar_names(search_name: str, threshold: float = 0.6) -> List[Dict]:
    """Search for similar names using fuzzy matching"""
    try:
        # Connect to the Results database
        connection_id = st.session_state.db_manager.connect_to_database("Results")
        
        # Query the table directly
        query = """
        SELECT id, name, source, probability, [key], encrypt_key
        FROM [dbo].[identified_names_team_epsilon]
        """
        
        df = st.session_state.db_manager.execute_query(connection_id, query)
        
        if df.empty:
            return []
        
        # Convert DataFrame to list of dictionaries
        results = df.to_dict('records')
        
        # Find similar matches using difflib with normalization
        similar_matches = []
        search_name_normalized = normalize_name(search_name)
        
        for result in results:
            name_normalized = normalize_name(result.get('name', ''))
            if name_normalized:
                # Calculate similarity ratio on normalized names
                similarity = difflib.SequenceMatcher(None, search_name_normalized, name_normalized).ratio()
                
                if similarity >= threshold:
                    similar_matches.append({
                        'id': result.get('id'),
                        'name': result.get('name'),
                        'source': result.get('source'),
                        'probability': result.get('probability'),
                        'key': result.get('key'),
                        'encrypt_key': result.get('encrypt_key'),
                        'similarity_score': round(similarity, 3)
                    })
        
        return similar_matches
    except Exception as e:
        st.error(f"Error in similarity search: {str(e)}")
        return []

def get_results_table_stats() -> Dict:
    """Get statistics about the results table"""
    try:
        # Connect to the Results database
        connection_id = st.session_state.db_manager.connect_to_database("Results")
        
        # Query the table directly
        query = """
        SELECT id, name, source, probability, [key], encrypt_key
        FROM [dbo].[identified_names_team_epsilon]
        """
        
        df = st.session_state.db_manager.execute_query(connection_id, query)
        
        if df.empty:
            return {}
        
        # Convert DataFrame to list of dictionaries
        results = df.to_dict('records')
        
        unique_names = set()
        unique_sources = set()
        
        for result in results:
            if result.get('name'):
                unique_names.add(result['name'].lower().strip())
            if result.get('source'):
                unique_sources.add(result['source'])
        
        return {
            'total_records': len(results),
            'unique_names': len(unique_names),
            'unique_sources': len(unique_sources)
        }
    except Exception as e:
        st.error(f"Error getting table stats: {str(e)}")
        return {}

def get_recent_records(limit: int = 5) -> List[Dict]:
    """Get recent records from the results table"""
    try:
        # Connect to the Results database
        connection_id = st.session_state.db_manager.connect_to_database("Results")
        
        # Query the table directly with limit
        query = f"""
        SELECT TOP {limit} id, name, source, probability, [key], encrypt_key
        FROM [dbo].[identified_names_team_epsilon]
        ORDER BY id DESC
        """
        
        df = st.session_state.db_manager.execute_query(connection_id, query)
        
        if df.empty:
            return []
        
        # Convert DataFrame to list of dictionaries
        results = df.to_dict('records')
        
        return [{
            'name': result.get('name'),
            'source': result.get('source'),
            'probability': result.get('probability')
        } for result in results]
    except Exception as e:
        st.error(f"Error getting recent records: {str(e)}")
        return []

if __name__ == "__main__":
    main()
