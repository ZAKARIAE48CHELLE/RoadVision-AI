# RoadVision AI — Intelligent Road Damage Detection & Mapping

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11-red.svg)](https://pytorch.org/)
[![Ultralytics](https://img.shields.io/badge/YOLO-v8-brightgreen.svg)](https://ultralytics.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

RoadVision AI est un système de vision par ordinateur conçu pour détecter, classifier et cartographier les dégradations de la chaussée (fissures, nids-de-poule) à partir du benchmark international **RDD2022**. Le projet met en œuvre un cadre expérimental rigoureux et reproductible comparant deux familles d'architectures de pointe : **YOLO** (représentant CNN / ancre-free) et **RT-DETR** (détecteur à base de Transformers temps réel).

---

## 🏗️ Architecture du Projet

```text
roadvision-ai/
├── README.md                          # Documentation générale du projet
├── requirements.txt                   # Dépendances Python versionnées
├── .gitignore                         # Règles d'exclusion Git (données brutes, poids, caches)
├── configs/
│   ├── dataset.yaml                   # Définitions des classes RDD2022, chemins et splits
│   ├── yolo.yaml                      # Hyperparamètres et stratégie d'entraînement YOLO
│   ├── rtdetr.yaml                    # Hyperparamètres et stratégie RT-DETR
│   └── experiments.yaml               # Plan expérimental, ablations et règles de sélection
├── data/
│   ├── raw/                           # Dataset brut téléchargé (non versionné)
│   ├── processed/                     # Dataset prétraité au format standardisé (YOLO/COCO)
│   ├── splits/                        # Manifestes d'échantillonnage traçables (manifest.csv)
│   └── metadata/                      # Informations complémentaires (pays, résolutions)
├── notebooks/
│   ├── 01_dataset_exploration.ipynb   # Audit visuel, distribution des classes, analyse des boîtes
│   └── 02_error_analysis.ipynb        # Analyse approfondie des erreurs et cas limites
├── src/
│   ├── data/                          # Modules de chargement, conversion et vérification des données
│   ├── training/                      # Scripts d'entraînement modulaires
│   ├── evaluation/                    # Calcul des métriques COCO, latence et profiling
│   ├── inference/                     # Pipelines d'inférence image
│   ├── video/                         # Traitement de flux vidéo et dédoublonnage temporel
│   └── mapping/                       # Géoréférencement et projection cartographique
├── app/
│   └── streamlit_app.py               # Interface interactive de démonstration
├── scripts/
│   └── check_environment.py          # Script de diagnostic automatique de l'environnement
├── tests/                             # Tests unitaires et vérifications d'intégrité
├── results/
│   ├── metrics/                       # Tableaux de résultats et métriques d'évaluation
│   ├── figures/                       # Graphiques de distribution, courbes PR et pertes
│   ├── failures/                      # Cas d'échecs documentés (10+ cas limites)
│   └── resource_logs/                 # Profiling mémoire et temps GPU/CPU
└── docs/
    ├── protocol.md                    # Protocole scientifique, hypothèses et métriques
    ├── experiments.md                 # Journal détaillé des expériences
    └── final_report.md                # Rapport de synthèse
```

---

## 🏷️ Classes de Dégradations RDD2022

| Code | Classe | Description |
|---|---|---|
| **D00** | Fissure longitudinale | Fissure parallèle à la trajectoire des véhicules |
| **D10** | Fissure transversale | Fissure perpendiculaire au sens de circulation |
| **D20** | Fissuration en réseau (Alligator) | Maillage polygonal interconnecté (faïençage) |
| **D40** | Nid-de-poule (Pothole) | Cavité ou trou dans l'enrobé |

---

## ⚙️ Installation & Démarrage Rapide

### 1. Cloner le dépôt
```bash
git clone https://github.com/ZAKARIAE48CHELLE/RoadVision-AI.git
cd RoadVision-AI
```

### 2. Créer l'environnement et installer les dépendances
```bash
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Exécuter le diagnostic d'environnement
```bash
python scripts/check_environment.py
```

Le script contrôle automatiquement la version de Python, la détection GPU/CUDA, la RAM disponible, l'espace disque et la présence des bibliothèques requises.

---

## 🧪 Protocole Expérimental
Consultez le document de référence [`docs/protocol.md`](docs/protocol.md) pour les détails sur :
- Les hypothèses scientifiques formalisées (H1, H2, H3).
- La stratégie de séparation sans fuite d'information (*No Data Leakage*).
- Les métriques standardisées ($mAP_{50}$, $mAP_{50:95}$, latence, empreinte mémoire).
- La règle objective de sélection du modèle final.
