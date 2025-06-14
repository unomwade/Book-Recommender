import streamlit as st
import duckdb
import os

from recommender import LibraryRecommender  # Your module containing the LibraryRecommender
from dotenv import load_dotenv

# 1. Load environment variables (for OPENAI_API_KEY, etc.)
load_dotenv()

# 2. Connect to the DuckDB database
db_path = "./data/library_db.duckdb"
con = duckdb.connect(db_path)

###############################################################################
# Database interaction functions
###############################################################################

def add_user_to_db(name: str, email: str, address: str):
    """Insert a new user record into the DuckDB 'users' table."""
    # Get the max user_id from 'users'; if table empty, default to 0
    df_max = con.execute("SELECT COALESCE(MAX(user_id), 0) FROM users").fetchdf()
    max_user_id = df_max.iloc[0, 0] if not df_max.empty else 0
    new_user_id = max_user_id + 1

    # Insert the new user
    con.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        (int(new_user_id), name, email, address)
    )

def add_book_to_db(title: str, author: str, genre: str, description: str):
    """Insert a new book record into the DuckDB 'books' table."""
    # Get the max book_id from 'books'; if table empty, default to 0
    df_max = con.execute("SELECT COALESCE(MAX(book_id), 0) FROM books").fetchdf()
    max_book_id = df_max.iloc[0, 0] if not df_max.empty else 0
    new_book_id = max_book_id + 1

    con.execute(
        "INSERT INTO books VALUES (?, ?, ?, ?, ?)",
        (int(new_book_id), title, author, genre, description)
    )

def add_checkout_to_db(user_id: int, book_id: int):
    """Insert a new checkout record into the DuckDB 'checkouts' table."""
    con.execute(
        "INSERT INTO user_checkouts VALUES (?, ?)",
        (int(user_id), int(book_id))
    )

def get_user_id(user_name: str) -> int:
    """Get the user ID from the 'users' table given a user name."""
    df = con.execute(
        f"SELECT user_id FROM users WHERE name = '{user_name}'"
    ).fetchdf()

    if df.empty:
        raise ValueError(f"User '{user_name}' not found in the database.")

    return int(df.iloc[0, 0])

def get_book_id(book_title: str) -> int:
    """Get the book ID from the 'books' table given a book title."""
    df = con.execute(
        f"SELECT book_id FROM books WHERE title = '{book_title}'"
    ).fetchdf()

    if df.empty:
        raise ValueError(f"Book '{book_title}' not found in the database.")

    return int(df.iloc[0, 0])

def get_user_email(user_id: int) -> str:
    """Get the email address of a user from the 'users' table."""
    df = con.execute(
        f"SELECT email FROM users WHERE user_id = {user_id}"
    ).fetchdf()

    if df.empty:
        raise ValueError(f"User ID '{user_id}' not found in the database.")

    return df.iloc[0, 0]

###############################################################################
# Email sending function(s)
###############################################################################

def send_email(to_email: str, subject: str, body: str):
    # Placeholder function for sending an email
    return {"to": to_email, "subject": subject, "body": body}

def get_user_email(user_id: int) -> str:
    """
    Retrieves the email of a user given their user ID.
    """
    df = con.execute(f"SELECT email FROM users WHERE user_id = {user_id}").fetchdf()
    if df.empty:
        raise ValueError("No email found for this user.")
    return df.iloc[0]["email"]

###############################################################################
# Initialize the LibraryRecommender
###############################################################################
openai_api_key = os.getenv("OPENAI_API_KEY")
recommender = LibraryRecommender(
    openai_api_key=openai_api_key,
    model_name="gpt-4o-mini",
    temperature=0.15,
    max_tokens=500,
    duckdb_pth=db_path
)

