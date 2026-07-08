import streamlit as st
import pickle
import difflib
import pandas as pd

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


st.markdown("""
<style>

/* ---------- Main App ---------- */

.stApp{
    background: linear-gradient(135deg,#EEF5FF,#FFFFFF);
}

/* ---------- Global Font ---------- */

html, body, [class*="css"]{
    font-family: "Segoe UI", sans-serif;
    color:#1E293B !important;
}

/* ---------- Headings ---------- */

h1,h2,h3,h4,h5,h6{
    color:#0F172A !important;
}

/* ---------- Markdown ---------- */

[data-testid="stMarkdownContainer"]{
    color:#1E293B !important;
    font-size:18px;
}

/* ---------- Paragraph ---------- */

p{
    color:#334155 !important;
}

/* ---------- Labels ---------- */

label{
    color:#0F172A !important;
    font-size:18px !important;
    font-weight:600;
}

/* ---------- Title ---------- */

.main-title{
    text-align:center;
    font-size:60px;
    font-weight:bold;
    color:#3b64f6 !important;
}

.sub-title{
    text-align:center;
    font-size:22px;
    color:#64748B !important;
    margin-bottom:30px;
}

/* ---------- Selectbox ---------- */

.stSelectbox label{
    color:#0F172A !important;
    font-size:20px !important;
}

/* Dropdown text */
.stSelectbox div[data-baseweb="select"]{
    color:#0F172A !important;
    background:white !important;
}

/* ---------- Button ---------- */

.stButton>button{

    width:100%;
    height:60px;

    background:linear-gradient(
    90deg,
    #3bcdf6,
    #3bcdf6);

    color:white;

    font-size:20px;

    font-weight:bold;

    border-radius:12px;

    border:none;

}

.stButton>button:hover{

    background:#1da3d8;

}

/* ---------- Sidebar ---------- */

section[data-testid="stSidebar"]{

    background:#F8FAFC;

}

section[data-testid="stSidebar"] *{

    color:#1E293B !important;

}

/* ---------- Metrics ---------- */

[data-testid="stMetricValue"]{

    color:#2563EB !important;

}

[data-testid="stMetricLabel"]{

    color:#334155 !important;

}

/* ---------- Cards ---------- */

.movie-card{

    background:white;

    color:#1E293B !important;

    padding:20px;

    border-radius:15px;

    border:1px solid #E2E8F0;

    box-shadow:0 8px 20px rgba(0,0,0,.08);

    margin-bottom:20px;

}

.movie-card h3{

    color:#0F172A !important;

}

.movie-card p{

    color:#334155 !important;

}

</style>
""", unsafe_allow_html=True)
st.sidebar.title("🎬 Movie Dashboard")

st.sidebar.metric(
    "Movies",
    len(movies)
)

st.sidebar.metric(
    "Average Rating",
    round(movies.vote_average.mean(),2)
)

st.sidebar.metric(
    "Highest Rating",
    movies.vote_average.max()
)

st.sidebar.divider()

st.sidebar.subheader("About")

st.sidebar.info("""

Movie Recommendation System

✔ Content Based Filtering

✔ TF-IDF

✔ Cosine Similarity

""")

st.markdown(
"""
<div class='main-title'>
 Movie Recommendation System
</div>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<div class='sub-title'>
Discover movies you'll love using Machine Learning
</div>
""",
unsafe_allow_html=True
)

st.markdown("## Top Rated Movies")

top_movies = movies.sort_values(
    "vote_average",
    ascending=False
).head(5)

cols = st.columns(5)

for col, (_, row) in zip(cols, top_movies.iterrows()):

    with col:

        st.metric(
            row["title"][:18],
            f" {row['vote_average']}"
        )

movie = st.selectbox(
    "🔍 Search Movie",
    sorted(movies["title"].tolist()),
    placeholder="Type movie name..."
)

def recommend(movie_name):

    titles = movies["title"].tolist()

    match = difflib.get_close_matches(movie_name, titles, n=1)

    if not match:
        return []

    close_match = match[0]

    movie_index = movies[
        movies["title"] == close_match
    ]["index"].values[0]

    similarity_scores = list(
        enumerate(similarity[movie_index])
    )

    sorted_movies = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for movie in sorted_movies:

        index = movie[0]

        row = movies[
            movies["index"] == index
        ]

        if row.empty:
            continue

        title = row["title"].values[0]

        if title == close_match:
            continue

        recommendations.append({

            "title": title,

            "rating": float(
                row["vote_average"].values[0]
            ),

            "release": str(
                row["release_date"].values[0]
            )[:4],

            "genres": row["genres"].values[0],

            "director": row["director"].values[0],

            "overview": str(
                row["overview"].values[0]
            ),

            "popularity": float(
                row["popularity"].values[0]
            )

        })

        if len(recommendations) == 10:
            break

    return recommendations

recommend_btn = st.button("Recommend")

if recommend_btn:

    recommendations = recommend(movie)

    st.markdown("## Recommended Movies")

    for rec in recommendations:

        with st.container(border=True):

            col1, col2 = st.columns([4,1])

            with col1:

                st.markdown(f"### 🎬 {rec['title']}")

                st.write(
                    f"🎭 **Genres:** {rec['genres']}"
                )

                st.write(
                    f"👨‍💼 **Director:** {rec['director']}"
                )

                st.write(
                    f"📅 **Release Year:** {rec['release']}"
                )

                overview = rec["overview"]

                if len(overview) > 220:

                    overview = overview[:220] + "..."

                st.write(overview)

            with col2:

                rating = rec["rating"]

                st.metric(
                    "⭐ Rating",
                    f"{rating:.1f}/10"
                )

                st.progress(
                    min(rating/10,1.0)
                )

                popularity = min(
                    rec["popularity"]/100,
                    1.0
                )

                st.metric(
                    "🔥 Popularity",
                    f"{rec['popularity']:.1f}"
                )

                st.progress(popularity)

        st.write("")

st.markdown("---")

st.markdown(
"""
<center>

Made with ❤️ using Streamlit

<br>

Developed by <b>user</b>

</center>
""",
unsafe_allow_html=True
)
