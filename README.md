### SHL Assessment Recommendation System: Approach Document
Overview
The SHL Assessment Recommendation System aims to help hiring managers find relevant assessments using natural language queries or job descriptions. This system uses a Flask API to handle backend processing and a Streamlit frontend for user interaction. This document explains how we plan to build and launch the system.

System Architecture
The system has two main parts:
1. Flask API: Takes in requests, processes queries and sends back relevant assessments.
2. Streamlit App: Offers an easy-to-use interface for entering queries and showing recommendations.

Development Steps
1. Data Collection
- Scraping Assessments: We used web scraping methods with BeautifulSoup and Selenium to collect assessment data from the SHL website. The data has assessment names, URLs, durations, test types, and support options.
- Data Storage: We saved the collected data in a CSV file (`shl_assessments_enriched.csv`) to make it easy to access and work with.
 2. Backend Development
- Flask API: We built a Flask app (`app.py`) to work as the backend. The API has:
  - A route (`/recommend`) that takes POST requests with a query.
  - A function (`recommend_assessments`) to process the query, pull out keywords, and match them with the assessment data.
  - Ways to handle errors and send back the right responses for bad queries or processing problems.
3. Recommendation Logic
- Keyword Extraction: We created a function using spaCy to pull out important keywords from what users ask.
- Scoring System: We came up with a way to score how well assessments match based on keywords in their names and types.
- Ranking Recommendations: We put assessments in order based on their scores and gave back the best matches.


4. Frontend Development
- Streamlit App: We built a Streamlit application (`app_streamlit.py`) to give users an easy-to-use interface. The app has these main parts:
  - A box where users can type in job descriptions or questions.
  - A button to send the question and get suggestions from the Flask API.
  - A section that shows the recommended assessments and their details.
5. Deployment
- Flask API Deployment: We put the Flask API on Render making it available online. This process involved:
  - Making a `requirements.txt` file to show what the app needs.
  - Telling Render how to start the Flask app with `gunicorn`.
- Streamlit App Deployment: We launched the Streamlit app on Streamlit Sharing connecting it to the Flask API's public web address for smooth operation.

 Evaluation
- I  set up ways to measure how well the system works (Mean Recall@K and Mean Average Precision@K).
- Ran tests using preset questions to check if the recommendation system performs well.

 Conclusion
The SHL Assessment Recommendation System brings together web scraping, language processing, and web development to create a useful tool for hiring managers. Its design lets us update and grow the system , so it can change to meet future needs.

![image](https://github.com/user-attachments/assets/e8039fde-d210-43e3-aecb-ab6b924e500a)
