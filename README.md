# document-retrieval
Build a backend for document retrieval. The goal of the task is to generate context for LLMs to use for inference.

**Caching Algorithm**
Created a Queue in server which will store limited number of nodes from vector database from previous quries. For every query from user will be first matched with queries in queue and if similarity (cosine) is above 0.9 than those nodes returned back from the lookup table maintained seperately.  

### Results

First request => time taken `787 ms`
![first_img](./img/first_request.png)

Second Similar request => time taken `54 ms`
![second_img](./img/second_request.png)

Bad request 
![bad_img](./img/bad_request.png)


### Example Request 
---

Health check endpoint 
```shell
curl --location 'localhost:8001/health'
```

Search check endpoint
```shell
curl --location 'localhost:8001/search' --header 'user_id: riondsilva' --header 'Content-Type: application/json' --data '{ "text": "Ingredient Substitutions" , "top_k": 5 , "threshold": 0.3 }'
```


### Docker Image
---
*Run in order

Chroma Image
```shell
docker run -p 8000:8000 chromadb/chroma
```

Postgres Image
```shell
docker run --name user-database -p 5432:5432
 -e POSTGRES_PASSWORD=abcdefgh -d postgres:12.20-alpine3.20   
```
```shell
docker stop user-database
```

Doc-Retrieval 
```shell
git clone https://github.com/RionDsilvaCS/21BCE8083_ML.git
```

Create  `.env` file in the main directory and add the below variables
```
DATABASE_URL="postgresql://postgres:abcdefgh@localhost:5432/postgres"
COLLECTION_NAME="cook_book"
```

Create directory name `data` and add pdf documents 
```
mkdir data
```

Run `store_in_db.py` to save the `./data` content to chromadb
```shell
python store_in_db.py
```

```shell
docker compose up --build
```

### API Endpoints
-- --

`/health` is **GET** endpoint to check if server is boot up

Endpoint
```link
http://127.0.0.1:8001/health
```

Response
```JSON
{
  "Server Status": "Successfully running 🎉"
}
```


`/search` is a **POST** endpoint to conversate with the chatbot

Endpoint
```link
http://127.0.0.1:8001/search
```

Header 
```JSON
{
  "user_id": "R!I@O#N$"
}
```

JSON Body
```json
{
  "text": "How are you?",
  "top_k": 3,
  "threshold": 0.3
}
```

Response 
```JSON
{
  "bot_message": {
    "top_k_results": [
      {
        "message": "I am great 🎉"
      },
      {
        "message": "I am fine"
      },
      {
        "message": "I am good"
      }
    ],
    "top_k": 3,
    "threshold": 0.9
  },
  "user_message": {
    "text": "How are you?",
    "top_k": 3,
    "threshold": 0.9,
    "inference_time (secs)": 1.16
  },
  "user_info": "R!I@O#N$"
}
```
