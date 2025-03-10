# Wiki Tutor

Wiki Tutor is a web-based application built with Flask that helps users learn about any topic by fetching and summarizing Wikipedia content. The app retrieves the main text and internal links for a given topic and uses a language model (LLM) to generate summaries at basic, intermediate, and advanced levels. The end goal is to create a dynamic learning path for users, showcasing both technical development and cybersecurity skills.

## Features

- **Dynamic Topic Search:** Users enter a topic to fetch related Wikipedia content.
- **Content Extraction:** Retrieve both page text and internal links (related content) from Wikipedia.
- **Content Summarization:** Use a cost-effective LLM to summarize content into multiple learning levels.
- **Data Caching:** Store summarized data in a database to reduce redundant API calls.
- **Learning Path Organization:** Arrange the summarized topics into a coherent learning sequence.
- **Future Enhancements:** Integrate security testing phases (offensive, defensive, and purple teaming) and document all steps for a comprehensive portfolio.

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** Undecided
- **Database:** SQL
- **Caching:** Redis 
- **APIs:** Wikipedia API (MediaWiki API) for fetching data
- **Deployment:** AWS (EC2, RDS, ElastiCache) with potential Docker containerization
- **Version Control:** Git and GitHub

