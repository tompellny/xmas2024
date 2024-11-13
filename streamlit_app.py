import streamlit as st
import pandas as pd
from datetime import date
import os

# Define your password
PASSWORD = "happy"

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Authentication function
def authenticate(password):
    if password == PASSWORD:
        st.session_state.logged_in = True
    else:
        st.error("Incorrect password")

# Display the password input and authenticate if not logged in
if not st.session_state.logged_in:
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        authenticate(password)

else:
    # Your main app code here
    st.write("Welcome to the protected app!")
    # Add more content that should be displayed after login

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