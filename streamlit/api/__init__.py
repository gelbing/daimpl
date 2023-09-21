import os

import streamlit as st

DB_HOSTS = os.environ.get("BACKEND_HOSTS", "localhost").split(",")
BACKEND_URIS = [f"http://{host}:8000" for host in DB_HOSTS]


def choose_backend():
    """Choose the BACKEND URI"""
    backend_uri = st.sidebar.selectbox(
        "Choose a backend port",
        BACKEND_URIS,
        format_func=lambda URI: f"URI:  {URI}",
        # Defaults to the first port in BACKEND_PORTS
        index=0,
    )

    # backend uris are of the form http://client-1-backend:8000 with cid being client-1
    cid = backend_uri.split("http://")[1].split("-backend")[0]

    return backend_uri, cid
