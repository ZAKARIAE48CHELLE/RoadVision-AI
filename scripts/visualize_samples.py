"""
Visualize Sample Ground Truth Annotations from RDD2022
Extracts 6 diverse annotated images (including rare classes and multi-defect cases)
and saves them as an annotated visual figure.
"""

import os
import glob
import xml.etree.ElementTree as ET
import cv2
import matplotlib.pyplot as plt

CLASS_COLORS = {
    "D00": (52, 152, 219),   # Blue: Longitudinal crack
    "D10": (46, 204, 113),   # Green: Transverse crack
    "D20": (241, 196, 15),   # Yellow: Alligator crack
    "D40": (231, 76, 60),    # Red: Pothole
}

def draw_annotations(img_path, xml_path):
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for obj in root.findall("object"):
        cls_name = obj.find("name").text.strip()
        color = CLASS_COLORS.get(cls_name, (200, 200, 200))
        
        bndbox = obj.find("bndbox")
        xmin = int(float(bndbox.find("xmin").text))
        ymin = int(float(bndbox.find("ymin").text))
        xmax = int(float(bndbox.find("xmax").text))
        ymax = int(float(bndbox.find("ymax").text))
        
        # Draw rectangle
        cv2.rectangle(img_rgb, (xmin, ymin), (xmax, ymax), color, 2)
        
        # Label badge
        label = f"{cls_name}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img_rgb, (xmin, max(0, ymin - 18)), (xmin + w + 4, ymin), color, -1)
        cv2.putText(img_rgb, label, (xmin + 2, max(12, ymin - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        
    return img_rgb

def visualize_samples():
    xml_dir = "data/raw/United_States/train/annotations/xmls"
    img_dir = "data/raw/United_States/train/images"
    
    # Select images having D40 (pothole) and multi-class
    pothole_samples = []
    alligator_samples = []
    crack_samples = []
    
    for xml_file in sorted(os.listdir(xml_dir)):
        path = os.path.join(xml_dir, xml_file)
        tree = ET.parse(path)
        classes = {obj.find("name").text.strip() for obj in tree.getroot().findall("object")}
        base = os.path.splitext(xml_file)[0]
        
        if "D40" in classes and len(pothole_samples) < 2:
            pothole_samples.append(base)
        elif "D20" in classes and len(alligator_samples) < 2:
            alligator_samples.append(base)
        elif ("D00" in classes or "D10" in classes) and len(crack_samples) < 2:
            crack_samples.append(base)
            
        if len(pothole_samples) == 2 and len(alligator_samples) == 2 and len(crack_samples) == 2:
            break
            
    selected = pothole_samples + alligator_samples + crack_samples
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, base in enumerate(selected):
        img_p = os.path.join(img_dir, f"{base}.jpg")
        xml_p = os.path.join(xml_dir, f"{base}.xml")
        vis_img = draw_annotations(img_p, xml_p)
        axes[idx].imshow(vis_img)
        axes[idx].set_title(f"Sample: {base}", fontsize=11, fontweight="bold")
        axes[idx].axis("off")
        
    plt.tight_layout()
    plt.savefig("results/figures/annotated_samples.png", dpi=200)
    plt.close()
    print("Sample visualization saved to results/figures/annotated_samples.png")

if __name__ == "__main__":
    visualize_samples()
