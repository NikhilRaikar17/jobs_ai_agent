import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime
import pandas as pd

# Define database connection using SQLAlchemy
DB_FILE = "sqlite:///jobs.db"
engine = create_engine(DB_FILE)

# Fake user credentials (Replace with a database in production)
USER_CREDENTIALS = {
    "admin": "megha",
    "megha": "megha"
}

# Function to fetch job listings


def fetch_jobs():
    """Fetch job listings from the database using SQLAlchemy."""
    query = text("SELECT * FROM jobs ORDER BY date_posted DESC")
    with engine.connect() as conn:
        result = conn.execute(query)
        jobs = result.fetchall()

    columns = result.keys()
    df = pd.DataFrame(jobs, columns=columns)

    if "date_posted" in df.columns:
        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
        df = df.dropna(subset=["date_posted"])

    return df


# Function to get unique values for filters
def get_unique_values(column):
    """Get unique values from a column for dropdown filters."""
    query = text(f"SELECT DISTINCT {column} FROM jobs WHERE {
                 column} IS NOT NULL ORDER BY {column} ASC")
    with engine.connect() as conn:
        result = conn.execute(query)
        values = [row[0] for row in result.fetchall()]
    return values


# **Login Page**
def login():
    """Simple login function to authenticate users."""
    st.title("🔒 Login to Job Listings Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! 🎉")
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

# **Logout Function**


def logout():
    """Logs out the user by clearing session state."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


# **Initialize Streamlit session state for authentication**
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# **If not authenticated, show login page**
if not st.session_state.authenticated:
    login()
    st.stop()  # Stop execution until user logs in

# **Main Dashboard (Only visible after login)**
st.set_page_config(page_title="Job Listings Dashboard", layout="wide")

st.title("📊 Job Listings Dashboard")
st.markdown(f"### Welcome, **{st.session_state.username}**!")

# **Logout Button**
if st.button("🚪 Logout"):
    logout()

# **Refresh Button**
if "refresh" not in st.session_state:
    st.session_state.refresh = False

if st.button("🔄 Refresh Job Listings"):
    st.session_state.refresh = not st.session_state.refresh

# **Load jobs from the database**
df = fetch_jobs()

# **Sidebar filters**
st.sidebar.header("🔍 Filter Jobs")

# Dropdown filters (using SQL queries)
job_titles = get_unique_values("title")
selected_title = st.sidebar.selectbox("Select Job Title", ["All"] + job_titles)

companies = get_unique_values("company")
selected_company = st.sidebar.selectbox("Select Company", ["All"] + companies)

locations = get_unique_values("location")
selected_location = st.sidebar.selectbox(
    "Select Location", ["All"] + locations)

# Date filter (min & max dates)
if not df.empty:
    min_date = df["date_posted"].min().date(
    ) if not df.empty else datetime.today().date()
    max_date = df["date_posted"].max().date(
    ) if not df.empty else datetime.today().date()
    selected_date = st.sidebar.slider(
        "Filter by Date", min_date, max_date, (min_date, max_date))

# Apply filters using SQLAlchemy
filtered_query = "SELECT * FROM jobs WHERE 1=1"
filters = {}

if selected_title != "All":
    filtered_query += " AND title = :title"
    filters["title"] = selected_title

if selected_company != "All":
    filtered_query += " AND company = :company"
    filters["company"] = selected_company

if selected_location != "All":
    filtered_query += " AND location = :location"
    filters["location"] = selected_location

filtered_query += " AND date_posted BETWEEN :start_date AND :end_date"
filters["start_date"] = selected_date[0]
filters["end_date"] = selected_date[1]

# Execute filtered query
with engine.connect() as conn:
    result = conn.execute(text(filtered_query), filters)
    filtered_jobs = result.fetchall()

columns = result.keys()
filtered_df = pd.DataFrame(filtered_jobs, columns=columns)

# **Display results**
st.write(f"### Showing {len(filtered_df)} job listings")

if not filtered_df.empty:
    # Make job titles clickable
    def make_clickable(job_url, title):
        return f'<a href="{job_url}" target="_blank">{title}</a>'

    filtered_df["title"] = filtered_df.apply(
        lambda row: make_clickable(row["job_url"], row["title"]), axis=1)

    if "description" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=["description"])

    # Hide index and format table
    st.markdown(filtered_df.to_html(
        escape=False, index=False), unsafe_allow_html=True)
else:
    st.warning("No job listings found for the selected filters.")

st.markdown("---")
st.markdown("### Built with ❤️ using Streamlit and SQLAlchemy")
