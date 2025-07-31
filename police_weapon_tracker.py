import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Bhopal Police - Weapon License Tracker",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'notifications_sent' not in st.session_state:
    st.session_state.notifications_sent = []

def load_data():
    """Load the weapon license data"""
    try:
        # Try to load the comprehensive dataset first
        df = pd.read_csv('bhopal_weapon_licenses_comprehensive.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset not found! Please ensure the CSV file is in the same directory.")
        return None

def send_notification_simulation(mobile, name, message_type):
    """Simulate sending SMS notification"""
    messages = {
        'collection': f"Dear {name}, As per government orders, please submit your licensed weapon to {st.session_state.selected_station} by {st.session_state.deadline}. Contact: 0755-XXX-XXXX. - Bhopal Police",
        'reminder': f"Reminder: {name}, your weapon submission deadline is approaching ({st.session_state.deadline}). Please visit {st.session_state.selected_station} immediately. - Bhopal Police",
        'return': f"Dear {name}, you may collect your submitted weapon from {st.session_state.selected_station} after {st.session_state.return_date}. Bring ID proof. - Bhopal Police"
    }
    
    return {
        'mobile': mobile,
        'name': name,
        'message': messages[message_type],
        'timestamp': datetime.now(),
        'status': 'Sent'
    }

def create_dashboard():
    """Create the main dashboard"""
    if st.session_state.df is None:
        return
    
    df = st.session_state.df
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1> Bhopal Police Department</h1>
        <h3>Weapon License Tracking & Management System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_licenses = len(df)
        st.metric("Total Licenses", total_licenses, help="Total weapon licenses in system")
    
    with col2:
        active_licenses = len(df[df['Status'] == 'Active'])
        st.metric("Active Licenses", active_licenses, help="Currently active licenses")
    
    with col3:
        expired_licenses = len(df[df['Status'] == 'Expired'])
        st.metric("Expired Licenses", expired_licenses, delta=f"{expired_licenses/total_licenses*100:.1f}%")
    
    with col4:
        submitted_weapons = len(df[df['Status'] == 'Submitted'])
        st.metric("Weapons Submitted", submitted_weapons, help="Weapons currently with police")
    
    with col5:
        revoked_licenses = len(df[df['Status'] == 'Revoked'])
        st.metric("Revoked Licenses", revoked_licenses, help="Permanently revoked licenses")
    
    # Quick Actions Section
    st.markdown("##  Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(" Election Period Alert", help="Send collection notices for election period"):
            st.session_state.action_type = 'election'
            st.session_state.show_notification_panel = True
    
    with col2:
        if st.button(" Festival Period Alert", help="Send collection notices for festival period"):
            st.session_state.action_type = 'festival'
            st.session_state.show_notification_panel = True
    
    with col3:
        if st.button(" Emergency Collection", help="Send immediate collection notices"):
            st.session_state.action_type = 'emergency'
            st.session_state.show_notification_panel = True

def create_analytics():
    """Create analytics dashboard"""
    if st.session_state.df is None:
        return
    
    df = st.session_state.df
    
    st.markdown("##  Analytics Dashboard")
    
    # Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig_status = px.pie(
            values=df['Status'].value_counts().values,
            names=df['Status'].value_counts().index,
            title="License Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        fig_weapon = px.bar(
            x=df['Gun_Type'].value_counts().index,
            y=df['Gun_Type'].value_counts().values,
            title="Weapon Type Distribution",
            color=df['Gun_Type'].value_counts().values,
            color_continuous_scale="viridis"
        )
        fig_weapon.update_layout(showlegend=False)
        st.plotly_chart(fig_weapon, use_container_width=True)
    
    # Area-wise Analysis
    st.markdown("###  Area-wise License Distribution")
    area_data = df['Area'].value_counts().head(15)
    fig_area = px.bar(
        x=area_data.values,
        y=area_data.index,
        orientation='h',
        title="Top 15 Areas by License Count",
        color=area_data.values,
        color_continuous_scale="blues"
    )
    fig_area.update_layout(height=500)
    st.plotly_chart(fig_area, use_container_width=True)
    
    # Gender Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        gender_data = df['Gender'].value_counts()
        fig_gender = px.pie(
            values=gender_data.values,
            names=gender_data.index,
            title="Gender Distribution",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
            hole=0.4  # Creates donut chart
        )
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with col2:
        # Age Analysis
        df['Age'] = (datetime.now() - pd.to_datetime(df['DOB'])).dt.days // 365
        age_bins = [0, 30, 40, 50, 60, 100]
        age_labels = ['21-30', '31-40', '41-50', '51-60', '60+']
        df['Age_Group'] = pd.cut(df['Age'], bins=[20] + age_bins[1:], labels=age_labels, right=False)
        
        age_dist = df['Age_Group'].value_counts()
        fig_age = px.bar(
            x=age_dist.index,
            y=age_dist.values,
            title="Age Group Distribution",
            color=age_dist.values,
            color_continuous_scale="plasma"
        )
        st.plotly_chart(fig_age, use_container_width=True)

def create_weapon_management():
    """Create weapon management interface"""
    if st.session_state.df is None:
        return
    
    df = st.session_state.df
    
    st.markdown("##  Weapon Management")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        selected_area = st.selectbox("Select Area", ['All'] + sorted(df['Area'].unique().tolist()))
    
    with col2:
        selected_status = st.selectbox("Select Status", ['All'] + sorted(df['Status'].unique().tolist()))
    
    with col3:
        selected_weapon = st.selectbox("Select Weapon Type", ['All'] + sorted(df['Gun_Type'].unique().tolist()))
    
    with col4:
        search_name = st.text_input("Search by Name")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_area != 'All':
        filtered_df = filtered_df[filtered_df['Area'] == selected_area]
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    if selected_weapon != 'All':
        filtered_df = filtered_df[filtered_df['Gun_Type'] == selected_weapon]
    
    if search_name:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
    
    st.markdown(f"###  Filtered Results ({len(filtered_df)} records)")
    
    # Add bulk actions
    if len(filtered_df) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(" Send Collection Notice to All"):
                st.session_state.bulk_action_df = filtered_df
                st.session_state.show_bulk_notification = True
        
        with col2:
            if st.button(" Export Filtered Data"):
                csv = filtered_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="filtered_weapons.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        with col3:
            if st.button(" Refresh Data"):
                st.rerun()
    
    # Display data with action buttons
    for idx, row in filtered_df.iterrows():
        with st.expander(f"📋 {row['Name']} - {row['License_No']} ({row['Status']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Name:** {row['Name']}")
                st.write(f"**License No:** {row['License_No']}")
                st.write(f"**Area:** {row['Area']}")
                st.write(f"**Address:** {row['Address']}")
                st.write(f"**Weapon:** {row['Gun_Type']} - {row['Weapon_Model']}")
                st.write(f"**Mobile:** {row['Mobile']}")
                st.write(f"**Status:** {row['Status']}")
                if row['Remarks']:
                    st.write(f"**Remarks:** {row['Remarks']}")
            
            with col2:
                if st.button(f" Send Notice", key=f"send_{idx}"):
                    notification = send_notification_simulation(
                        row['Mobile'], 
                        row['Name'], 
                        'collection'
                    )
                    st.session_state.notifications_sent.append(notification)
                    st.success(f"Notice sent to {row['Name']}")
                
                if row['Status'] == 'Active':
                    if st.button(f" Mark Submitted", key=f"submit_{idx}"):
                        st.session_state.df.loc[st.session_state.df['License_No'] == row['License_No'], 'Status'] = 'Submitted'
                        st.success(f"Weapon marked as submitted")
                        st.rerun()
                
                elif row['Status'] == 'Submitted':
                    if st.button(f" Mark Returned", key=f"return_{idx}"):
                        st.session_state.df.loc[st.session_state.df['License_No'] == row['License_No'], 'Status'] = 'Active'
                        st.success(f"Weapon marked as returned")
                        st.rerun()

def create_notification_panel():
    """Create notification management panel"""
    st.markdown("##  Notification Center")
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.selected_station = st.selectbox(
            "Collection Point",
            ["Habibganj Police Station", "MP Nagar Police Station", "TT Nagar Police Station", 
             "Arera Colony Police Station", "Kolar Road Police Station"]
        )
        
        st.session_state.deadline = st.date_input(
            "Collection Deadline",
            value=date.today() + timedelta(days=7)
        )
    
    with col2:
        message_type = st.selectbox(
            "Message Type",
            ["Collection Notice", "Reminder", "Return Notice"]
        )
        
        st.session_state.return_date = st.date_input(
            "Return Date (if applicable)",
            value=date.today() + timedelta(days=30)
        )
    
    # Area Selection
    if st.session_state.df is not None:
        selected_areas = st.multiselect(
            "Select Areas",
            options=sorted(st.session_state.df['Area'].unique()),
            default=[]
        )
        
        if selected_areas:
            filtered_for_notification = st.session_state.df[
                (st.session_state.df['Area'].isin(selected_areas)) & 
                (st.session_state.df['Status'] == 'Active')
            ]
            
            st.markdown(f"###  Target Recipients: {len(filtered_for_notification)} license holders")
            
            if st.button(" Send Bulk Notifications"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                notifications = []
                for idx, (_, row) in enumerate(filtered_for_notification.iterrows()):
                    notification = send_notification_simulation(
                        row['Mobile'], 
                        row['Name'], 
                        'collection'
                    )
                    notifications.extend([notification])
                    
                    # Update progress
                    progress = (idx + 1) / len(filtered_for_notification)
                    progress_bar.progress(progress)
                    status_text.text(f'Sending notifications... {idx + 1}/{len(filtered_for_notification)}')
                    
                    time.sleep(0.1)  # Simulate sending delay
                
                st.session_state.notifications_sent.extend(notifications)
                st.success(f" Successfully sent {len(notifications)} notifications!")
    
    # Notification History
    if st.session_state.notifications_sent:
        st.markdown("###  Recent Notifications")
        for notification in reversed(st.session_state.notifications_sent[-10:]):  # Show last 10
            st.markdown(f"""
            <div class="success-card">
                <strong>To:</strong> {notification['name']} ({notification['mobile']})<br>
                <strong>Sent:</strong> {notification['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Message:</strong> {notification['message'][:100]}...
            </div>
            """, unsafe_allow_html=True)

def create_reports():
    """Create reports section"""
    if st.session_state.df is None:
        return
    
    df = st.session_state.df
    
    st.markdown("##  Reports & Insights")
    
    # Summary Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("###  License Statistics")
        stats = df['Status'].value_counts()
        for status, count in stats.items():
            percentage = (count / len(df)) * 100
            st.write(f"**{status}:** {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("###  Top Areas")
        top_areas = df['Area'].value_counts().head(5)
        for area, count in top_areas.items():
            st.write(f"**{area}:** {count} licenses")
    
    with col3:
        st.markdown("###  Weapon Types")
        weapon_stats = df['Gun_Type'].value_counts()
        for weapon, count in weapon_stats.items():
            st.write(f"**{weapon}:** {count}")
    
    # Alerts and Recommendations
    st.markdown("###  Alerts & Recommendations")
    
    # Expired licenses
    expired_count = len(df[df['Status'] == 'Expired'])
    if expired_count > 0:
        st.markdown(f"""
        <div class="alert-card">
            <strong> Alert:</strong> {expired_count} licenses have expired and need renewal or revocation.
        </div>
        """, unsafe_allow_html=True)
    
    # Area concentration
    max_area = df['Area'].value_counts().index[0]
    max_count = df['Area'].value_counts().iloc[0]
    if max_count > len(df) * 0.15:  # If one area has >15% of all licenses
        st.markdown(f"""
        <div class="alert-card">
            <strong> Notice:</strong> High concentration of licenses in {max_area} ({max_count} licenses). 
            Consider additional monitoring during sensitive periods.
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application"""
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/8/8b/Madhya_Pradesh_Police_logo.png", width=150)
        st.markdown("# Navigation")
        
        # Load data
        if st.button("🔄 Load/Refresh Data"):
            st.session_state.df = load_data()
            if st.session_state.df is not None:
                st.success("Data loaded successfully!")
        
        # Navigation
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Weapon Management", "Analytics", "Notifications", "Reports"]
        )
        
        # File upload option
        st.markdown("### 📁 Upload Data")
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        if uploaded_file is not None:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
    
    # Load data if not already loaded
    if st.session_state.df is None:
        st.session_state.df = load_data()
    
    if st.session_state.df is None:
        st.error("No data available. Please upload a CSV file or ensure the dataset exists.")
        st.info("Expected CSV columns: Name, License_No, Area, Police_Station, Address, Gun_Type, Weapon_Model, Issue_Date, Expiry_Date, Status, Mobile, Gender, DOB, Remarks")
        return
    
    # Route to different pages
    if page == "Dashboard":
        create_dashboard()
    elif page == "Weapon Management":
        create_weapon_management()
    elif page == "Analytics":
        create_analytics()
    elif page == "Notifications":
        create_notification_panel()
    elif page == "Reports":
        create_reports()

if __name__ == "__main__":
    main()