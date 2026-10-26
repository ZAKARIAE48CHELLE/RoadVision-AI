"""
Dataset Audit Script for RDD2022 (United States subset)
Performs deep analysis on:
- File integrity and pairing (images vs annotations)
- Image dimensions and channels
- Class distributions and box counts
- Empty/Negative images
- Bounding box sizes (small, medium, large according to COCO definitions)
- Aspect ratios and area ratios
- Generates summary figures
"""

import os
import glob
import xml.etree.ElementTree as ET
from collections import Counter
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

def audit_dataset(data_dir="data/raw/United_States"):
    train_img_dir = os.path.join(data_dir, "train", "images")
    train_xml_dir = os.path.join(data_dir, "train", "annotations", "xmls")
    test_img_dir = os.path.join(data_dir, "test", "images")

    train_imgs = sorted(os.listdir(train_img_dir))
    train_xmls = sorted(os.listdir(train_xml_dir))
    test_imgs = sorted(os.listdir(test_img_dir))

    print("=" * 60)
    print("1. File Counts & Pairing Verification")
    print("=" * 60)
    print(f"Train Images count : {len(train_imgs)}")
    print(f"Train XMLs count   : {len(train_xmls)}")
    print(f"Test Images count  : {len(test_imgs)}")

    # Check 1-to-1 matching
    img_basenames = {os.path.splitext(f)[0] for f in train_imgs}
    xml_basenames = {os.path.splitext(f)[0] for f in train_xmls}

    missing_xml = img_basenames - xml_basenames
    missing_img = xml_basenames - img_basenames
    print(f"Images without XML : {len(missing_xml)}")
    print(f"XMLs without Image : {len(missing_img)}")

    # Analyze Annotations
    print("\n" + "=" * 60)
    print("2. Parsing Annotations and Bounding Boxes")
    print("=" * 60)

    class_counter = Counter()
    boxes_per_image = []
    box_records = []
    images_with_no_boxes = 0
    img_resolutions = Counter()

    for xml_file in train_xmls:
        xml_path = os.path.join(train_xml_dir, xml_file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        size_elem = root.find("size")
        if size_elem is not None:
            w = int(size_elem.find("width").text)
            h = int(size_elem.find("height").text)
            d = int(size_elem.find("depth").text) if size_elem.find("depth") is not None else 3
            img_resolutions[(w, h, d)] += 1
        else:
            w, h = 640, 640

        objects = root.findall("object")
        n_boxes = len(objects)
        boxes_per_image.append(n_boxes)

        if n_boxes == 0:
            images_with_no_boxes += 1

        for obj in objects:
            cls_name = obj.find("name").text.strip()
            class_counter[cls_name] += 1

            bndbox = obj.find("bndbox")
            xmin = float(bndbox.find("xmin").text)
            ymin = float(bndbox.find("ymin").text)
            xmax = float(bndbox.find("xmax").text)
            ymax = float(bndbox.find("ymax").text)

            bw = max(0, xmax - xmin)
            bh = max(0, ymax - ymin)
            area = bw * bh
            rel_area = area / (w * h) if (w * h) > 0 else 0

            # COCO scale definitions
            # Small: area < 32^2 (1024), Medium: 32^2 <= area <= 96^2 (9216), Large: area > 96^2
            scale = "small" if area < 1024 else ("medium" if area <= 9216 else "large")

            box_records.append({
                "image_id": os.path.splitext(xml_file)[0],
                "class": cls_name,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "width": bw,
                "height": bh,
                "aspect_ratio": bw / (bh + 1e-6),
                "area": area,
                "rel_area": rel_area,
                "scale": scale
            })

    df_boxes = pd.DataFrame(box_records)

    print(f"Total Bounding Boxes Detected : {len(df_boxes)}")
    print(f"Images with 0 annotations (negative samples) : {images_with_no_boxes} ({images_with_no_boxes/len(train_xmls)*100:.2f}%)")
    print(f"Images with >= 1 annotations                : {len(train_xmls) - images_with_no_boxes}")
    print(f"Average boxes per image                     : {np.mean(boxes_per_image):.2f} (max: {np.max(boxes_per_image)})")

    print("\nResolution Distribution:")
    for res, count in img_resolutions.items():
        print(f"  {res[0]}x{res[1]} (channels: {res[2]}) : {count} images ({count/len(train_xmls)*100:.1f}%)")

    print("\nClass Distribution:")
    for cls_name, count in class_counter.most_common():
        pct = (count / len(df_boxes)) * 100 if len(df_boxes) > 0 else 0
        print(f"  - {cls_name:<10}: {count:>6} boxes ({pct:.2f}%)")

    print("\nBounding Box Scale Breakdown (COCO standard):")
    if not df_boxes.empty:
        for scale, cnt in df_boxes["scale"].value_counts().items():
            print(f"  - {scale:<10}: {cnt:>6} ({cnt/len(df_boxes)*100:.2f}%)")

    # Save summary figures
    os.makedirs("results/figures", exist_ok=True)
    os.makedirs("data/metadata", exist_ok=True)

    df_boxes.to_csv("data/metadata/raw_boxes_analysis.csv", index=False)

    # Plot 1: Class Distribution
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=list(class_counter.keys()), y=list(class_counter.values()), palette="viridis")
    plt.title("Distribution des Classes dans RDD2022 (United States - Train)", fontsize=13, fontweight="bold")
    plt.xlabel("Code Dégradation", fontsize=11)
    plt.ylabel("Nombre d'instances annotées", fontsize=11)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')
    plt.tight_layout()
    plt.savefig("results/figures/classes_distribution.png", dpi=200)
    plt.close()

    # Plot 2: Box sizes & aspect ratio distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.countplot(data=df_boxes, x="scale", order=["small", "medium", "large"], palette="magma", ax=axes[0])
    axes[0].set_title("Répartition des Tailles de Boîtes (Norme COCO)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Catégorie de taille", fontsize=10)
    axes[0].set_ylabel("Nombre de boîtes", fontsize=10)

    sns.boxplot(data=df_boxes, x="class", y="rel_area", palette="Set2", ax=axes[1], showfliers=False)
    axes[1].set_title("Surface Relative par Classe (Box Area / Image Area)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Classe", fontsize=10)
    axes[1].set_ylabel("Surface relative", fontsize=10)

    plt.tight_layout()
    plt.savefig("results/figures/box_geometry_distribution.png", dpi=200)
    plt.close()

    print("\n" + "=" * 60)
    print("Figures successfully generated in results/figures/ :")
    print("  - results/figures/classes_distribution.png")
    print("  - results/figures/box_geometry_distribution.png")
    print("  - data/metadata/raw_boxes_analysis.csv")
    print("=" * 60)

if __name__ == "__main__":
    audit_dataset()
