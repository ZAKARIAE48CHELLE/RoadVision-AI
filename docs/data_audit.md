# Audit et Analyse des Données — RDD2022 (Sous-ensemble United States)

## 1. Vue d'ensemble du Corpus Extrait

Le sous-ensemble **RDD2022 (United States)** a été extrait et audité de manière exhaustive :
- **Nombre total d'images :** 6 005 images (4 805 `train` avec annotations complètes, 1 200 `test` d'évaluation).
- **Format d'annotation source :** XML PASCAL VOC.
- **Intégrité et appariement :** **100%** de correspondance exacte (4 805 images $\leftrightarrow$ 4 805 fichiers XML, zéro image orpheline, zéro fichier corrompu).
- **Résolution :** Toutes les images sont strictement normalisées à **$640 \times 640 \times 3$ (RGB)**.

---

## 2. Statistiques et Décompte des Dégradations

| Code | Type de dommage routier | Nombre de boîtes | Proportion (%) | Criticité opérationnelle |
|:---:|:---|:---:|:---:|:---|
| **D00** | Fissure longitudinale | 6 750 | 61.29% | Dégradation linéaire fréquente |
| **D10** | Fissure transversale | 3 295 | 29.92% | Dégradation thermique/structurelle |
| **D20** | Fissuration en réseau (Alligator) | 834 | 7.57% | Rupture de portance avancée |
| **D40** | Nid-de-poule (*Pothole*) | 135 | 1.23% | **Danger immédiat pour les usagers** |
| **Total** | | **11 014** | **100.0%** | |

### Analyse du déséquilibre de classes (Imbalance) :
- Les fissures linéaires (**D00** et **D10**) représentent à elles seules **91.21%** des dégradations annotées.
- La classe **D40 (nids-de-poule)** est fortement sous-représentée (seulement 135 instances, soit 1.23%).
- **Recommandation pour l'entraînement :** Nécessité d'appliquer des poids de pertes équilibrés (*class weights* ou *Focal Loss*), et de sur-échantillonner ou cibler des métriques de rappel spécifiques pour D40 lors de l'évaluation finale.

---

## 3. Géométrie et Échelle des Boîtes (Norme COCO)

L'évaluation des surfaces relatives et absolues selon les critères COCO ($area = w \times h$) révèle :
- **Medium ($32^2 \le area \le 96^2$) :** 5 967 boîtes (**54.18%**)
- **Large ($area > 96^2$) :** 4 532 boîtes (**41.15%**)
- **Small ($area < 32^2$) :** 515 boîtes (**4.68%**)

> **Constat géométrique :** Les fissures et dégradations occupent principalement des surfaces moyennes à grandes en raison de leur étalement spatial sur la chaussée. L'aspect ratio des fissures D00 est majoritairement vertical ($w \ll h$) tandis que D10 est horizontal ($w \gg h$), validant le fait que les augmentations de rotation excessive à 90° doivent être évitées afin de ne pas intervertir arbitrairement la sémantique de D00 et D10.

---

## 4. Artefacts et Visualisations Produits

Les figures et métadonnées suivantes sont générées et archivées :
- `results/figures/classes_distribution.png` : Graphique à barres de la distribution des 4 classes.
- `results/figures/box_geometry_distribution.png` : Répartition par catégorie de taille et surface relative par classe.
- `results/figures/annotated_samples.png` : Exemples visuels de vérité terrain avec boîtes englobantes colorées.
- `data/metadata/raw_boxes_analysis.csv` : Audit tabulaire complet des 11 014 boîtes.
