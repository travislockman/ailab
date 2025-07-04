from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models

app = Flask(__name__)
CORS(app)

# Load pretrained ResNet18 model
model = models.resnet18(pretrained=True).eval()

# ImageNet normalization preprocessing
preprocessing = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Load ImageNet class labels
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

@app.route("/api/classify", methods=["POST"])
def classify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    image = Image.open(request.files['file']).convert('RGB')
    input_tensor = preprocessing(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        _, predicted_idx = torch.max(output, 1)
        label = labels[predicted_idx.item()]

    return jsonify({'label': label})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
