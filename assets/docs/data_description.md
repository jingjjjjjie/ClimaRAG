## 📊 Data Description

The dataset used in this project focuses on **six key dimensions related to climate change**, including:

1. **Factors influencing climate change**  
2. **Impacts of climate change**  
3. **Monitoring methods**  
4. **Policies and response strategies**  
5. **Climate adaptation and mitigation measures**  
6. **Socioeconomic and environmental interactions**

Relevant academic literature was retrieved from the **Web of Science (WoS)** database using **All Fields keyword search** queries.  
The search results were imported into **EndNote**, which was chosen because it allows direct access to the **full text** of the referenced publications — ensuring data completeness and reliability for this research.

### 🔧 Data Processing Workflow

The data processing pipeline involved two major stages:

1. **Metadata Extraction**  
   Export bibliographic information (e.g., titles, authors, publication years) from EndNote.

2. **Full-text Integration**  
   Import the complete PDF files of the retrieved documents for embedding and text analysis.

The final dataset was stored in **JSON format**, facilitating vectorization and retrieval tasks in the RAG pipeline.

Out of approximately **600 retrieved papers**, **293 full-text PDFs** were successfully obtained and processed, forming the final corpus used for the retrieval-augmented generation system.

### 🧭 Data Location

The data is locate under src/data, under the name data.json. Do remember to change the data loading path in src/config/settings.py