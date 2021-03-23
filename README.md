# Tracking Project 


### 15/03/2021 - 19/03/2021

* Évaluation des techniques d'OF + tracking classique sur la vidéo du projet Tracking 
* Résultats peu convaincants. 
* Ressource en formation

### 08/03/2021 - 12/03/2021

* Recherche de stratégies permettant d'améliorer le tracking 
* Documentation sur les techniques d'Optic Flow
* Implémentation de la méthode avec OpenCV 
* Les évaluations montrent des compétences intéressantes, potentiellement couplables avec les trackers KCF


### 01/03/2021 - 05/03/2021

    *Amélioration des performances
        * Réduction de la taille de l'image en entrée des trackers
        * Conversion de l'image en niveau de gris (1 channel au lieu de 3) pour le tracker CSRT (KCF requiert les 3 channels)
        * Augmentation significative des fps en traitement, mais à améliorer encore
        * Pas d'impact constaté
    * Utilisation d'un filtre de Kalman pour lisser les vecteurs vitesses et tenter de récupérer des tracking perdus
        * Réduction significative du bruit sur les vecteurs vitesses 
        * Quelques légères imprécisions constatées :
            * À certains moments le vecteur vitesse n'est pas tout à faire colinéaire à la voiture
            * Pourrait être améliorer en ayant accès aux commandes envoyées aux véhicules (correspondrait à l'entrée "control" des filtres de Kalmans)
    * Résultats peu encourageants quant à la reprise des tracking perdus

### 25/02/2021 

* Initialisation of Reveal folder for tracking weekly project advancement
* Added FPS recording 


### 24/02/2021 

* Tracker CSRT gives interesting results. Kinda slow though 
* Found good initialisation parameters for test video
* Seems wise to use colored cars to ease discrimination  
* Started researching ways to compute speed vector 


### 22/02/2021 

Project initialisation: 

* `test_ocv.py` tests tracking using webcam 
* `multi_ocv.py` tries to implement multi-object tracking but currently encounters core segmentation issue 