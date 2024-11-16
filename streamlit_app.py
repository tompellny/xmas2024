import streamlit as st
import pandas as pd
from datetime import date
from datetime import datetime
import os
import altair as alt

# ---------------- SETTINGS -------------------------------
st.set_page_config(page_title="Weihnachten 2024", layout="wide")


# ---------------- PASSWORD CHECK -------------------------
# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Authentication function
def authenticate(password):
    if password == st.secrets['secrets']['PASSWORD']:
        st.session_state.logged_in = True
        st.rerun()  # Force rerun to apply the new state
    else:
        st.error("Hoppla, Passwort falsch. Ab hier geht's für dich nicht weiter.")

# Display the password input and authenticate if not logged in
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([2, 1, 2])
    col1.write("")
    with col2:
        password = st.text_input("Bitte Passwort eingeben:", type="password")
        if st.button("Lass mich rein"):
            authenticate(password)
    col3.write("")


# ---------------- CSV LOAD AND SAVE ----------------------
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

# ---------------- SIDEBAR TO ADD/DELETE IDEAS ------------------------
    # Sidebar for idea entry form
    st.sidebar.header("Geschenkidee hinzufügen")

    # Dropdown for names
    names = ["Alma", "Antonia", "Elva", "Eva",  "Lotte", "Marla", "Ol", "Sabine", "Sandra", "Smilla", "Sophia", "Susanne", "Tho"]
    selected_name = st.sidebar.selectbox("Wenn ich ... wäre", names)

    # Text input for the idea
    idea_text = st.sidebar.text_area("würde ich mir ... wünschen:")
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
    st.sidebar.write("")
    st.sidebar.write("")  
    st.sidebar.header("Geschenkidee löschen")
    if not ideas_df.empty:
        # Create a list of options displaying the index and first 15 characters of each idea
        delete_options = [f"{idx} — {row['Geschenkidee'][:15]} ..." for idx, row in ideas_df.iterrows()]
        
        # Use the formatted options in the dropdown and map the selected option back to the original index
        selected_option = st.sidebar.selectbox("Zu löschende Geschenkidee wählen:", delete_options, key="delete_index")
        delete_index = int(selected_option.split(" — ")[0])  # Extract the index number from the selected option
    
        if st.sidebar.button("Idee löschen", key="delete_button"):
            ideas_df = ideas_df.drop(delete_index).reset_index(drop=True)
            save_ideas(ideas_df)
            st.sidebar.success("Ok, Geschenkidee gelöscht!")
    else:
        st.sidebar.write("Es gibt noch keine Geschenkideen zu löschen.")


    # ---------------- SHOW IDEAS ---------------------------
    # Display all submitted ideas in the main section
    st.header("Weihnachtsideen 2024")
    st.image("assets/xmas-banner.png", width=350)
    st.write("")
    st.subheader("Unsere Geschenkideen", divider="red")

    selected_names = st.pills("Filtern", names, label_visibility="collapsed", selection_mode="multi")

    if selected_names:
        ideas_df_filtered = ideas_df[ideas_df['Beschenkte'].isin(selected_names)]
    else:
        ideas_df_filtered = ideas_df
    
    st.dataframe(
        ideas_df_filtered,
        use_container_width=True,
        column_config={
            "Link": st.column_config.LinkColumn(),
            "Datum": st.column_config.TextColumn("Hinzugefügt am"),
        }
    )

    # ---------------- DOWNLOAD BUTTON ---------------------------
    # Read the CSV file (if you want to display it or check its existence)
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    try:
        with open("assets/ideas.csv", "r", encoding="utf-8") as file:
            csv_data = file.read()  # Read the raw file content
            st.download_button(
                label="Download Ideen",
                data=csv_data.encode("utf-8"),  # Ensure proper encoding for download
                file_name=f"ideas_{timestamp}.csv",  # Add timestamp to the filename
                mime="text/csv"
            )
    except FileNotFoundError:
        st.error("Hoppla, habe keine Daten zum Download gefunden.")


    # ---------------- SHOW CHART--------------
    st.write("")
    st.subheader("Leader Board", divider="red")
    # Group the data by Name and count the number of ideas
    ideas_per_name = ideas_df.groupby("Beschenkte").size().reset_index(name="Geschenkideen")

    # Create an Altair bar chart
    chart = alt.Chart(ideas_per_name).mark_bar(color="white").encode(
        x=alt.X("Beschenkte", title=""),
        y=alt.Y("Geschenkideen", title="Geschenkideen"),
        tooltip=["Beschenkte", "Geschenkideen"]
    ).properties(
        title="Für wen haben wir am meisten Geschenkideen?",
        width=600,
        height=400
    )

    # Display the chart
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.altair_chart(chart, use_container_width=True)
    col2.write("")
    col3.write("")