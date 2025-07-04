from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import base64
import foolbox as fb
from foolbox.attacks import LinfFastGradientAttack
import eagerpy as ep

app = Flask(__name__)
CORS(app)

# Load pretrained ResNet18
model = models.resnet18(pretrained=True).eval()

# Normalized transform (for classification)
preprocessing = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# Raw transform (no normalization)
raw_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
])

# Load ImageNet labels
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Foolbox model wrapper
fmodel = fb.PyTorchModel(model, bounds=(0, 1), preprocessing=dict(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
))
attack = LinfFastGradientAttack()

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


@app.route("/api/foolbox", methods=["POST"])
def foolbox_attack():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    epsilon = float(request.form.get("epsilon", 0.03))
    image = Image.open(request.files['file']).convert('RGB')

    # Prepare input for Foolbox
    raw_tensor = raw_transform(image).unsqueeze(0)  # [1, 3, 224, 224]
    ep_tensor = ep.astensor(raw_tensor)

    print("DEBUG: raw_tensor shape →", raw_tensor.shape)

    # Get label from normalized input
    with torch.no_grad():
        norm_tensor = preprocessing(image).unsqueeze(0)
        output = model(norm_tensor)
        _, label_tensor = torch.max(output, 1)
    label = label_tensor.item()

    # Run Foolbox attack
    _, advs, _ = attack(fmodel, ep_tensor, torch.tensor([label]), epsilons=epsilon)
    adversarial_ep = advs[0]

    if adversarial_ep is None:
        return jsonify({'error': 'Adversarial image generation failed'})

    # Convert EagerPy tensor back to PyTorch for processing
    adversarial_tensor = adversarial_ep.raw
    adversarial_tensor = torch.clamp(adversarial_tensor, 0, 1)

    # Unnormalize for display
    inv_normalize = transforms.Normalize(
        mean=[-0.485 / 0.229, -0.456 / 0.224, -0.406 / 0.225],
        std=[1 / 0.229, 1 / 0.224, 1 / 0.225]
    )
    image_for_output = inv_normalize(adversarial_tensor.squeeze(0))
    image_for_output = torch.clamp(image_for_output, 0, 1)

    # Convert to base64 PNG
    adversarial_pil = transforms.ToPILImage()(image_for_output)
    buf = io.BytesIO()
    adversarial_pil.save(buf, format='PNG')
    base64_image = base64.b64encode(buf.getvalue()).decode()

    # Classify adversarial
    with torch.no_grad():
        new_pred = model(adversarial_tensor)
        _, new_label_idx = torch.max(new_pred, 1)
        new_label = labels[new_label_idx.item()]

    return jsonify({
        'original_label': labels[label],
        'adversarial_label': new_label,
        'adversarial_image_base64': base64_image
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
