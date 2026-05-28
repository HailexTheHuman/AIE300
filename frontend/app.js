const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;
const methodOverride = require('method-override');
require('dotenv').config();
const apiUrl = process.env.API_URL;

app.use(express.json());
app.use(express.urlencoded({extended:true}));
app.use(methodOverride(function (req, res) {
    if (req.body && typeof req.body === 'object' && '_method' in req.body) {
        const method = req.body._method;
        delete req.body._method;
        return method;
    }
}));
app.use(express.static('public'));
app.set('view engine', 'ejs');

app.use((req, res, next) => {
    console.log('Method:', req.method, '| URL:', req.url, '| Body:', req.body);
    next();
});


app.get('/', (req, res) => {
    res.render('index');
});

app.get('/items', async (req, res) => {
    try {
        let items = await fetch(`${apiUrl}/items`).then(response => response.json());
        console.log(items)
        res.render('items', {items: items.items, message: null});
    } catch (error) {
        console.error('Error fetching items:', error);
        console.log(items)
        res.render('items', { items: [], message: 'no items found' });
    }
});

app.post('/items', async (req, res) => {
    console.log('body: ', req.body)
    const newItem = {name: req.body.name, price: parseFloat(req.body.price)};
    try {
        let response = await fetch(`${apiUrl}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newItem)
        });
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`)
        }
        const data = await response.json();
        console.log(data)
        res.redirect(`/items/${data.item.id}`);
    } catch (error) {
        console.error('Error creating item:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/items/:id', async (req, res) => {
    try {
        const itemId = req.params.id;
        let response = await fetch(`${apiUrl}/items/${itemId}`)
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`)
        }
        const item_data = await response.json();
        // .then(response => response.json())
        // .then(item => {
        console.log(item_data)
        res.render('item', { item: item_data.item });
        // });
    } catch (error) {
        console.error('Error fetching item:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.put('/items/:id', async (req, res) => {
    const itemId = req.params.id;
    const updatedItem = {name: req.body.name, price: parseFloat(req.body.price)};
    console.log("put reached in frontend", updatedItem)
    try {
        let response = await fetch(`${apiUrl}/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedItem)
        });
        if (!response.ok) {
            return res.status(response.status).send('Failed to update item');
        }
        const data = await response.json();
        console.log("status", response.status)
        res.redirect(`/items/${data.item_id}`);
    } catch (error) {
        console.error('Error updating item:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.delete('/items/:id', async (req, res) => {
    const itemId = req.params.id;

    try {
        let response = await fetch(`${apiUrl}/items/${itemId}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            return res.status(response.status).send('Failed to delete item');
        }
        let data = await response.json();
        res.redirect('/items');
    } catch (error) {
        console.error('Error deleting item:', error);
        res.status(500).send('Internal Server Error');
    }
});


app.post('/predict', async (req, res) => {
    const features = [
        parseFloat(req.body.f1),
        parseFloat(req.body.f2),
        parseFloat(req.body.f3),
        parseFloat(req.body.f4)
    ];
    const response = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features })
    });
    const data = await response.json();
        res.render('predict', {
            prediction:data.prediction,
            confidence:data.confidence
        });
});


app.get('/predict', async (req, res) => {
    res.render('predict', {
            prediction:0,
            confidence:0
        });
});


app.get('/chat', (req, res) => {
    res.render('chat', { conversation_history: [] });
});

app.post('/chat', async (req, res) => {
    const { message, conversation_history } = req.body;
    const history = conversation_history ? JSON.parse(conversation_history) : [];

    try {
        const response = await fetch(`${apiUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, conversation_history: history })
        });
        const data = await response.json();
        res.render('chat', {
            conversation_history: data.conversation_history
        });
    } catch (error) {
        console.error('Chat error:', error);
        res.status(500).send('Chat error');
    }
});




app.listen(port, () => {
    console.log(`Frontend server running at http://localhost:${port}`);
});