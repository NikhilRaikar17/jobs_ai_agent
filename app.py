import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# Define database connection using SQLAlchemy
DB_FILE = "sqlite:///jobs.db"
engine = create_engine(DB_FILE)

# Fake user credentials (Replace with a database in production)
USER_CREDENTIALS = {
    "admin": "password123",
    "megha": "megha"
}

# Function to fetch job listings


def fetch_jobs():
    """Fetch job listings from the database using SQLAlchemy."""
    query = text(
        "SELECT * FROM jobs WHERE applied = 0 ORDER BY date_posted DESC")
    with engine.connect() as conn:
        result = conn.execute(query)
        jobs = result.fetchall()

    columns = result.keys()
    df = pd.DataFrame(jobs, columns=columns)

    if "date_posted" in df.columns:
        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
        df = df.dropna(subset=["date_posted"])

    return df


def update_applied_status(updated_df):
    """Update the applied status in the database based on changes in `st.data_editor`."""
    for index, row in updated_df.iterrows():
        query = text("UPDATE jobs SET applied = :applied WHERE id = :job_id")
        with engine.connect() as conn:
            conn.execute(
                query, {"applied": 1 if row["applied"] == "Yes" else 0, "job_id": row["id"]})
            conn.commit()


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
            st.rerun()  # Refresh page after login
        else:
            st.error("Invalid username or password. Please try again.")

# **Logout Function**


def logout():
    """Logs out the user by clearing session state."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()  # Refresh page after logout


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
# st.sidebar.header("🔍 Filter Jobs")

# job_titles = get_unique_values("title")
# selected_title = st.sidebar.selectbox("Select Job Title", ["All"] + job_titles)

# companies = get_unique_values("company")
# selected_company = st.sidebar.selectbox("Select Company", ["All"] + companies)

# locations = get_unique_values("location")
# selected_location = st.sidebar.selectbox(
#     "Select Location", ["All"] + locations)

# if not df.empty:
#     min_date = df["date_posted"].min().date(
#     ) if not df.empty else datetime.today().date()
#     max_date = df["date_posted"].max().date(
#     ) if not df.empty else datetime.today().date()
#     selected_date = st.sidebar.slider(
#         "Filter by Date", min_date, max_date, (min_date, max_date))

# **Apply filters using SQLAlchemy**
filtered_query = "SELECT * FROM jobs WHERE applied=0 ORDER BY date_posted DESC"
filters = {}

# if selected_title != "All":
#     filtered_query += " AND title = :title"
#     filters["title"] = selected_title

# if selected_company != "All":
#     filtered_query += " AND company = :company"
#     filters["company"] = selected_company

# if selected_location != "All":
#     filtered_query += " AND location = :location"
#     filters["location"] = selected_location

# filtered_query += " AND date_posted BETWEEN :start_date AND :end_date"
# filters["start_date"] = selected_date[0]
# filters["end_date"] = selected_date[1]

# Execute filtered query
with engine.connect() as conn:
    result = conn.execute(text(filtered_query), filters)
    filtered_jobs = result.fetchall()

columns = result.keys()
filtered_df = pd.DataFrame(filtered_jobs, columns=columns)

if "applied" in filtered_df.columns:
    filtered_df["applied"] = filtered_df["applied"].apply(
        lambda x: "Yes" if x == 1 else "No")


# **Pagination Settings**
JOBS_PER_PAGE = 20  # Number of jobs per page

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

total_jobs = len(filtered_df)
total_pages = (total_jobs // JOBS_PER_PAGE) + \
    (1 if total_jobs % JOBS_PER_PAGE > 0 else 0)

start_idx = (st.session_state.current_page - 1) * JOBS_PER_PAGE
end_idx = start_idx + JOBS_PER_PAGE

# **Display results**
st.write(f"### Showing {total_jobs} job listings (Page {
         st.session_state.current_page} of {total_pages})")

if not filtered_df.empty:
    # Apply pagination
    paginated_df = filtered_df.iloc[start_idx:end_idx].copy()

    if "description" in paginated_df.columns:
        paginated_df = paginated_df.drop(columns=["description"])

    if "extracted_csv" in paginated_df.columns:
        paginated_df = paginated_df.drop(columns=["extracted_csv"])

    # # Hide index and format table
    # st.markdown(paginated_df.to_html(
    #     escape=False, index=False), unsafe_allow_html=True)

    edited_df = st.data_editor(
        paginated_df,
        column_config={
            "job_url": st.column_config.LinkColumn(
                display_text=r"APPLY_URL"
            ),
            "company": st.column_config.TextColumn("Company", disabled=True),
            "location": st.column_config.TextColumn("Location", disabled=True),
            "date_posted": st.column_config.DateColumn("Date Posted", disabled=True),
            "applied": st.column_config.SelectboxColumn(
                "Applied",
                options=["Yes", "No"],  # Dropdown values
                required=True,
            ),
        },
        use_container_width=False,
        height=750,
        hide_index=True,
    )

    # **Update database only if changes are detected**
    if not edited_df.equals(paginated_df):
        update_applied_status(edited_df)
        st.success("✅ Applied status updated successfully!")
        st.rerun()  # Refresh the app to reflect changes

    # **Pagination Controls**
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_page > 1:
            if st.button("⬅️ Previous"):
                st.session_state.current_page -= 1
                st.rerun()

    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ➡️"):
                st.session_state.current_page += 1
                st.rerun()
else:
    st.warning("No job listings found for the selected filters.")

st.markdown("---")
st.markdown("### Built with ❤️ using Streamlit and SQLAlchemy")
