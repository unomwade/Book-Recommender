from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

import duckdb
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

###############################################################################
##### Define your structured output model for the recommendation response #####
###############################################################################
class Recommendation(BaseModel):
    title: str = Field(..., title="The title of the book")
    book_id: int = Field(..., title="Parse unique identifier of the book")
    feedback: str = Field(..., title="The feedback for the book and why it was recommended")
    grade: int = Field(
        ...,
        title="The grade of the book recommendation, based on prior checkouts, 0 to 100",
    )
    summarized_email_body: str = Field(..., title="The summarized email body to send to the user")
    synopsis: str = Field(..., title="A brief synopsis of the recommended book")

###############################################################################
################## Load environment variables and setup #######################
###############################################################################
load_dotenv()  # Make sure you have a .env with OPENAI_API_KEY, etc.

###############################################################################
#################### Library Recommender Class Definition #####################
###############################################################################
class LibraryRecommender:
    def __init__(
        self, 
        openai_api_key: str,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.15,
        max_tokens: int = 500,
        duckdb_pth: str = "./data/library_db.duckdb"
    ):
        """
        Initialize the LibraryRecommender with a DuckDB connection,
        a ChatOpenAI model, and a prompt template.
        """

        # Set up an LLM for recommendations
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        ).with_structured_output(Recommendation)  # structured output to match Recommendation model

        # Connect to DuckDB
        self.db = duckdb.connect(duckdb_pth)

        # Define a prompt template for recommendations
        self.recommendation_prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful library assistant who recommends books based on user tastes. 
            The user is looking for help with: "{user_input}"

            Below is a list of available books in the library's catalog (books not checked out yet):
            {catalog}

            The user has previously checked out the following books:
            {checkouts}

            Suggest 1 book (from the catalog) that might be relevant or interesting for the user. 
            Explain your recommendation, provide a rating (0-100), summarize an email to the user, 
            and give a brief synopsis of the book. 
            """)

    def get_user_id(self, user_name: str) -> str:
        """
        Get the user_id from the 'users' table based on the user's name.
        NOTE: This uses string interpolation for demo purposes;
        in production, consider parameterized queries to avoid SQL injection.
        """
        df = self.db.execute(
            f"SELECT user_id FROM users WHERE name = '{user_name}'"
        ).fetchdf()

        if df.empty:
            raise ValueError(f"User '{user_name}' not found in the database.")

        return df.iloc[0, 0]

    def get_user_checkouts(self, user_id: str) -> pd.DataFrame:
        """
        Get the books checked out by a user from the 'checkouts' table.
        """
        df = self.db.execute(
            f"SELECT b.* FROM user_checkouts uc RIGHT JOIN books b ON uc.book_id = b.book_id WHERE user_id = '{user_id}'"
        ).fetchdf()
        return df

    def get_catalog_as_text(self) -> str:
        """
        Converts the book catalog from DuckDB into a textual list.
        - Filters out books that are already checked out.
        """
        df_books = self.db.execute(
            f"SELECT * FROM books WHERE book_id NOT IN (SELECT book_id FROM user_checkouts WHERE user_id = {self.user_id})"
        ).fetchdf()
        if df_books.empty:
            return "No books in the catalog yet. Or all books are checked out for user."
        
        lines = []
        for _, row in df_books.iterrows():
            line = (
                f"- Title: {row['title']}, Book_id: {row['book_id']}, Author: {row['author']}, "
                f"Genre: {row['genre']}, Desc: {row['description']}"
            )
            lines.append(line)
        return "\n".join(lines)

    def _format_checkouts_as_text(self, df_checkouts: pd.DataFrame) -> str:
        """
        Takes a DataFrame of checkouts and formats them as a simple text list.
        """
        if df_checkouts.empty:
            return "No previous checkouts."
        
        lines = []
        for _, row in df_checkouts.iterrows():
            lines.append(f"- Book ID: {row['book_id']}, Title: {row['title']}, Author: {row['author']}")
        return "\n".join(lines)

    def create_chain(self):
        """
        Create an Chain for generating recommendations from the prompt.
        """
        return self.recommendation_prompt | self.llm

    def generate_recommendation(self, user_name: str, user_input: str) -> Recommendation:
        """
        Generates a recommendation using the user's name, their query, 
        and the current catalog of books. 
        Returns a Recommendation object as defined by the Pydantic model.
        """
        self.user_id = self.get_user_id(user_name)
        catalog_text = self.get_catalog_as_text()
        user_checkouts = self.get_user_checkouts(self.user_id)

        # Format the user checkouts as text
        checkouts_text = self._format_checkouts_as_text(user_checkouts)

        # Create the chain and invoke it
        chain = self.create_chain()
        response = chain.invoke({
            "user_input": user_input,
            "catalog": catalog_text,
            "checkouts": checkouts_text
        })

        return response