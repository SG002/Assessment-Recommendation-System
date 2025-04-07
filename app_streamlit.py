import streamlit as st
import requests


st.title("SHL Assessment Recommendation System")


query = st.text_input("Enter your job description or query:")


if st.button("Get Recommendations"):
    if query:
        
        response = requests.post("https://shlars.streamlit.app/", json={"query": query})
        
        
        print("Raw response:", response.text)
        
        if response.status_code == 200:
            recommendations = response.json()
            st.subheader("Recommended Assessments:")
            for rec in recommendations:
                st.write(f"**Name:** {rec['name']}")
                st.write(f"**URL:** [Link]({rec['url']})")
                st.write(f"**Remote Support:** {rec['remote_support']}")
                st.write(f"**Adaptive Support:** {rec['adaptive_support']}")
                st.write(f"**Duration:** {rec['duration']}")
                st.write(f"**Test Type:** {rec['test_type']}")
                st.write("---")
        else:
            st.error("Error: " + response.text)  
    else:
        st.warning("Please enter a query.") 