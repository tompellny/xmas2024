import streamlit as st
import pandas as pd
from datetime import date
from datetime import datetime
import os
import altair as alt
from streamlit_gsheets import GSheetsConnection

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


# ---------------- LOGIN SUCCESS ----------------------
else:
    # ---------------- GSHEET CONNECTION ----------------------
    # Create a GSheets connection object
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        ideas_df = conn.read(worksheet=st.secrets['sheets']['GS_IDEAS'], usecols=list(range(4)), ttl=5)
    except Exception as e:
        st.error(f"Hoppla, Fehler beim Laden der Google Sheets Daten: {e}")
        st.stop()

    ideas_df = ideas_df.dropna(how="all")

# ---------------- SIDEBAR TO ADD/DELETE IDEAS ------------------------
    # Sidebar for idea entry form
    st.sidebar.header("Geschenkidee hinzufügen")

    # Dropdown for names
    names = ["Alma", "Antonia", "Elva", "Eva",  "Lotte", "Marla", "Ol", "Sabine", "Sandra", "Smilla", "Sophia", "Susanne", "Tho"]
    selected_name = st.sidebar.selectbox("Wenn ich ... wäre", names, index=None, placeholder="Beschenkte(n) wählen...")

    # Text input for the idea
    idea_text = st.sidebar.text_area("würde ich mir ... wünschen:")
    idea_url = st.sidebar.text_input("Link (optional):")

    # Submit button
    if st.sidebar.button("Idee hinzufügen"):
        if idea_text.strip() != "":
            new_idea = pd.DataFrame([{
                                    "Beschenkte": selected_name,
                                    "Geschenkidee": idea_text,
                                    "Link": idea_url,
                                    "Datum": date.today().strftime("%Y-%m-%d"),
                                    }])
            ideas_df = pd.concat([ideas_df, new_idea], ignore_index=True)
            # Update the Google Sheet with the merged data
            conn.update(worksheet=st.secrets['sheets']['GS_IDEAS'], data=ideas_df)
            st.sidebar.success("Merci für die tolle Geschenkidee!")
        else:
            st.sidebar.error("Bitte gib eine Geschenkidee ein, bevor du auf «Hinzufügen» klickst.")

    # Sidebar - Delete Idea
    st.sidebar.write("")
    st.sidebar.write("")  
    st.sidebar.header("Geschenkidee löschen")
    if not ideas_df.empty:
        # Create a list of options displaying the index and first 15 characters of each idea
        delete_options = [f"{idx} — {row['Geschenkidee'][:20]} ..." for idx, row in ideas_df.iterrows()]
        
        # Use the formatted options in the dropdown and map the selected option back to the original index
        selected_option = st.sidebar.selectbox("Zu löschende Geschenkidee wählen:", delete_options, key="delete_index")
        delete_index = int(selected_option.split(" — ")[0])  # Extract the index number from the selected option
    
        if st.sidebar.button("Idee löschen", key="delete_button"):
            ideas_df = ideas_df.drop(delete_index).reset_index(drop=True)
            conn.update(worksheet=st.secrets['sheets']['GS_IDEAS'], data=ideas_df)
            st.sidebar.success("Ok, Geschenkidee gelöscht!")
    else:
        st.sidebar.write("Es gibt noch keine Geschenkideen zu löschen.")


    # ---------------- SHOW IDEAS ---------------------------
    # Display all submitted ideas in the main section
    #st.subheader("Weihnachtsgeschenkideen 2024")
    st.image("assets/xmas-banner.png", width=400)
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
        },
        height=500,
    )

    
    # ---------------- SHOW CHART--------------
    st.write("")
    st.subheader("Leader Board", divider="red")
    # Group the data by Name and count the number of ideas
    ideas_per_name = ideas_df.groupby("Beschenkte").size().reset_index(name="Geschenkideen")

    # Create an Altair bar chart
    chart = alt.Chart(ideas_per_name).mark_bar(color="white").encode(
        x=alt.X("Beschenkte", title=""),
        y=alt.Y("Geschenkideen", title="Geschenkideen", axis=alt.Axis(format='d')),  # Force integer format
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
