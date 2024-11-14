import streamlit as st
import pandas as pd
from datetime import date
import os

# Define your password
PASSWORD = "lassmichrein"

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Authentication function
def authenticate(password):
    if password == PASSWORD:
        st.session_state.logged_in = True
    else:
        st.error("Hoppla, Passwort falsch. Ab hier geht's für dich nicht weiter.")

# Display the password input and authenticate if not logged in
if not st.session_state.logged_in:
    password = st.text_input("Bitte Passwort eingeben:", type="password")
    if st.button("Lass mich rein"):
        authenticate(password)

else:
    # Set CSV file path
    CSV_PATH = "assets/ideas.csv"

    # Load ideas from CSV with pipe separator, or create an empty DataFrame if it doesn't exist
    def load_ideas():
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH, sep="|")
        else:
            ideas_df = pd.DataFrame(columns=["Beschenkte", "Geschenkidee", "Link", "Datum", "Favorit"])
            ideas_df.to_csv(CSV_PATH, sep="|", index=False)
            return ideas_df

    # Save ideas to CSV with pipe separator
    def save_ideas(ideas_df):
        ideas_df.to_csv(CSV_PATH, sep="|", index=False)

    # Load existing ideas
    ideas_df = load_ideas()

    # Sidebar for idea entry form
    st.sidebar.header("Geschenkidee hinzufügen")

    # Dropdown for names
    names = ["Alma", "Antonia", "Elva", "Eva",  "Lotte", "Marla", "Ol", "Sabine", "Sandra", "Smilla", "Sophia", "Susanne", "Tho"]
    selected_name = st.sidebar.selectbox("Also wenn ich ... wäre,", names)

    # Text input for the idea
    idea_text = st.sidebar.text_area("dann würde ich mir ... wünschen:")
    idea_url = st.sidebar.text_input("Link:")

    # Submit button
    if st.sidebar.button("Idee hinzufügen"):
        if idea_text.strip() != "":
            new_idea = {
                "Beschenkte": selected_name,
                "Geschenkidee": idea_text,
                "Link": idea_url,
                "Datum": date.today().strftime("%Y-%m-%d")
            }
            ideas_df = pd.concat([ideas_df, pd.DataFrame([new_idea])], ignore_index=True)
            save_ideas(ideas_df)
            st.sidebar.success("Merci für die tolle Geschenkidee!")
        else:
            st.sidebar.error("Bitte gib eine Geschenkidee ein, bevor du auf «Hinzufügen» klickst.")

    # Sidebar - Delete Idea
    st.sidebar.header("Geschenkidee löschen")
    if not ideas_df.empty:
        # Create a list of options displaying the index and first 15 characters of each idea
        delete_options = [f"{idx} — {row['Geschenkidee'][:15]} ..." for idx, row in ideas_df.iterrows()]
        
        # Use the formatted options in the dropdown and map the selected option back to the original index
        selected_option = st.sidebar.selectbox("Select idea to delete", delete_options, key="delete_index")
        delete_index = int(selected_option.split(" — ")[0])  # Extract the index number from the selected option
    
        if st.sidebar.button("Weg damit", key="delete_button"):
            ideas_df = ideas_df.drop(delete_index).reset_index(drop=True)
            save_ideas(ideas_df)
            st.sidebar.success("Ok, Geschenkidee gelöscht!")
    else:
        st.sidebar.write("Es gibt noch keine Geschenkideen zu löschen.")

    # Display all submitted ideas in the main section
    st.image("assets/xmas.png", width=300)
    st.header("Alle Geschenkideen")

    popover = st.popover("Filtern")
    selected_name = popover.selectbox("Hier auswählen", ["alle"] + names)

    if selected_name == "alle":
        ideas_df_filtered = ideas_df
    else:
        ideas_df_filtered = ideas_df[ideas_df['Beschenkte'] == selected_name]

    st.dataframe(
        ideas_df_filtered,
        column_config={
            "Link": st.column_config.LinkColumn(),
            "Datum": st.column_config.TextColumn("Hinzugefügt am"),
        }
    )