import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load and split data
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Convert to tensors
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.LongTensor(y_test)

# DataLoader
dataset = TensorDataset(X_train_t, y_train_t)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# Model
class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(16, 3)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))

model = SimpleClassifier()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# Training loop
for epoch in range(100):
    model.train()
    total_loss = 0
    for X_batch, y_batch in loader:
        optimizer.zero_grad()
        out = model(X_batch)
        loss = loss_fn(out, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/100 - Loss: {total_loss:.4f}")

# Test accuracy
model.eval()
with torch.no_grad():
    preds = model(X_test_t).argmax(dim=1)
    acc = (preds == y_test_t).float().mean()
    print(f"Test Accuracy: {acc.item() * 100:.2f}%")

# Save model
torch.save(model.state_dict(), "model.pth")
print("Model saved to model.pth")