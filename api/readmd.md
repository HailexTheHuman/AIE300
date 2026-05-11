Project Kickoff - A simple API

to install dependencies open at terminal and enter the command:
    pip install -r requirements.txt

to run the server run the following command in a terminal:
    uvicorn main:app --reload

available endpoints are:
    GET /
        reads root
    GET /items/
        reads all items
    POST /items/
        create item
    GET /items/{item_id}
        reads a specific item by id
    PUT /items/{item_id}
        updates a specific item by id
    DELETE /items/{item_id}
        deletes a specific item by id
    GET /docs/
        reads the documentation
    POST /predict/
        Classifies an Iris flower based on its measurements.
        Request: json of features ex: { "features": [5.1, 3.5, 1.4, 0.2] }
        Features order: sepal length, sepal width, petal length, petal width (all in cm).
        Response: json of prediction and confidence ex: { "prediction": "setosa", "confidence": 0.99 }




## Part 1: Docker Model Runner

- **Model pulled:** ai/smollm2
- **Endpoint:** http://model-runner.docker.internal/engines/llama.cpp/v1/chat/completions
- **Note:** On Windows, the Model Runner endpoint is only accessible from inside 
  Docker containers via `model-runner.docker.internal`, not from the host via localhost.
- **Test command:**
docker run --rm curlimages/curl curl -X POST "http://model-runner.docker.internal/engines/llama.cpp/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model": "ai/smollm2", "messages": [{"role": "user", "content": "Explain what Docker is in one sentence."}]}'

- **Response:** {"choices":[{"finish_reason":"stop","index":0,"message":{"role":"assistant","content":"Docker is an open-source platform that allows users to containerize applications into isolated environments, making it easier to manage and share software."}}],"created":1778525687,"model":"bf6f20a603055433b4b998119e17928fc4a89b35c42855dd7eada105058cae0a","system_fingerprint":"b1-e365e65","object":"chat.completion","usage":{"completion_tokens":29,"prompt_tokens":38,"total_tokens":67,"prompt_tokens_details":{"cached_tokens":37}},"id":"chatcmpl-7wEvUuIdRzmGn86tVSzUUrBwSRFuxl7Q","timings":{"cache_n":37,"prompt_n":1,"prompt_ms":43.669,"prompt_per_token_ms":43.669,"prompt_per_second":22.899539719251646,"predicted_n":29,"predicted_ms":404.075,"predicted_per_token_ms":13.933100    927 100    818 100    109   1740    231                              0



