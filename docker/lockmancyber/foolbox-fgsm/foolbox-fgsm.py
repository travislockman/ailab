from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import foolbox as fb
from foolbox.attacks import FGSM
import base64
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model and wrap with Foolbox
model = models.resnet18(pretrained=True).eval()
fmodel = fb.PyTorchModel(model, bounds=(0, 1))

# Transform image (no normalization for Foolbox)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
])

# FGSM attack
attack = FGSM()

@app.route("/api/foolbox-fgsm", methods=["POST"])
def foolbox_fgsm():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    epsilon = float(request.form.get("epsilon", 0.03))
    image = Image.open(request.files['file']).convert('RGB')
    img_tensor = transform(image).unsqueeze(0)

    # Get label prediction (needed for FGSM)
    with torch.no_grad():
        logits = model(img_tensor)
        label = torch.argmax(logits, dim=1)

    _, adv_images, _ = attack(fmodel, img_tensor, label, epsilons=epsilon)
    adv_image = adv_images[0]

    # Convert tensors to base64 PNG
    def to_base64(tensor):
        np_img = (tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(np_img).save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode()

    return jsonify({
        'original': to_base64(img_tensor.squeeze()),
        'adversarial': to_base64(torch.tensor(adv_image).squeeze())
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