def main():
    st.set_page_config(page_title="Library Recommendation Demo", layout="wide")
    st.title("Library Recommendation Demo (LangChain + Streamlit)")

    ###########################################################################
    # Add a new user
    ###########################################################################
    st.header("Add a New User")
    with st.form(key="add_user_form", clear_on_submit=True):
        col_user_name, col_user_email, col_user_address = st.columns(3)
        with col_user_name:
            user_name_input = st.text_input("Name")
        with col_user_email:
            user_email_input = st.text_input("Email")
        with col_user_address:
            user_address_input = st.text_input("Address")

        submitted_user = st.form_submit_button("Add User")
        if submitted_user:
            if user_name_input and user_email_input:
                try:
                    add_user_to_db(user_name_input, user_email_input, user_address_input)
                    st.success(f"User '{user_name_input}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding user: {e}")
            else:
                st.error("Please enter both a name and an email address.")

    # Display current users
    st.subheader("Current Users")
    df_users = con.execute("SELECT * FROM users").fetchdf()
    if not df_users.empty:
        st.dataframe(df_users)
    else:
        st.write("No users in the system yet.")

    ###########################################################################
    # Add a new book to the catalog
    ###########################################################################
    st.header("Add a New Book to the Catalog")
    with st.form(key="add_book_form", clear_on_submit=True):
        col_title, col_author, col_genre = st.columns(3)
        with col_title:
            title_input = st.text_input("Book Title")
        with col_author:
            author_input = st.text_input("Author")
        with col_genre:
            genre_input = st.text_input("Genre")
        description_input = st.text_area("Description")

        submitted_book = st.form_submit_button("Add Book")
        if submitted_book:
            if title_input and author_input:
                try:
                    add_book_to_db(title_input, author_input, genre_input, description_input)
                    st.success(f"Book '{title_input}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding book: {e}")
            else:
                st.error("Please enter at least a title and author.")

    # Display current catalog
    st.subheader("Current Catalog in the System")
    df_books = con.execute("SELECT * FROM books").fetchdf()
    if not df_books.empty:
        st.dataframe(df_books)
    else:
        st.write("No books in the catalog yet.")

    ###########################################################################
    # Get a Recommendation and Send Email
    ###########################################################################
    st.header("Ask the Library Assistant for Recommendations")
    user_names = df_users["name"].tolist() if not df_users.empty else []

    if user_names:
        with st.expander("Generate Recommendation"):
            user_for_recs = st.selectbox("Select a user for recommendations", options=user_names, key="user_for_recs")
            user_query = st.text_area("Enter your question or reading preference here", key="user_query")

            if st.button("Get Recommendations", key="generate_recs"):
                if user_query.strip():
                    with st.spinner("Generating recommendations..."):
                        try:
                            # Generate recommendation and store it in session_state
                            rec = recommender.generate_recommendation(
                                user_name=user_for_recs,
                                user_input=user_query
                            )
                            st.session_state["recommendation"] = rec  # Save the recommendation to session state
                            st.success("Recommendation generated successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")

            # Display the recommendation if it exists in session state
            if "recommendation" in st.session_state:
                rec = st.session_state["recommendation"]

                st.write("**Recommendation:**")
                st.write(f"**Title:** {rec.title}")
                st.write(f"**Book ID:** {rec.book_id}")
                st.write(f"**Synopsis:** {rec.synopsis}")
                st.write(f"**Why You Might Like It:** {rec.feedback}")
                st.write(f"**User Grade:** {rec.grade}")

                # Send the email
                if st.button("Send Recommendation via Email", key="send_email"):
                    try:
                        user_id = get_user_id(user_for_recs)
                        user_email = get_user_email(user_id)
                        email_body = f"""
                        Hi {user_for_recs},

                        Based on your interests, we recommend the following book:

                        Title: {rec.title}
                        Synopsis: {rec.synopsis}
                        Why You'll Like It: {rec.feedback}

                        Happy Reading!
                        """
                        if send_email(user_email, "Your Library Recommendation", email_body):
                            st.success(f"Email sent to {user_email} successfully!")
                            st.write("Email Body:" + email_body)
                        else:
                            st.error("Failed to send the email.")
                    except Exception as e:
                        st.error(f"Error sending email: {e}")

                # Checkout the book
                if st.button("Checkout Book", key="checkout_book"):
                    try:
                        book_id = get_book_id(rec.title)
                        user_id = get_user_id(user_for_recs)
                        add_checkout_to_db(user_id, book_id)
                        st.success(f"Book '{rec.title}' checked out successfully!")
                    except Exception as e:
                        st.error(f"Error checking out book: {e}")


if __name__ == "__main__":
    main()