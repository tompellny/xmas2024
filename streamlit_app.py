import streamlit as st
import pandas as pd
from datetime import date
import os

# Set CSV file path
CSV_PATH = "assets/ideas.csv"

# Load ideas from CSV with pipe separator, or create an empty DataFrame if it doesn't exist
def load_ideas():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH, sep="|")
    else:
        ideas_df = pd.DataFrame(columns=["Name", "Idea", "Date"])
        ideas_df.to_csv(CSV_PATH, sep="|", index=False)
        return ideas_df

# Save ideas to CSV with pipe separator
def save_ideas(ideas_df):
    ideas_df.to_csv(CSV_PATH, sep="|", index=False)

# Load existing ideas
ideas_df = load_ideas()

# Sidebar for idea entry form
st.sidebar.header("Neue Geschenkidee")

# Dropdown for names
names = ["Sa", "Su", "San"]
selected_name = st.sidebar.selectbox("Wenn ich ... wäre,", names)

# Text input for the idea
idea_text = st.sidebar.text_area("würde ich mir das wünschen:")

# Submit button
if st.sidebar.button("Submit"):
    if idea_text.strip() != "":
        new_idea = {
            "Name": selected_name,
            "Idea": idea_text,
            "Date": date.today().strftime("%Y-%m-%d")
        }
        ideas_df = pd.concat([ideas_df, pd.DataFrame([new_idea])], ignore_index=True)
        save_ideas(ideas_df)
        st.sidebar.success("Idea submitted successfully!")
    else:
        st.sidebar.error("Please enter an idea before submitting.")

# Sidebar - Delete Idea
st.sidebar.header("Geschenkidee löschen")
if not ideas_df.empty:
    delete_index = st.sidebar.selectbox("Idee auswählen", ideas_df.index, key="delete_index")
    if st.sidebar.button("Löschen", key="delete_button"):
        ideas_df = ideas_df.drop(delete_index).reset_index(drop=True)
        save_ideas(ideas_df)
        st.sidebar.success("Idea deleted successfully!")
else:
    st.sidebar.write("No ideas to delete.")

# Display all submitted ideas in the main section
st.header("Geschenkideen")
st.dataframe(ideas_df)