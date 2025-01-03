import streamlit as st
import requests
import json

# Define your Google Drive file ID
file_id = "1icr6nxHP-KHB8q42ln5dUublWTWUvBJI"

# Construct the download URL
file_url = f"https://drive.google.com/uc?id={file_id}"

# Fetch the file content
response = requests.get(file_url)
if response.status_code == 200:
    data = response.json()
else:
    st.error("Failed to load the sensitive file from Google Drive.")
    st.stop()

# Streamlit layout
st.title("HyperSight Dashboard")
st.sidebar.header("Filters")

# Category filter
categories = list(set(item['category'] for item in data))
category_filter = st.sidebar.selectbox("Select Category", categories)

# Subtopic label filter (dynamically updates based on selected category)
filtered_subtopics = [
    item['subtopic_label'] for item in data if item['category'] == category_filter
]
subtopic_label_filter = st.sidebar.selectbox("Select Subtopic Label", filtered_subtopics)

# Common issues filter (dynamically updates based on selected subtopic label)
filtered_common_issues = []
for item in data:
    if item['category'] == category_filter and item['subtopic_label'] == subtopic_label_filter:
        filtered_common_issues = [issue['issue'] for issue in item['common_issues']]
        break

common_issue_filter = st.sidebar.selectbox("Select Common Issue", ["All"] + filtered_common_issues)

# Urgency filter
urgencies = ["All"]
for item in data:
    if item['category'] == category_filter and item['subtopic_label'] == subtopic_label_filter:
        urgencies.extend([issue.get('urgency', 'Unknown') for issue in item['common_issues']])
        break
urgency_filter = st.sidebar.selectbox("Select Urgency", ["All"] + list(set(urgencies)))

# Responsible department filter
departments = ["All"]
for item in data:
    if item['category'] == category_filter and item['subtopic_label'] == subtopic_label_filter:
        departments.extend([issue.get('responsible_department', 'Unknown') for issue in item['common_issues']])
        break
responsible_department_filter = st.sidebar.selectbox("Select Responsible Department", ["All"] + list(set(departments)))

# Display filtered data
for item in data:
    if item['category'] == category_filter and item['subtopic_label'] == subtopic_label_filter:
        st.header(item['subtopic_label'])

        for issue in item['common_issues']:
            if (
                (common_issue_filter == "All" or issue['issue'] == common_issue_filter) and
                (urgency_filter == "All" or issue.get('urgency', 'Unknown') == urgency_filter) and
                (responsible_department_filter == "All" or issue.get('responsible_department', 'Unknown') == responsible_department_filter)
            ):
                st.subheader(f"{issue['issue']} ({issue['ticket_count']} tickets)")
                st.write(issue['description'])
                st.markdown(f"**Urgency:** {issue.get('urgency', 'Unknown')}")
                st.markdown(f"**Urgency Justification:** {issue.get('urgency_justification', 'No justification available')}")
                st.markdown(f"**Responsible Department:** {issue['responsible_department']}")
                st.markdown(f"**Responsible Department Justification:** {issue.get('responsible_department_justification', 'No justification available')}")
                
                with st.expander("View Tickets"):
                    for ticket in issue['tickets']:
                        st.markdown(f"**State:** {ticket['state']}")
                        st.markdown(f"**Read_Status:** {ticket['read']}")
                        st.markdown(f"**Priority:** {ticket['priority']}")
                        st.markdown(f"**Sentiment:** {ticket['sentiment']}")
                        st.markdown(f"**Summary:** {ticket['summary']}")
                        st.markdown(f"[View Details]({ticket['link']})")
                        st.markdown("---")
