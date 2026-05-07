import torch

# Tensors
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.randn(3, 3)
print("Tensor a:", a)
print("Random matrix b:", b)

# Operations
print("a + a:", a + a)
print("Matrix multiply b @ b.T:", b @ b.T)

# Autograd
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1
y.backward()
print(f"x = {x.item()}, dy/dx = {x.grad.item()}")  # Should print 8.0

