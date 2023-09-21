import os
import time

import requests
from api import choose_backend

import streamlit as st

# Backend URL
BACKEND_URI, CLIENT_ID = choose_backend()


# This function will be used to display any errors
def handle_error(e):
    st.exception(e)


# Refresh button to refresh the page
refresh = st.sidebar.button("Refresh")
if refresh:
    st.experimental_rerun()


# Creating a form for creating a new todo
with st.form("create_todo_form"):
    title = st.text_input("Title")
    description = st.text_input("Description")
    submitted = st.form_submit_button("Create Todo")
    if submitted:
        try:
            response = requests.post(
                f"{BACKEND_URI}/todo",
                json={
                    "client_id": CLIENT_ID,
                    "title": title,
                    "description": description,
                },
            )
            response.raise_for_status()
            st.write("Todo created successfully.")
        except Exception as e:
            handle_error(e)

# Show all todos with option for deleting them
st.header("All Todos")
try:
    response = requests.get(f"{BACKEND_URI}/todo")
    response.raise_for_status()
    todos = response.json()
    for todo in todos:
        container = st.container()

        title = container.text_input(
            "Title",
            todo["title"],
            key=f"all_todos_title_{todo['client_id']}_{todo['id']}",
        )
        description = container.text_input(
            "Description",
            todo["description"],
            key=f"all_todos_description_{todo['client_id']}_{todo['id']}",
        )
        col1, col2, _ = st.columns([1, 1, 5])
        if col1.button("Update", key=f"update_{todo['client_id']}_{todo['id']}"):
            try:
                response = requests.post(
                    f"{BACKEND_URI}/todo/{todo['client_id']}/{todo['id']}",
                    json={"title": title, "description": description},
                )

                response.raise_for_status()
                st.write("Todo updated successfully.")
                time.sleep(1)

                st.experimental_rerun()

            except Exception as e:
                handle_error(e)

        if col2.button("Delete", key=f"delete_{todo['client_id']}_{todo['id']}"):
            try:
                response = requests.delete(
                    f"{BACKEND_URI}/todo/{todo['client_id']}/{todo['id']}"
                )
                response.raise_for_status()
                st.write("Todo deleted successfully.")
                time.sleep(1)
                st.experimental_rerun()
            except Exception as e:
                handle_error(e)

        st.write("---")
except Exception as e:
    handle_error(e)
