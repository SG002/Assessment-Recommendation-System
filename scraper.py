import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import spacy


warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  


nlp = spacy.load("en_core_web_sm")

def extract_keywords(query):
    
    doc = nlp(query)
    
    
    keywords = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    
    print(f"Extracted Keywords: {keywords}")
    
    return keywords

def scrape_assessment_details(driver, url):
    driver.get(url)
    try:
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Assessment length')]"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        
        duration = "N/A"
        h4 = soup.find('h4', string=lambda text: 'Assessment length' in str(text))
        if h4:
            next_p = h4.find_next('p')
            if next_p:
                duration_text = next_p.get_text(strip=True)
                duration = ''.join(filter(str.isdigit, duration_text)) or "N/A"
        
        
        test_type = "Cognitive"  
        test_type_element = soup.find(string=lambda text: 'Test Type' in str(text))
        if test_type_element:
            test_type = test_type_element.find_next().get_text(strip=True)
        
        
        remote_support = "No"
        remote_element = soup.find(string=lambda text: 'Remote Testing' in str(text))
        if remote_element and '●' in remote_element.find_next().get_text():
            remote_support = "Yes"
        
        return {
            "duration": f"{duration} mins",
            "test_type": test_type,
            "remote_support": remote_support
        }
        
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {str(e)}")
        return {
            "duration": "N/A",
            "test_type": "N/A",
            "remote_support": "No"
        }

def scrape_shl_assessments():
    os.makedirs("data", exist_ok=True)
    
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        
        print("Loading main catalog page...")
        driver.get("https://www.shl.com/solutions/products/product-catalog/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "custom__table-heading__title"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        assessments = []
        
        
        rows = soup.find_all('tr')
        print(f"Found {len(rows)} potential assessments")
        
        for row in rows:
            title_cell = row.find('td', class_='custom__table-heading__title')
            if title_cell:
                name = title_cell.find('a').get_text(strip=True)
                url = "https://www.shl.com" + title_cell.find('a')['href']
                assessments.append({
                    "name": name,
                    "url": url,
                    "remote_support": "No",  
                    "adaptive_support": "No"
                })

        
        print(f"Scraping details for {len(assessments)} assessments...")
        for i, assessment in enumerate(assessments, 1):
            print(f"  {i}/{len(assessments)}: {assessment['name']}")
            details = scrape_assessment_details(driver, assessment['url'])
            assessment.update(details)
        
        
        df = pd.DataFrame(assessments)
        df.to_csv("data/shl_assessments_enriched.csv", index=False)
        print(f"Saved {len(df)} enriched assessments to 'data/shl_assessments_enriched.csv'")
        print("Sample data:")
        print(df.head().to_string())
        
        return df
        
    except Exception as e:
        print(f"Error in main scraping function: {str(e)}")
        return None
    finally:
        driver.quit()

def load_assessments_from_csv(file_path):
    return pd.read_csv(file_path)


assessments_df = load_assessments_from_csv("data/shl_assessments_enriched.csv")

print(assessments_df.head())

def calculate_relevance_score(keywords, assessment):
    score = 0
    
    
    assessment_name = assessment['name'].lower()
    assessment_test_type = assessment['test_type'].lower()
    
    
    if any(keyword in assessment_name for keyword in keywords):
        score += 1  
    if any(keyword in assessment_test_type for keyword in keywords):
        score += 1  
    
    return score

def recommend_assessments(query, assessments, top_k=10):
    
    keywords = extract_keywords(query)
    
    
    scored_assessments = []
    for assessment in assessments:
        score = calculate_relevance_score(keywords, assessment)
        scored_assessments.append((assessment, score))
    
    
    scored_assessments.sort(key=lambda x: x[1], reverse=True)
    return [assessment for assessment, score in scored_assessments[:top_k]]

def mean_recall_at_k(recommendations, relevant_assessments, k):
    total_recall = 0
    for recs, relevant in zip(recommendations, relevant_assessments):
        retrieved_relevant = len(set(recs[:k]) & set(relevant))
        recall = retrieved_relevant / len(relevant) if relevant else 0
        total_recall += recall
    return total_recall / len(recommendations) if recommendations else 0

def mean_average_precision_at_k(recommendations, relevant_assessments, k):
    total_ap = 0
    for recs, relevant in zip(recommendations, relevant_assessments):
        ap = 0
        relevant_count = 0
        for i, rec in enumerate(recs[:k]):
            if rec in relevant:
                relevant_count += 1
                ap += relevant_count / (i + 1)
        ap /= min(k, len(relevant)) if relevant else 1
        total_ap += ap
    return total_ap / len(recommendations) if recommendations else 0


# test_cases = [
#     {
#         "query": "I am hiring for Java developers who can also collaborate effectively with my business teams.",
#         "expected": ["Assessment A", "Assessment B"]  
#     },
#     {
#         "query": "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script.",
#         "expected": ["Assessment C", "Assessment D"]  
#     },
#     {
#         "query": "Here is a JD text, can you recommend some assessment that can help me screen applications.",
#         "expected": ["Assessment E", "Assessment F"]  
#     },
#     {
#         "query": "I am hiring for an analyst and want applications to screen using Cognitive and personality tests.",
#         "expected": ["Assessment G", "Assessment H"]  
#     }
# ]

# def run_tests():
#     for i, test_case in enumerate(test_cases):
#         query = test_case["query"]
#         expected = test_case["expected"]
        
        
#         recommendations = recommend_assessments(query, assessments_df.to_dict(orient='records'))
        
        
#         recommended_names = [rec['name'] for rec in recommendations]
        
        
#         recall = mean_recall_at_k([recommended_names], [expected], k=3)
#         map_score = mean_average_precision_at_k([recommended_names], [expected], k=3)
        
        
#         print(f"Test Case {i + 1}:")
#         print(f"Query: {query}")
#         print(f"Expected: {expected}")
#         print(f"Recommended: {recommended_names}")
#         print(f"Mean Recall@3: {recall:.2f}")
#         print(f"Mean Average Precision@3: {map_score:.2f}")
#         print("---")


# run_tests()

if __name__ == "__main__":
    start_time = time.time()
    scrape_shl_assessments()
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")