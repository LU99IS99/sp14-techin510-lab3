import os
import streamlit as st
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection utility
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Operational error when connecting to the database: {e}")
        return None
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        return None

# Function to create a new prompt table
def create_table():
    conn = get_db_connection()
    if not conn:
        st.error("Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            st.info("Table 'prompts' created successfully.")
    except psycopg2.Error as e:
        st.error(f"Failed to create table: {e.pgerror}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

# Function to add a new prompt
def create_prompt(title, prompt, genre):
    if not title or not prompt or not genre:  # Check for empty inputs
        st.error("Title, prompt content, and genre are required.")
        return
    
    conn = get_db_connection()
    if conn is None:
        st.error("Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO prompts (title, prompt, genre, is_favorite) VALUES (%s, %s, %s, %s)", (title, prompt, genre, False))
            conn.commit()
            st.success("Prompt added successfully!")
    except psycopg2.Error as e:
        st.error(f"Failed to add prompt: {e.pgerror}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

# Function to list all prompts
def list_prompts():
    conn = get_db_connection()
    if not conn:
        st.error("Failed to connect to the database.")
        return []

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, prompt, genre, is_favorite FROM prompts ORDER BY created_at DESC")
            prompts = cur.fetchall()
            return prompts
    except psycopg2.Error as e:
        st.error(f"Failed to execute query: {e.pgerror}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return []
    finally:
        conn.close()

# Function to toggle the favorite status of a prompt
def toggle_favorite(prompt_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (prompt_id,))
            conn.commit()
        conn.close()

# Function to delete a prompt
def delete_prompt(prompt_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
            conn.commit()
        conn.close()

# Main Streamlit app function
def main():
    st.title("Prompt Manager")

    # Form to create new prompt
    with st.form("new_prompt_form"):
        title = st.text_input("Prompt Title")
        prompt_text = st.text_area("Prompt Content")
        genre = st.text_input("Prompt Genre")  # Input for genre
        create_button = st.form_submit_button("Create Prompt")
        if create_button and title and prompt_text and genre:
            create_prompt(title, prompt_text, genre)  # Pass genre to the function

    # Display all prompts with options to edit, delete, and toggle favorite
    st.subheader("Available Prompts")
    prompts = list_prompts()
    for prompt in prompts:
        with st.expander(f"{prompt[1]} - {prompt[3]} ({'Favorite' if prompt[4] else 'Not Favorite'})"):
            st.text(prompt[2])
            if st.button("Toggle Favorite", key=f"toggle_fav_{prompt[0]}"):
                toggle_favorite(prompt[0])
                st.experimental_rerun()
            if st.button("Delete", key=f"delete_{prompt[0]}"):
                delete_prompt(prompt[0])
                st.experimental_rerun()

if __name__ == "__main__":
    main()
