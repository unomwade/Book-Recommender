# Library Recommendation System

This project implements a **Library Recommendation System** using Python, DuckDB, and OpenAI's GPT-based language models. It includes data ingestion, a recommender module, and an application for suggesting books to users based on their preferences and past interactions.

---

## Features

- **Data Ingestion**:
  - Loads data from CSV files into a DuckDB database.
  - Prepares the `books`, `users`, and `user_checkouts` tables.

- **Recommender Module**:
  - Uses OpenAI's GPT model (via LangChain) to generate book recommendations.
  - Structured responses include book details, a synopsis, and a personalized email-ready summary.

- **Main Application**:
  - Executes the ingestion process and runs the main recommendation application seamlessly.

- **Streamlit Application**:
  - User interface that also that acts as a database manager and recommender UI for a librarian
  - Contains ability to add users/books and track checkouts
  - Ability in future to send user an email with recommendation

- **Dockerized Setup**:
  - Dockerfile provided for easy deployment and environment consistency.
  - Runs on Python 3.11.

---

## Installation and Setup

### Prerequisites

- [Docker](https://www.docker.com/)
- Python 3.11 (optional, if running locally)
- [OpenAI API Key](https://platform.openai.com/)

### Directory Structure

```plaintext
project/
│
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point for the application
├── recommender.py          # Recommender system implementation
├── app.py                  # UI and Streamlit App
├── data_collection/        # Directory for data ingestion scripts
│   └── ingest.py           # Data ingestion script
├── data/                   # Directory for data and database files
│   ├── library_db.duckdb   # DuckDB database (auto-created on start-up)
|   ├── ingest.py           # Running data ingestions
│   └── csv/                # Directory for CSV input files
│       ├── book.csv        # Books data
│       ├── checkouts.csv   # User checkouts data
│       └── users.csv       # Users data
```
## Running the Project

### 1. Using Docker

Build the Docker Image
```bash
docker build -t library-recommender --build-arg OPENAI_API_KEY=your_openai_api_key .
```
Run the Application
```bash
docker run -p 8501:8501 library-recommender
```
- The container mounts the data directory for accessing CSV files and saving the DuckDB database.

### 2. Running Locally

Install Dependencies

Ensure you have Python 3.11 and install the required libraries:
```bash
pip install -r requirements.txt
```
Set Environment Variables

Create a .env file for the OpenAI API key:
```bash
export OPENAI_API_KEY=your_openai_api_key
``` 

Run data ingest
```bash
python ./data/ingest.py
```

Run the Application
```bash
streamlit run app.py
```

## Application Screenshot

Below is a preview of the Library Recommendation System in action:

![Top of Screen and DB Interaction](docs/main_screen.png)
![Recommendation System in Action](docs/recommendation.png)

## Files and Scripts

### 1. main.py

The entry point for the application:
- Runs ingest.py to load data into DuckDB.
- Executes the recommendation system via app.py.

### 2. app.py

The entry point for the application:
- Has ability to interact with database, like an admin terminal (Not all ACID methods)
- Can display recommendations and updates recommendations based on database changes

### 2. data/ingest.py

Handles data ingestion:
- Reads book.csv, checkouts.csv, and users.csv.
- Creates and populates the DuckDB tables: books, users, and user_checkouts.

### 3. recommender.py

Implements the Library Recommender:
- Defines a LibraryRecommender class that:
- Connects to the DuckDB database.
- Fetches user and catalog data.
- Generates structured recommendations using OpenAI’s GPT models via LangChain.
- Responses include:
  - Recommended book title.
  - A brief synopsis.
  - Personalized feedback and a grade.
  - A summarized email-ready message.

### 4. Dockerfile

Builds a containerized environment with:
- Python 3.11.
- Dependencies from requirements.txt.
- Prepares /app/data/csv for input data.

Example Workflow
1. Data Ingestion:
- ingest.py processes and uploads data to DuckDB.
2. Recommendation Generation:
- Input: User name and query (e.g., “I enjoy fantasy novels”).
- Output: A recommendation response with details about a relevant book.
3. Dockerized Execution:
- Run the complete workflow in a reproducible container.

## Example Recommendation

Input:
```text
User: Alice
Query: I love books with strong female protagonists and magical worlds.
```

Output:
```text
{
  "book_id": "1",
  "title": "Matilda",
  "feedback": "This book features a bright young girl with extraordinary powers who overcomes challenges.",
  "grade": 95,
  "synopsis": "A story about Matilda, a gifted child navigating a world of neglectful parents and an oppressive headmistress.",
  "summarized_email_body": "Hi Alice, based on your interest in strong female protagonists and magical worlds, we recommend 'Matilda'. Here's why you'll love it: 'Matilda' tells the inspiring story of a brilliant young girl overcoming the odds with her intelligence and extraordinary abilities."
}
```
## Requirements

Python Dependencies (requirements.txt)
```text
pandas
duckdb
langchain
langchain_openai
openai
python-dotenv
pydantic
```

## Troubleshooting

Common Issues
1. DuckDB Data Ingestion Fails:
- Ensure CSV files are correctly formatted.
- Verify that all data values are compatible with DuckDB column types.
2. OpenAI API Key Error:
- Ensure the .env file contains a valid OPENAI_API_KEY.
- Check API usage limits on your OpenAI account.
3. Docker Volume Mount Issues:
- Verify that the data directory exists locally and is mounted correctly to /app/data inside the container.

Acknowledgments
- DuckDB: In-memory SQL database engine.
- LangChain: Framework for building applications with LLMs.
- OpenAI: Provider of GPT-based language models.

---

## Usage Scenarios:

- **Developers**: Use Docker for consistent environments.
- **Data Scientists**: Extend the recommendation logic by experimenting with LangChain prompts or DuckDB queries.
- **Demonstrations**: Showcase the workflow end-to-end with easy Docker deployment.