# Import required libraries
import streamlit as st  # Import Streamlit to build the web app UI
from geopy.geocoders import Nominatim  # To convert geographic coordinates into readable addresses
from streamlit_option_menu import option_menu  # To create a styled navigation menu in the sidebar
import streamlit_js_eval  # To run JavaScript inside Streamlit and get geolocation
import pycountry  # To convert country codes (like 'us') into full country names ('United States')
import json  # To load and work with data stored in a JSON file (like rights.json)

# Detect user location early so it can be reused on different pages
location = streamlit_js_eval.get_geolocation()  # This gets the user's latitude and longitude from the browser
if location:
    geolocator = Nominatim(user_agent="app.py")  # Create a geolocator object with a required user_agent
    latitude = float(location['coords']['latitude'])  # Get the latitude from location
    longitude = float(location['coords']['longitude'])  # Get the longitude from location
    geolocation = geolocator.reverse(str(latitude) + "," + str(longitude))  # Convert coordinates to an address
    address = geolocation.raw['address']  # Get the detailed address
    country_code = address.get('country_code')  # Get the 2-letter country code (like 'us', 'in')
    detected_country = pycountry.countries.get(alpha_2=country_code).name  # Convert to full country name
else:
    detected_country = None  # If location isn’t available, keep it as None

# Create a sidebar menu with three pages using option_menu
page = option_menu(
    "JusticePath Navigation",  # Title of the menu shown in the sidebar
    ["Home", "Search", "Chatbot"],  # List of pages available in the app
    icons=["house", "search", "chat-dots"],  # Icons next to each page name
    menu_icon="cast",  # Icon at the top of the menu
    default_index=0  # The default selected page when the app loads
)

# HOME PAGE
if page == "Home":
    st.title("Welcome to JusticePath")  # Show the app title
    st.write("Helping you understand your rights easily.")  # Introductory message

    if detected_country:  # If the user’s country was found from geolocation
        st.write(f"Your country: {detected_country}")  # Show the user’s country

        # Button: View constitution (demo only)
        if st.button("View Country Constitution"):
            st.info(f"This would open the constitution for {detected_country} (demo only).")

        # Button: Find legal aid (demo only)
        if st.button("Find Legal Aid Resources"):
            st.info(f"This would show legal aid resources in {detected_country} (demo only).")
    else:
        st.warning("Location not available.")  # Show a warning if the location couldn’t be detected

# SEARCH PAGE
elif page == "Search":
    st.title("Search Your Rights")  # Title for the search page

    with open('rights.json') as f:  # Open the JSON file containing rights information
        rights_data = json.load(f)  # Load the data into Python as a list of dictionaries

    # Create a list of all unique countries mentioned in the JSON file
    countries = sorted(list(set(item['country'] for item in rights_data)))
    countries.insert(0, "All Countries")  # Add a default "All Countries" option at the top

    # If a country was detected from location, make it the default in the dropdown
    default_index = countries.index(detected_country) if detected_country in countries else 0

    # Country filter dropdown
    selected_country = st.selectbox("Filter by country", countries, index=default_index)

    # Keyword search box
    search_query = st.text_input("Search rights by keyword (title, article, etc.)")

    # Start with all data loaded
    filtered_data = rights_data

    # If user selected a specific country, filter the data
    if selected_country != "All Countries":
        filtered_data = [item for item in filtered_data if item['country'] == selected_country]

    # If user typed something in the search box, filter based on that
    if search_query:
        query = search_query.lower()  # Convert search query to lowercase to make it case-insensitive
        filtered_data = [
            item for item in filtered_data
            if query in item['title'].lower()  # Match search query in the title
            or query in item['description'].lower()  # ...or in the description
            or query in item['category'].lower()  # ...or in the category
            or query in item['article'].lower()  # ...or in the article name
            or query in item['country'].lower()  # ...or even in the country name
        ]

    # Display the filtered results
    if filtered_data:
        for r in filtered_data:
            st.subheader(f"{r['title']} ({r['country']})")  # Show the title and country
            st.write(f"**Description:** {r['description']}")  # Show the description
            st.write(f"**Category:** {r['category']}")  # Show the rights category
            st.write(f"**Article:** {r['article']}")  # Show the legal article
            st.markdown("---")  # Add a line separator between entries
    else:
        st.info("No matching results found.")  # If no matches were found, show an info message

# CHATBOT PAGE
elif page == "Chatbot":
    st.title("JusticePath Chatbot")  # Title for the chatbot page

    user_input = st.text_input("Ask a legal question")  # Input box for user’s question

    if user_input:  # If the user typed something
        # Send the question to the OpenAI GPT model and get a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the GPT model version
            messages=[{"role": "user", "content": user_input}]  # Provide the user’s question as a message
        )

        # Display the chatbot's reply
        st.write(response['choices'][0]['message']['content'])
