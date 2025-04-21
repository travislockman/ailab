import torch
from torchvision import models, transforms
from PIL import Image

# === Load ResNet-18 pretrained model ===
model = models.resnet18(pretrained=True)
model.eval()

# === Define image transform ===
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet stats
        std=[0.229, 0.224, 0.225]
    )
])

# === Local image path ===
img_path = "images/my_test_image_original_foolbox.jpg"  # <-- Put your image here
image = Image.open(img_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0)

# === Run through ResNet ===
with torch.no_grad():
    output = model(input_tensor)

# === Load labels from local file ===
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# === Get top prediction ===
_, predicted = output.max(1)
print(f"\n------------\nPrediction: \n{labels[predicted.item()]}\n------------\n")
