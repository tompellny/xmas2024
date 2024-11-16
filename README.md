A simple app to collect gift ideas.

### How to run it on your own machine

1. Install the requirements
   ```
   $ pip install -r requirements.txt
   ```

2. Run the app
   ```
   $ streamlit run streamlit_app.py
   ```

3. CSV with ideas
Gift ideas are saved to a CSV. The CSV is not pushed to the repo and included in .gitignore
   ```
   assets/ideas.csv
   ```

4. Password
The app requires an initial password. The password is stored in the secrets.toml file and needs to be added to the Streamlit's "App settings | Secrets".
   ```
   [secrets]
   ```
   PASSWORD = "your password"
   ```
