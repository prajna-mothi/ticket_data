import streamlit as st
import json
import requests
import json
import pandas as pd


# Construct the download URL
file_url = f"https://drive.google.com/uc?id=1RZyX1RV7Iqg3OgVxue644pI89v-PNEEB"

# Fetch the file content
response = requests.get(file_url)
if response.status_code == 200:
    data = response.json()
else:
    st.error("Failed to load the sensitive file from Google Drive.")


# Load JSON data
# json_file_path = '/Users/prajnamothi/Documents/HyperSight/Greenely/all_data.json' # Your JSON file name

# # Load the JSON into a DataFrame
# with open(json_file_path, "r", encoding="utf-8") as f:
#     data_from_json = json.load(f)

df = pd.DataFrame(data)

# Streamlit App
st.title("HyperSight Dashboard")

# Sidebar Content
st.sidebar.header("Dashboard Information")

# Add a filter for report periods
report_periods = sorted(df["report_period"].unique())
selected_report_period = st.sidebar.selectbox("Report Period", report_periods)

# Filter the DataFrame by report period
filtered_df = df[df["report_period"] == selected_report_period]

# Calculate the total number of tickets based on the filtered DataFrame
total_tickets = len(filtered_df)

# Display total tickets in the sidebar
st.sidebar.markdown(f"**Total Tickets:** {total_tickets}")

# Sidebar Filters
st.sidebar.header("Filters")

# Add ticket counts to the categories
category_counts = filtered_df["category"].value_counts()
categories_with_counts = [
    (category, count) for category, count in category_counts.items()
]

# Reorder to place "Batterier" at the top and "Andra" at the bottom
categories_with_counts = sorted(
    categories_with_counts, key=lambda x: (x[0] != "Batterier", x[0] == "Andra", x[0])
)

categories_display = [
    f"{category} ({count} tickets)" for category, count in categories_with_counts
]
categories = [category for category, _ in categories_with_counts]

selected_category_display = st.sidebar.selectbox(
    "Category",
    categories_display,
)
selected_category = categories[categories_display.index(selected_category_display)]

# Add ticket counts to the subcategories
subcategory_counts = (
    filtered_df[filtered_df["category"] == selected_category]["subcategory"].value_counts()
)
subcategories_display = [
    f"{subcategory} ({count} tickets)" for subcategory, count in subcategory_counts.items()
]
subcategories = [subcategory for subcategory in subcategory_counts.index]

selected_subcategory_display = st.sidebar.selectbox(
    "Subcategory",
    subcategories_display,
)
selected_subcategory = subcategories[subcategories_display.index(selected_subcategory_display)]

# Responsible Department Filter
responsible_department = st.sidebar.selectbox(
    "Responsible Department",
    ["All"] + sorted(filtered_df["responsible_department"].unique()),
)

# Filter further based on category, subcategory, and responsible department
filtered_df = filtered_df[
    (filtered_df["category"] == selected_category)
    & (filtered_df["subcategory"] == selected_subcategory)
]
if responsible_department != "All":
    filtered_df = filtered_df[filtered_df["responsible_department"] == responsible_department]

# Add a toggle button for sorting
sort_ascending = st.sidebar.checkbox("Sort by Ticket Volume (Ascending)")

# Display Dashboard Content
if not filtered_df.empty:
    # Count tickets for each common issue and sort based on toggle button
    common_issue_counts = filtered_df["common_issue"].value_counts()
    sorted_common_issues = common_issue_counts.sort_values(
        ascending=sort_ascending
    ).index

    # Display sorted common issues
    st.markdown(f"### Subcategory: {selected_subcategory} ({len(filtered_df)} total tickets)")
    for common_issue in sorted_common_issues:
        group = filtered_df[filtered_df["common_issue"] == common_issue]
        st.markdown(f"#### Common Issue: {common_issue} ({len(group)} tickets)")

        # Include issue_summary, responsible_department, justification
        st.markdown(f"**Issue Summary:** {group['issue_summary'].iloc[0]}")
        st.markdown(f"**Responsible Department:** {group['responsible_department'].iloc[0]}")
        st.markdown(f"**Justification:** {group['responsible_department_justification'].iloc[0]}")

        # Expandable section for tickets
        with st.expander("View Tickets"):
            for _, row in group.iterrows():
                st.markdown(f"**Ticket Issue:** {row['issue']}")
                st.markdown(f"**Summary:** {row['summary']}")
                st.markdown(f"**Sentiment:** {row['sentiment']}")
                st.markdown(f"**State:** {row['state']}")
                st.markdown(f"**Read Status:** {row['read']}")
                st.markdown(f"**Priority:** {row['priority']}")
                st.markdown(f"[View Details]({row['link']})")
                st.markdown("---")  # Divider between tickets
else:
    st.write("No tickets found for the selected filters.")
