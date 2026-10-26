# Protocole Expérimental — RoadVision AI

## 1. Contexte et Problématique

### Contexte
La surveillance continue de l'état des infrastructures routières est un enjeu de sécurité publique, économique et environnemental. Les méthodes traditionnelles d'inspection manuelles ou semi-automatisées sont coûteuses, lentes et difficilement déployables à grande échelle. L'usage de la vision par ordinateur embarquée permet une détection automatisée, rapide et cartographiable des dégradations de la chaussée.

### Problématique
Comment détecter et classifier automatiquement des dommages routiers sur des images réelles sous diverses conditions environnementales (variations de luminosité, texture, échelle, occultations partielles), tout en trouvant un compromis mesurable et optimal entre **qualité de détection (mAP, rappel)** et **rapidité d'inférence (latence en ms)** ?

---

## 2. Formulation du Problème : Entrées, Sorties et Contraintes

- **Entrées (Inputs) :**
  - Images RGB issues du benchmark RDD2022 (Road Damage Dataset 2022).
  - Résolution nominale standardisée : $640 \times 640$ pixels.
- **Sorties (Outputs) :**
  - Boîtes englobantes délimitant chaque dommage : $(x_{center}, y_{center}, width, height)$ normalisées $\in [0, 1]$.
  - Score de confiance $c \in [0, 1]$.
  - Identifiant de classe parmi les 4 catégories officielles retenues :
    - `0 - D00` : Fissure longitudinale
    - `1 - D10` : Fissure transversale
    - `2 - D20` : Fissuration en réseau (alligator / faïençage)
    - `3 - D40` : Nid-de-poule (pothole)
- **Contraintes et règles d'or :**
  1. **Zéro fuite d'information (No Data Leakage) :** Les partitions `train`, `val`, `test` sont formées avant tout entraînement. Le jeu `test` reste **strictement verrouillé** et n'intervient à aucun moment dans le réglage des hyperparamètres ou l'early stopping.
  2. **Intégrité spatiale :** Pas de split aléatoire naïf si des images consécutives proviennent d'une même séquence vidéo ou route.
  3. **Pas d'hallucination de métadonnées :** RDD2022 ne garantit pas de coordonnées GPS synchronisées précises sur toutes ses sources. Aucune coordonnée GPS fictive ne sera injectée sans mention explicite de simulation.

---

## 3. Hypothèses Scientifiques Initiales

- **Hypothèse H1 (Architecture & Compromis mAP/Vitesse) :**
  Les architectures fondées sur CNN (ex: YOLOv8) et celles fondées sur Transformer (ex: RT-DETR) présentent des compromis différents : le Transformer peut capturer un contexte global supérieur pour les fissures complexes étendues (D20), mais au prix d'un coût de calcul et d'une mémoire crête supérieurs à ceux de YOLO.
- **Hypothèse H2 (Augmentation de données) :**
  L'application de transformations telles que la mosaïque (*Mosaic*) et les variations photométriques (HSV) améliore la généralisation sur les conditions d'éclairage difficiles, mais une augmentation géométrique excessive peut déformer la sémantique directionnelle des fissures (notamment la distinction critique entre D00 longitudinale et D10 transversale).
- **Hypothèse H3 (Résolution d'entrée) :**
  Une résolution plus élevée ($640 \times 640$ vs $480 \times 480$) améliore significativement le rappel sur les petits défauts (nids-de-poule lointains D40 et fissures fines), au détriment de la latence d'inférence.

---

## 4. Métriques d'Évaluation Standardisées

Toutes les évaluations sont exécutées sur le **même jeu de test verrouillé** avec les métriques COCO officielles :

1. **Précision & Rappel :**
   - $\text{Precision} = \frac{TP}{TP + FP}$
   - $\text{Recall} = \frac{TP}{TP + FN}$
2. **mAP (Mean Average Precision) :**
   - **mAP@50 (IoU = 0.50) :** Indicateur standard de détection d'objet.
   - **mAP@50:95 (IoU de 0.50 à 0.95 par pas de 0.05) :** Métrique principale de rigueur pour l'alignement précis des boîtes.
3. **Métriques d'efficience opérationnelle :**
   - **Latence moyenne d'inférence (ms/image)** mesurée après warmup (batch size = 1 et batch size = 8).
   - **FPS (Frames Per Second)**.
   - **Empreinte mémoire VRAM / RAM crête (Mo/Go)**.
   - **Taille du modèle (nombre de paramètres et poids en Mo)**.

---

## 5. Règle Objective de Sélection du Meilleur Modèle

Le modèle sélectionné pour le déploiement applicatif final sera déterminé selon la fonction de score multicritère suivante, définie **a priori** :

$$\text{Score} = \text{mAP}_{50:95} + 0.2 \times \text{Recall}_{\text{D40}} - \lambda \times \max(0, \text{Latence}_{\text{ms}} - 50)$$

avec $\lambda = 0.002$. Un bonus explicite est accordé au rappel de la classe **D40 (nid-de-poule)** en raison de sa criticité immédiate pour la sécurité des usagers de la route.

---

## 6. Analyse des Échecs et Cas Limites (Failure Analysis)

Pour chaque modèle évalué, un audit systématique d'au moins **10 cas limites ou échecs** sera documenté :
- Faux positifs générés par des ombres portées, joints de dilatation ou marquages au sol usés.
- Faux négatifs sur fissures fines ou chaussées humides à faible contraste.
- Confusions de classes entre fissures longitudinales (D00) et transversales (D10) selon l'angle de prise de vue.
- Détections multiples redondantes ou boîtes fragmentées sur fissures alligator (D20).
