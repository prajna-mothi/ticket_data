import streamlit as st
import json
import requests
import json

#Define your Google Drive file ID
file_id = "1gv2SDF_Yshf7zHAz4VpVIjkWcRSPOfZ9"

# Construct the download URL
file_url = f"https://drive.google.com/uc?id=1gv2SDF_Yshf7zHAz4VpVIjkWcRSPOfZ9"

# Fetch the file content
response = requests.get(file_url)
if response.status_code == 200:
    data = response.json()
else:
    st.error("Failed to load the sensitive file from Google Drive.")




# Load JSON data
# with open("dashboard_with_tickets.json", "r") as f:
#     data = json.load(f)

# Adjust the sidebar width using Streamlit's set_page_config
st.set_page_config(layout="wide")

# Custom CSS to adjust dropdown width
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] .css-1d391kg {  /* Sidebar width */
        width: 400px;
    }
    [data-testid="stSidebar"] .css-1v4vqrs { /* Dropdown text area */
        overflow: visible;
        text-overflow: clip;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit layout
st.title("HyperSight Dashboard")
st.subheader("Company Name: Mynt AB")
st.subheader("Report Period: Nov 1 - Nov 30")

st.sidebar.header("Filters")

# Category filter
categories = list(set(item['category'] for item in data))
category_filter = st.sidebar.selectbox("Category", categories)

# Subtopic label filter with ticket count
subcategory_options = [
    f"{item['subtopic_label']} ({item['ticket_count']} tickets)" for item in data if item['category'] == category_filter
]
subcategory_mapping = {
    f"{item['subtopic_label']} ({item['ticket_count']} tickets)": item['subtopic_label']
    for item in data if item['category'] == category_filter
}
subcategory_selected = st.sidebar.selectbox("Subcategory", subcategory_options, key="subcategory_select")
subtopic_label_filter = subcategory_mapping[subcategory_selected]

# Common issues filter (renamed to "Issues under Subcategory")
filtered_common_issues = []
selected_subtopic = None
for item in data:
    if item['category'] == category_filter and item['subtopic_label'] == subtopic_label_filter:
        selected_subtopic = item
        filtered_common_issues = [issue['issue'] for issue in item['common_issues']]
        break

common_issue_filter = st.sidebar.selectbox("Issues under Subcategory", ["All"] + filtered_common_issues)

# Responsible department filter (exclude "Unknown")
departments = list(set(
    issue.get('responsible_department', 'Unknown')
    for item in data if item['category'] == category_filter
    for issue in item['common_issues']
))
departments = [department for department in departments if department != "Unknown"]  # Exclude "Unknown"
responsible_department_filter = st.sidebar.selectbox("Responsible Department", ["All"] + departments)

# Sorting toggle button
if "sort_ascending" not in st.session_state:
    st.session_state.sort_ascending = True  # Default to ascending order

if selected_subtopic:
    total_tickets = sum(issue['ticket_count'] for issue in selected_subtopic['common_issues'])

    # Use columns to place subcategory heading and sort button side by side
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"{selected_subtopic['subtopic_label']} ({total_tickets} total tickets)")
    with col2:
        if st.button("⬆️ Sort" if st.session_state.sort_ascending else "⬇️ Sort"):
            st.session_state.sort_ascending = not st.session_state.sort_ascending

    # Sort issues based on the toggle state
    issues = selected_subtopic['common_issues']
    issues = sorted(issues, key=lambda x: x['ticket_count'], reverse=not st.session_state.sort_ascending)

    for idx, issue in enumerate(issues, start=1):
        if (
            (common_issue_filter == "All" or issue['issue'] == common_issue_filter) and
            (responsible_department_filter == "All" or issue.get('responsible_department', 'Unknown') == responsible_department_filter)
        ):
            bg_color = "#f9f9f9" if idx % 2 == 0 else "#e9e9e9"
            st.markdown(
                f"""
                <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px;">
                    <h4>{idx}. {issue['issue']} ({issue['ticket_count']} tickets)</h4>
                    <p>{issue['issue_description']}</p>
                    <p><b>Responsible Department:</b> {issue['responsible_department']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("View Tickets"):
                for ticket in issue['tickets']:
                    st.markdown(f"**State:** {ticket['state']}")
                    st.markdown(f"**Read Status:** {ticket['read']}")
                    st.markdown(f"**Priority:** {ticket['priority']}")
                    st.markdown(f"**Sentiment:** {ticket['sentiment']}")
                    st.markdown(f"**Summary:** {ticket['summary']}")
                    st.markdown(f"[View Details]({ticket['link']})")
                    st.markdown("---")
