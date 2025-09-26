import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from analyzer_llm import report_analyzer

# Page configuration
st.set_page_config(
    page_title="Delay Issue Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
#000000- black , #1a1a1a- dark grey , #6a0dad - purple ,#4b0082- purple , #0f0f0f- dark colour
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: white;
    }
    
    .metric-card {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #6a0dad;
        margin: 0.5rem 0;
    }
    
    .concern-card {
        background-color: #0f0f0f;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #4b0082;
        margin: 1rem 0;
    }
    
    .rank-badge {
        background-color: #6a0dad;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .upload-section {
        background-color: #1a1a1a;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #6a0dad;
        text-align: center;
        margin: 2rem 0;
    }
    
    h1, h2, h3 {
        color: white !important;
    }
    
    .stSelectbox label {
        color: white !important;
    }
    
    .stButton > button {
        background-color: #6a0dad;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #7b68ee;
        transform: translateY(-2px);
    }
    
    .stFileUploader label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate the dashboard UI
def generate_dashboard(analysis_data):
    """Generate interactive dashboard from analysis data"""
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(analysis_data, orient='index').reset_index()
    df.columns = ['Issue_Type', 'Rank', 'Average_Violation_Count', 'Areas_of_Concern', 'Reason']
    df['Issue_Type_Display'] = df['Issue_Type'].str.replace('_', ' ').str.title()
    
    # Convert Average_Violation_Count to float for calculations
    df['Average_Violation_Count'] = pd.to_numeric(df['Average_Violation_Count'], errors='coerce')
    
    # Dashboard Title
    st.title("Delay Issue Analysis Dashboard")
    st.markdown("**Interactive analysis of the most concerning delay entities**")
    st.markdown("---")
    
    # Sidebar for filters and controls
    st.sidebar.header("Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Filter options
    show_all = st.sidebar.checkbox("Show All Issues", value=True)
    if not show_all:
        selected_issues = st.sidebar.multiselect(
            "Select Issues to Display:",
            df['Issue_Type_Display'].tolist(),
            default=df['Issue_Type_Display'].tolist()
        )
        df_filtered = df[df['Issue_Type_Display'].isin(selected_issues)]   ## this will filter the selected metrics
    else:
        df_filtered = df
    
    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort by:",
        ["Rank", "Average Violation Count"],
        index=0
    )
    
    if sort_by == "Rank":
        df_filtered = df_filtered.sort_values('Rank')
    else:
        df_filtered = df_filtered.sort_values('Average_Violation_Count', ascending=False)
    
    # Get top issue (rank 1)
    top_issue_row = df[df['Rank'] == 1]
    top_issue = top_issue_row['Issue_Type_Display'].iloc[0] if len(top_issue_row) > 0 else "N/A"
    
    # Calculate average violations (only for non-zero values)
    non_zero_violations = df[df['Average_Violation_Count'] > 0]['Average_Violation_Count']
    avg_violations = round(non_zero_violations.mean(), 2) if len(non_zero_violations) > 0 else 0
    
    total_issues = len(df)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Top Issue</h3>
            <h2 style="color: #6a0dad;">{top_issue}</h2>
            <p>Highest violation count</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Violations</h3>
            <h2 style="color: #7b68ee;">{avg_violations}</h2>
            <p>Across active issues</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Issues</h3>
            <h2 style="color: #4b0082;">{total_issues}</h2>
            <p>Categories analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---------------- New Tabs Layout ---------------- #
    tab1, tab2, tab3 = st.tabs(["Average Violation Counts & Rankings", "Detailed Analysis", "Interactive Comparison"])
    
    # === Tab 1 ===
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Average Violation Counts")
            colors = [ '#4b0082', "#660f9b", "#9040ba", "#6b4bc4", "#8f55d5", "#b884d2"]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_filtered['Issue_Type_Display'],
                y=df_filtered['Average_Violation_Count'],
                marker_color=colors[:len(df_filtered)],
                text=df_filtered['Average_Violation_Count'].round(2),
                textposition='auto',
                textfont=dict(color='white', size=12)
            ))
            fig.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                title_font=dict(color='white'),
                xaxis=dict(color='white', gridcolor="#5F5555"),
                yaxis=dict(color='white', gridcolor="#635555"),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Rankings")
            for _, row in df_filtered.iterrows():
                rank = int(row['Rank'])
                if rank <= 3:
                    rank_color = '#4b0082' if rank == 1 else "#660f9b" if rank == 2 else "#9040ba"
                else:
                    rank_color = "#6b4bc4"
                
                st.markdown(f"""
                <div style="background-color: #1a1a1a; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {rank_color};">
                    <span class="rank-badge" style="background-color: {rank_color};">#{rank}</span>
                    <strong>{row['Issue_Type_Display']}</strong><br>
                    <small style="color: #cccccc;">{row['Average_Violation_Count']} avg violations</small>
                </div>
                """, unsafe_allow_html=True)
    
    # === Tab 2 ===
    with tab2:
        st.subheader("Detailed Analysis")
        tab_names = [f"#{int(row['Rank'])} {row['Issue_Type_Display']}" for _, row in df_filtered.iterrows()]
        tabs = st.tabs(tab_names)
        for i, (_, row) in enumerate(df_filtered.iterrows()):
            with tabs[i]:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"""
                    <div class="concern-card">
                        <h4 style="color: #6a0dad; margin-top: 0;">Areas of Concern</h4>
                        <p style="line-height: 1.6;">{row['Areas_of_Concern']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="concern-card">
                        <h4 style="color: #7b68ee; margin-top: 0;">Reason for Selection</h4>
                        <p style="line-height: 1.6;">{row['Reason']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # === Tab 3 ===
    with tab3:
        st.subheader("Interactive Comparison")
        comparison_metric = st.selectbox(
            "Compare by:",
            ["Average Violation Count", "Rank"],
            key="comparison"
        )
        
        if comparison_metric == "Average Violation Count":
            df_nonzero = df_filtered[df_filtered['Average_Violation_Count'] > 0]
            if len(df_nonzero) > 0:
                fig = px.pie(
                    df_nonzero, 
                    values='Average_Violation_Count', 
                    names='Issue_Type_Display',
                    color_discrete_sequence=['#6a0dad', '#7b68ee', '#4b0082', '#9370db', '#8a2be2', '#9932cc'],
                    title="Distribution of Average Violations (Non-Zero Values)"
                )
                fig.update_layout(
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    font=dict(color='white'),
                    title_font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No violations to display in pie chart.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_filtered['Issue_Type_Display'],
                y=df_filtered['Rank'],
                mode='markers+lines',
                marker=dict(size=20, color='#6a0dad'),
                line=dict(color='#7b68ee', width=2),
                text=df_filtered['Average_Violation_Count'].round(2),
                textposition='top center',
                textfont=dict(color='white')
            ))
            fig.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                title="Rank vs Issue Type",
                title_font=dict(color='white'),
                xaxis=dict(color='white', gridcolor="#5C5252"),
                yaxis=dict(color='white', gridcolor="#5C4F4F", autorange='reversed'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)


# Main Application Logic
def main():
    # Initialize session state
    if 'dashboard_generated' not in st.session_state:
        st.session_state.dashboard_generated = False
    
    if not st.session_state.dashboard_generated:
        # Upload Section
        st.title("Upload Report for Delay Analysis")
        st.markdown("Upload your JSON file to generate comprehensive delay analysis using AI-powered insights")
        
        st.markdown("""
        <div class="upload-section">
            <h3 style="color: #6a0dad; margin-top: 0;">Report Upload</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=["json"],
            help="Upload your weekly delay data in JSON format"
        )
        
        if uploaded_file is not None:
            try:
                # Read and parse JSON file
                file_content = uploaded_file.read().decode('utf-8')
                json_data = json.loads(file_content)
                
                # Display preview of uploaded data
                st.success("File uploaded successfully!")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("Analyze Report", type="primary"):
                        with st.spinner("Analyzing your report using AI insights..."):
                            try:
                                # Call the external report_analyzer function
                                analysis_result = report_analyzer(json_data)
                                
                                if analysis_result:
                                    st.session_state.analysis_data = analysis_result
                                    st.session_state.dashboard_generated = True
                                    st.rerun()
                                else:
                                    st.error("Analysis function returned no results.")
                            except Exception as e:
                                st.error(f"Error during analysis: {str(e)}")
                                st.error("Please check that analyzer_llm.py exists and contains the report_analyzer function.")
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please check the file format and try again.")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        else:
            st.info("Please upload a JSON file to get started.")
    
    else:
        generate_dashboard(st.session_state.analysis_data)
        
        st.sidebar.markdown("---")
        if st.sidebar.button("Upload New Data"):
            st.session_state.dashboard_generated = False
            st.rerun()
        
        with st.sidebar.expander("Raw Analysis Data"):
            st.json(st.session_state.analysis_data)

# Hide Streamlit default elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
