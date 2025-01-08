import streamlit as st
import pandas as pd
import requests
import json

# Define your Google Drive file ID
file_id = "1G6rCx2epI-Bn-FiCPR7v-vcv9WAgmaJE"

# Construct the download URL
file_url = f"https://drive.google.com/uc?id={file_id}"

# Fetch the JSON file content
response = requests.get(file_url)
if response.status_code == 200:
    data = response.json()
else:
    st.error("Failed to load the JSON file from Google Drive.")
    st.stop()
# with open("dashboard_with_tickets.json", "r") as f:
#     data = json.load(f)




# Set page configuration (this must be the first Streamlit command)
st.set_page_config(layout="wide")



# Extract key fields from JSON and convert to a DataFrame
@st.cache_data
def flatten_json(data):
    rows = []
    for entry in data:
        category = entry['category']
        subcategory = entry['subcategory']
        report_period = entry['report_period']
        company_name = entry['company_name']
        ticket_count = entry['ticket_count']
        common_issue_count = entry['common_issue_count']
        for issue in entry['common_issues']:
            issue_mapped = issue['issue_mapped']
            issue_summary = issue['issue_summary']
            responsible_department = issue['responsible_department']
            responsible_department_justification = issue['responsible_department_justification']
            issue_ticket_count = issue['ticket_count']
            for ticket in issue['tickets']:
                rows.append({
                    "category": category,
                    "subcategory": subcategory,
                    "report_period": report_period,
                    "company_name": company_name,
                    "ticket_count": ticket_count,
                    "common_issue_count": common_issue_count,
                    "issue_mapped": issue_mapped,
                    "issue_summary": issue_summary,
                    "responsible_department": responsible_department,
                    "responsible_department_justification": responsible_department_justification,
                    "issue_ticket_count": issue_ticket_count,
                    "ticket_id": ticket['id'],
                    "state": ticket['state'],
                    "read": ticket['read'],
                    "priority": ticket['priority'],
                    "issue": ticket['issue'],
                    "summary": ticket['summary'],
                    "sentiment": ticket['sentiment'],
                    "link": ticket['link'],
                })
    return pd.DataFrame(rows)

# Convert the JSON to a DataFrame
df = flatten_json(data)

# Extract unique values for filters
report_periods = df["report_period"].unique()
categories = df["category"].unique()
company_name = df["company_name"].iloc[0]  # Assuming all rows have the same company name

# Calculate ticket counts for each category
category_ticket_counts = df.groupby("category").size().to_dict()

# Add custom CSS for sticky top section
st.markdown(
    """
    <style>
    .sticky-top {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: white;
        padding: 10px 0;
        z-index: 1000;
        border-bottom: 2px solid #f0f0f0;
    }
    .wide-layout {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sticky Top Section
st.markdown('<div class="sticky-top">', unsafe_allow_html=True)
st.title("HyperSight Dashboard")
st.subheader(company_name)

# Wider layout for filters
st.markdown('<div class="wide-layout">', unsafe_allow_html=True)

# Category Filter with ticket counts displayed
st.markdown('<div style="flex: 1;">', unsafe_allow_html=True)
selected_category = st.radio(
    "Select Category",
    [f"{category} ({category_ticket_counts[category]})" for category in sorted(categories)],
)
# Extract the category name without the ticket count
selected_category = selected_category.split(" (")[0]
st.markdown('</div>', unsafe_allow_html=True)

# Report Period Filter
st.markdown('<div style="flex: 1;">', unsafe_allow_html=True)
report_period_filter = st.selectbox("Report Period", sorted(report_periods))
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Apply Report Period Filter
filtered_df = df[df["report_period"] == report_period_filter]

# Apply Category Filter (mandatory)
filtered_df = filtered_df[filtered_df["category"] == selected_category]

# Group and display details by Subcategory and Issues
if not filtered_df.empty:
    for subtopic, subtopic_group in filtered_df.groupby("subcategory"):
        subtopic_count = len(subtopic_group)  # Calculate total tickets for the subtopic
        st.subheader(f"Subcategory: {subtopic} ({subtopic_count} tickets)")

        # Add a dynamic Responsible Department filter below the Subcategory label
        departments = subtopic_group["responsible_department"].unique()
        selected_department = st.selectbox(
            f"Filter Responsible Department for {subtopic}:", ["All"] + sorted(departments)
        )

        # Apply Responsible Department Filter if not "All"
        if selected_department != "All":
            subtopic_group = subtopic_group[subtopic_group["responsible_department"] == selected_department]

        # Display Issues within the Subcategory
        for issue, issue_group in subtopic_group.groupby("issue_mapped"):
            issue_ticket_count = len(issue_group)  # Calculate ticket count for the issue
            issue_summary = issue_group["issue_summary"].iloc[0]

            # Format issue summary as bullet points
            points = [point.strip() for point in issue_summary.split("\n") if point.strip()]
            formatted_summary = "\n".join(f"- {point}" for point in points)

            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>{issue} ({issue_ticket_count} tickets)</h4>
                    <p><b>Issue Summary:</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(formatted_summary)  # Render bullet points using Markdown

            with st.expander("View Tickets"):
                for _, ticket in issue_group.iterrows():
                    st.markdown(f"**Ticket ID:** {ticket['ticket_id']}")
                    st.markdown(f"**State:** {ticket['state']}")
                    st.markdown(f"**Read Status:** {ticket['read']}")
                    st.markdown(f"**Priority:** {ticket['priority']}")
                    st.markdown(f"**Issue:** {ticket['issue']}")
                    st.markdown(f"**Summary:** {ticket['summary']}")
                    st.markdown(f"**Sentiment:** {ticket['sentiment']}")
                    st.markdown(f"[View Ticket]({ticket['link']})")
                    st.markdown("---")
else:
    st.warning("No data found for the selected filters.")
