import os
import torch
import foolbox as fb
import numpy as np
from PIL import Image
from torchvision import models, transforms
from foolbox.attacks import FGSM

# Load ResNet-18 and set to eval
model = models.resnet18(pretrained=True).eval()
fmodel = fb.PyTorchModel(model, bounds=(0, 1))

# ImageNet normalization (for preprocessing ResNet)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
])
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

# Load ImageNet labels
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Attack config
attack = FGSM()

# Process each image in the images folder
image_dir = "images"
for filename in os.listdir(image_dir):
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')): continue

    # === Load and transform ===
    path = os.path.join(image_dir, filename)
    image = Image.open(path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0)  # shape: (1, 3, 224, 224)
    input_tensor = normalize(img_tensor)

    # === Get original prediction ===
    with torch.no_grad():
        logits = model(input_tensor)
        pred = torch.argmax(logits, dim=1).item()
    print(f"[Original] {filename} → {labels[pred]}")

    # === Generate adversarial example (set epsilon strength here) ===
    label_tensor = torch.tensor([pred])
    epsilon = 0.1  # You can tweak this (0.01–0.1 usually works)
    raw_adv, clipped_adv, is_adv = attack(fmodel, img_tensor, label_tensor, epsilons=epsilon)

    # === Get prediction on adversarial image ===
    with torch.no_grad():
        adv_input = normalize(clipped_adv)
        adv_logits = model(adv_input)
        adv_pred = torch.argmax(adv_logits, dim=1).item()
    print(f"[Adversarial] {filename} → {labels[adv_pred]}")

    # === Save adversarial image ===
    adv_image_np = (clipped_adv.squeeze().permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    adv_img = Image.fromarray(adv_image_np)
    adv_path = os.path.join(image_dir, f"{os.path.splitext(filename)[0]}_foolbox.jpg")
    adv_img.save(adv_path)
    print(f"Saved: {adv_path}\n")