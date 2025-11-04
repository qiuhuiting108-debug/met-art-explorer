# 🎨 Qiu Huiting’s MET Art Explorer — Final Version
# Data source: The Metropolitan Museum of Art Collection API (public, no key required)

import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="Qiu Huiting’s MET Art Explorer", page_icon="🎨", layout="wide")

# -------------------- CSS STYLE --------------------
st.markdown("""
<style>
body {
    background-color: #f7f7f7;
}
h1 {
    text-align: center;
    font-weight: 800;
    color: #222;
}
p.subtitle {
    text-align: center;
    color: gray;
    margin-top: -10px;
    margin-bottom: 30px;
}
div[data-testid="stTextInput"] input {
    border-radius: 20px;
    background-color: white;
    padding: 10px 15px;
    font-size: 16px;
}
div[data-testid="stImage"] img {
    border-radius: 16px;
}
.stButton > button {
    border-radius: 20px;
    background-color: #4CAF50;
    color: white;
    font-weight: 600;
    padding: 8px 20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1>🎨 Qiu Huiting’s MET Art Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Explore beautiful artworks from The Metropolitan Museum of Art API</p>", unsafe_allow_html=True)

# -------------------- SEARCH INPUT --------------------
query = st.text_input("Search for Artworks:", value="flower")

# -------------------- API FUNCTIONS --------------------
def search_objects(keyword):
    """Search object IDs by keyword."""
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": keyword, "hasImages": "true"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data.get("objectIDs", [])[:120]  # store up to 120 results

def get_object_detail(object_id):
    """Get detailed info for each artwork."""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

# -------------------- PAGINATION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = 1
if "ids" not in st.session_state:
    st.session_state.ids = []

# -------------------- SEARCH BUTTON --------------------
if st.button("🔍 Search"):
    if not query.strip():
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Searching artworks..."):
            ids = search_objects(query)
            if not ids:
                st.info("No artworks found.")
            else:
                st.session_state.ids = ids
                st.session_state.page = 1
                st.success(f"Found {len(ids)} results.")
                st.rerun()

# -------------------- DISPLAY RESULTS --------------------
if st.session_state.ids:
    start = (st.session_state.page - 1) * 12
    end = start + 12
    current_ids = st.session_state.ids[start:end]

    cols = st.columns(3)
    for i, oid in enumerate(current_ids):
        try:
            data = get_object_detail(oid)
            title = data.get("title", "Untitled")
            artist_name = data.get("artistDisplayName", "Unknown Artist")
            date = data.get("objectDate", "")
            img_url = data.get("primaryImageSmall", "")

            with cols[i % 3]:
                with st.container(border=True):
                    if img_url:
                        response = requests.get(img_url)
                        img = Image.open(BytesIO(response.content))
                        st.image(img, use_column_width=True)
                    st.markdown(f"**{title}**  \n_{artist_name}_  \n*{date}*")
        except Exception as e:
            st.write(f"⚠️ Error loading artwork ID {oid}: {e}")

    # -------------------- PAGINATION BUTTONS --------------------
    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.session_state.page > 1:
            if st.button("⬅️ Prev Page"):
                st.session_state.page -= 1
                st.rerun()
    with col_mid:
        st.markdown(f"<p style='text-align:center; color:gray;'>Page {st.session_state.page}</p>", unsafe_allow_html=True)
    with col_next:
        if end < len(st.session_state.ids):
            if st.button("Next ➡️"):
                st.session_state.page += 1
                st.rerun()

