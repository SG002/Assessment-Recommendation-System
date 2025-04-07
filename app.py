from flask import Flask, request, jsonify
import pandas as pd
from scraper import recommend_assessments  

app = Flask(__name__)


assessments_df = pd.read_csv("data/shl_assessments_enriched.csv")

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        recommendations = recommend_assessments(query, assessments_df.to_dict(orient='records'))
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

if __name__ == '__main__':
    app.run(debug=True)