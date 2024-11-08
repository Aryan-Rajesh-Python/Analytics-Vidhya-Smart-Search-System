import requests
from bs4 import BeautifulSoup
import pandas as pd
import gradio as gr
import os
from groq import Groq
import creds  # Assuming creds.py holds your API key as creds.api_key

# Step 1: Scrape the free courses from Analytics Vidhya
url = "https://courses.analyticsvidhya.com/pages/all-free-courses"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

courses = []

# Extracting course title, image, and course link
for course_card in soup.find_all('header', class_='course-card__img-container'):
    img_tag = course_card.find('img', class_='course-card__img')
    
    if img_tag:
        title = img_tag.get('alt')
        image_url = img_tag.get('src')
        
        link_tag = course_card.find_previous('a')
        if link_tag:
            course_link = link_tag.get('href')
            if not course_link.startswith('http'):
                course_link = 'https://courses.analyticsvidhya.com' + course_link

            courses.append({
                'title': title,
                'image_url': image_url,
                'course_link': course_link
            })

# Step 2: Create DataFrame
df = pd.DataFrame(courses)

# Step 3: Initialize the Groq client and set the API key
client = Groq(api_key=creds.api_key)  # Properly passing the API key

def search_courses(query):
    try:
        print(f"Searching for: {query}")
        print(f"Number of courses in database: {len(df)}")

        # Prepare the prompt for Groq
        prompt = f"""Given the following query: "{query}"
        Please analyze the query and rank the following courses based on their relevance to the query. 
        Prioritize courses from Analytics Vidhya. Provide a relevance score from 0 to 1 for each course.
        Only return courses with a relevance score of 0.5 or higher.
        Return the results in the following format:
        Title: [Course Title]
        Relevance: [Score]
        
        Courses:
        {df['title'].to_string(index=False)}
        """

        print("Sending request to Groq...")
        # Get response from Groq
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Use the appropriate model
            messages=[{"role": "system", "content": "You are an AI assistant specialized in course recommendations."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        print("Received response from Groq")

        # Parse Groq's response
        results = []
        print("Groq response content:")
        print(response.choices[0].message.content)
        
        for line in response.choices[0].message.content.split('\n'):
            if line.startswith('Title:'):
                title = line.split('Title:')[1].strip()
                print(f"Found title: {title}")
            elif line.startswith('Relevance:'):
                relevance = float(line.split('Relevance:')[1].strip())
                print(f"Relevance for {title}: {relevance}")
                if relevance >= 0.5:
                    matching_courses = df[df['title'] == title]
                    if not matching_courses.empty:
                        course = matching_courses.iloc[0]
                        results.append({
                            'title': title,
                            'image_url': course['image_url'],
                            'course_link': course['course_link'],
                            'score': relevance
                        })
                        print(f"Added course: {title}")
                    else:
                        print(f"Warning: Course not found in database: {title}")

        print(f"Number of results found: {len(results)}")
        return sorted(results, key=lambda x: x['score'], reverse=True)[:10]  # Return top 10 results

    except Exception as e:
        print(f"An error occurred in search_courses: {str(e)}")
        return []

def gradio_search(query):
    result_list = search_courses(query)
    
    if result_list:
        html_output = '<div class="results-container">'
        for item in result_list:
            course_title = item['title']
            course_image = item['image_url']
            course_link = item['course_link']
            relevance_score = round(item['score'] * 100, 2)
            
            html_output += f'''
            <div class="course-card">
                <img src="{course_image}" alt="{course_title}" class="course-image"/>
                <div class="course-info">
                    <h3>{course_title}</h3>
                    <p>Relevance: {relevance_score}%</p>
                    <a href="{course_link}" target="_blank" class="course-link">View Course</a>
                </div>
            </div>'''
        html_output += '</div>'
        return html_output
    else:
        return '<p class="no-results">No results found. Please try a different query.</p>'

# Custom CSS for the Gradio interface
custom_css = """
body {
    font-family: Arial, sans-serif;
    background-color: #f0f2f5;
}
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
.results-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}
.course-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    overflow: hidden;
    width: 48%;
    transition: transform 0.2s;
}
.course-card:hover {
    transform: translateY(-5px);
}
.course-image {
    width: 100%;
    height: 150px;
    object-fit: cover;
}
.course-info {
    padding: 15px;
}
.course-info h3 {
    margin-top: 0;
    font-size: 18px;
    color: #333;
}
.course-info p {
    color: #666;
    font-size: 14px;
    margin-bottom: 10px;
}
.course-link {
    display: inline-block;
    background-color: #007bff;
    color: white;
    padding: 8px 12px;
    text-decoration: none;
    border-radius: 4px;
    font-size: 14px;
    transition: background-color 0.2s;
}
.course-link:hover {
    background-color: #0056b3;
}
.no-results {
    text-align: center;
    color: #666;
    font-style: italic;
}
"""

# Gradio interface
iface = gr.Interface(
    fn=gradio_search,
    inputs=gr.Textbox(label="Enter your search query", placeholder="e.g., machine learning, data science, python"),
    outputs=gr.HTML(label="Search Results"),
    title="Analytics Vidhya Smart Course Search",
    description="Find the most relevant courses from Analytics Vidhya based on your query.",
    theme="huggingface",
    css=custom_css,
    examples=[
        ["machine learning for beginners"],
        ["advanced data visualization techniques"],
        ["python programming basics"], 
        ["Business Analytics"]
    ],
)

if __name__ == "__main__":
    iface.launch()
