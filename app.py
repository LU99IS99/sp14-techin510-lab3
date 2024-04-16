import os
import streamlit as st
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

def create_table():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS prompts;")  # Reset the table if needed
        cur.execute("""
            CREATE TABLE prompts (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                prompt TEXT NOT NULL,
                genre TEXT NOT NULL,
                activity TEXT NOT NULL,
                is_favorite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    conn.close()

def list_prompts(sort_by):
    conn = get_db_connection()
    query = f"SELECT id, title, prompt, activity, is_favorite FROM prompts ORDER BY {sort_by}"
    with conn.cursor() as cur:
        cur.execute(query)
        prompts = cur.fetchall()
    return prompts

def main():
    st.title("Prompt Manager")

    # Template and prompt creation
    activity_types = ["Travel", "Entertainment", "Work", "Eat"]
    chosen_activity = st.selectbox("Select Activity Type", options=activity_types)
    genre_options = ["Fiction", "Non-fiction", "Poetry", "Journal"]
    chosen_genre = st.selectbox("Select Genre", options=genre_options)
    template_prompts = {
        "Travel": "Describe your last travel experience.",
        "Entertainment": "What is your favorite movie and why?",
        "Work": "Describe a recent challenge at work and how you overcame it.",
        "Eat": "Describe your favorite meal and why you love it."
    }
    prompt_text = st.text_area("Prompt", value=template_prompts[chosen_activity])
    title = st.text_input("Prompt Title")

    if st.button("Save Prompt"):
        create_prompt(title, prompt_text, chosen_genre, chosen_activity)

    # Sorting options
    sort_options = ["created_at DESC", "activity", "title"]
    sort_by = st.selectbox("Sort Prompts By", options=sort_options)

    # Display prompts
    st.subheader("Available Prompts")
    prompts = list_prompts(sort_by)
    for id, title, prompt, activity, is_favorite in prompts:
        with st.expander(f"{title} - {activity} ({'Favorite' if is_favorite else 'Not Favorite'})"):
            st.write(prompt)
            if st.button("Toggle Favorite", key=f"fav_{id}"):
                toggle_favorite(id)
            if st.button("Delete", key=f"del_{id}"):
                delete_prompt(id)

def create_prompt(title, prompt, genre, activity):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO prompts (title, prompt, genre, activity, is_favorite) VALUES (%s, %s, %s, %s, %s)",
            (title, prompt, genre, activity, False)
        )
        conn.commit()

def toggle_favorite(prompt_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (prompt_id,))
        conn.commit()

def delete_prompt(prompt_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
        conn.commit()

if __name__ == "__main__":
    create_table()
    main()

