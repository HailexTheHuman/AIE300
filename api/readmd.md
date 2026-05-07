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