# Analytics Vidhya Smart Search System

## Goal:
To create a smart search tool that allows users to find relevant free courses on Analytics Vidhya’s platform.

## Approach:

1. **Data Collection**:
   - The first step was to scrape free course titles and relevant metadata (such as course links and images) from Analytics Vidhya’s platform using BeautifulSoup.

2. **Model Selection**:
   - Initially, I experimented with the **Groq API** for generating embeddings and conducting searches. This API was used to generate embeddings for both the user query and the course titles.

3. **Relevance Ranking**:
   - To match user queries with the most relevant courses, I computed **cosine similarity** between the user’s query embedding and the course title embeddings.
   - This similarity score helped rank the courses based on relevance, ensuring that the most relevant courses are prioritized.

4. **Real-Time Autocomplete Feature**:
   - A real-time autocomplete feature was implemented to suggest the top 3 course titles based on the user's input. This enhances the user experience by providing quick suggestions as the user types.

5. **Gradio Interface**:
   - The user interface was designed and deployed using **Gradio**, offering a clean, user-friendly layout.
   - The interface dynamically displays course details such as the title, image, link, and a relevance score.

6. **Deployment on Hugging Face Spaces**:
   - The search tool was deployed on **Hugging Face Spaces**, making it publicly accessible for users to try out.
   - The interface was customized using **CSS** to enhance its visual appeal and responsiveness, making it a pleasant experience across devices.

### Model Used:
- **Groq Model**: [https://huggingface.co/spaces/aryan79/Analytics_Vidhya_Smart_Search_System](https://huggingface.co/spaces/aryan79/Analytics_Vidhya_Smart_Search_System)

### Key Features:
- **Course Search**: Find relevant courses on Analytics Vidhya based on your query.
- **Autocomplete**: Real-time suggestions as you type.
- **Relevance Scoring**: Courses are ranked based on relevance to the search query.
- **User-Friendly Interface**: Clean and responsive layout for easy navigation.
