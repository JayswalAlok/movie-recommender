import pickle
import streamlit as st
import requests
import zipfile
import os

# Add developer credit at the top
st.markdown(
    """
    <style>
    .developer-credit {
        font-size: 16px;
        text-align: right;
        color: #555555;
        padding: 5px 15px 0 0;
        font-weight: bold;
    }
    </style>
    <div class="developer-credit">Developed by Jayswal Alok</div>
    """,
    unsafe_allow_html=True
)

# ========== ZIP FILE EXTRACTION LOGIC ========== #
def extract_zip_if_needed(zip_filename, output_filename):
    """Extract zip file if output file doesn't exist"""
    if not os.path.exists(output_filename) and os.path.exists(zip_filename):
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall('.')
            st.success(f"Successfully extracted {output_filename} from {zip_filename}")
        except Exception as e:
            st.error(f"Failed to extract {zip_filename}: {str(e)}")
            return False
    return True

# Check and extract both pickle files
extract_zip_if_needed('movie_list.zip', 'movie_list.pkl')
extract_zip_if_needed('similarity.zip', 'similarity.pkl')

# ========== MAIN APPLICATION CODE ========== #
try:
    # Load preprocessed data
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError as e:
    st.error(f"Critical error: {str(e)}. Please ensure all data files are uploaded.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data files: {str(e)}")
    st.stop()

# OMDB API Configuration
OMDB_API_KEY = 'd6ac8dbc'
OMDB_URL = 'http://www.omdbapi.com/'

def get_movie_details(title):
    try:
        params = {
            'apikey': OMDB_API_KEY,
            't': title,
            'plot': 'short',
            'r': 'json'
        }
        response = requests.get(OMDB_URL, params=params, timeout=10)
        data = response.json()

        if data.get('Response') == 'True':
            return {
                'Poster': data.get('Poster', 'N/A'),
                'Year': data.get('Year', 'N/A'),
                'Genre': data.get('Genre', 'N/A'),
                'Director': data.get('Director', 'N/A'),
                'Actors': data.get('Actors', 'N/A'),
                'imdbRating': data.get('imdbRating', 'N/A'),
                'Plot': data.get('Plot', 'N/A'),
                'Runtime': data.get('Runtime', 'N/A')
            }
        return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Streamlit UI
st.title('🎬 Movie Recommender System')

try:
    selected_movie = st.selectbox(
        'Select or type a movie title:',
        movies['title'].values
    )

    if st.button('Get Recommendations'):
        # Show selected movie details
        st.subheader(f"🎥 You selected: {selected_movie}")
        selected_details = get_movie_details(selected_movie)

        if selected_details:
            col1, col2 = st.columns([1, 3])
            with col1:
                if selected_details['Poster'] != 'N/A':
                    st.image(selected_details['Poster'], width=200)
                else:
                    st.warning("Poster not available")
            with col2:
                st.write(f"**📅 Year:** {selected_details['Year']}")
                st.write(f"**⏱️ Runtime:** {selected_details['Runtime']}")
                st.write(f"**🎭 Genre:** {selected_details['Genre']}")
                st.write(f"**🎬 Director:** {selected_details['Director']}")
                st.write(f"**⭐ IMDb Rating:** {selected_details['imdbRating']}")
                st.write(f"**📖 Plot:** {selected_details['Plot']}")
        else:
            st.warning("Couldn't fetch details for selected movie")

        # Get recommendations
        st.subheader("🍿 Top 5 Recommendations")
        idx = movies[movies['title'] == selected_movie].index[0]
        sim_scores = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]

        for i, (index, score) in enumerate(sim_scores, 1):
            movie_title = movies.iloc[index].title
            details = get_movie_details(movie_title)

            st.markdown(f"### {i}. {movie_title}")
            if details:
                cols = st.columns([1, 3])
                with cols[0]:
                    if details['Poster'] != 'N/A':
                        st.image(details['Poster'], width=150)
                    else:
                        st.write("No poster available")
                with cols[1]:
                    st.write(f"**Year:** {details['Year']}")
                    st.write(f"**Rating:** ⭐ {details['imdbRating']}")
                    st.write(f"**Genre:** {details['Genre']}")
                    st.write(f"**Plot:** {details['Plot'][:200]}...")
            else:
                st.warning("Details not available")
            st.write("---")

except Exception as e:
    st.error(f"Application error: {str(e)}")
