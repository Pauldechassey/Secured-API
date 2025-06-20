# TP Cybersécurité : Sujet D - Analyseur de Composants d'URL

**Objectif :** L'objectif de ce TP est de vous familiariser avec les bases du développement sécurisé (DevSecOps) en créant une API FastAPI qui décompose une URL en ses différents composants (schéma, domaine, port, chemin, paramètres de requête, fragment). Vous allez la tester, analyser son code et ses dépendances, et mettre en place une intégration continue.

**Durée estimée :** 4 heures

**Prérequis :**
*   Python 3.8+ et pip installés
*   Git installé et configuré
*   Un compte GitLab
*   Un éditeur de code (VS Code, PyCharm, etc.)
*   Une connexion internet

---

## Partie 0 : Mise en Place Initiale

1.  **Clonez le dépôt de base pour le Sujet D :**
    Un dépôt GitLab a été préparé avec les squelettes des fichiers nécessaires pour ce sujet. Clonez-le sur votre machine locale :
    ```bash
    git clone https://gitlab.com/epf-cachan/tp1-sujet-d.git
    cd tp1-sujet-d
    ```
    *Remplacez les placeholders par les bonnes valeurs.*

2.  **Explorez les fichiers :**
    Vous trouverez les fichiers `main.py`, `requirements.txt`, `README.md`, `.gitlab-ci.yml`, et `tests/test_main.py` avec des `#TODO` spécifiques à ce sujet. Le modèle Pydantic `HttpUrl` est utilisé pour la validation de base de l'URL en entrée.

---

## Partie 1 : Création de l'Application FastAPI (Python)

Notre application décomposera des URLs.

1.  **Créez et activez un environnement virtuel Python :**
    ```bash
    python -m venv venv
    source venv/bin/activate # Ou équivalent Windows
    ```

2.  **Installez les dépendances :**
    Le fichier `requirements.txt` inclut `fastapi` et `uvicorn`. Le module `urllib.parse` est standard.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Complétez l'application (`main.py`) :**
    Ouvrez `main.py`. Votre tâche est de :
    *   **Compléter la fonction `parse_url_components` :**
        *   Au `#TODO 1`, utilisez `urllib.parse.urlparse()` sur la chaîne `url_to_parse` pour obtenir un objet `ParseResult`.
        *   Au `#TODO 2`, extrayez les attributs `scheme`, `netloc`, `path`, `query` (la chaîne de requête brute), et `fragment` de l'objet `ParseResult`.
        *   Au `#TODO 3`, extrayez les attributs `hostname` et `port` de l'objet `ParseResult`. Ces attributs peuvent être `None`.
        *   Au `#TODO 4`, utilisez `urllib.parse.parse_qs()` sur la chaîne de requête brute (extraite au TODO 2) pour obtenir un dictionnaire de paramètres de requête.
        *   Assurez-vous que la fonction retourne un objet `URLParseResponse` correctement rempli avec toutes les valeurs extraites (ou `None` si une composante n'est pas présente).
    *   **Compléter l'endpoint `POST /parse_url` :**
        *   Appelez votre fonction `parse_url_components` avec la chaîne de l'URL provenant de `payload.url` (n'oubliez pas de convertir `payload.url` qui est un `HttpUrl` Pydantic en `str` avant de le passer à `urlparse`).
        *   Retournez le résultat.

4.  **Lancez l'application localement :**
    ```bash
    uvicorn main:app --reload
    ```
    Ouvrez `http://127.0.0.1:8000/docs`. Testez l'endpoint `/parse_url` avec différentes URLs :
    *   Une URL complexe avec tous les composants.
    *   Une URL simple sans port, ni query, ni fragment.
    *   Une URL avec seulement des query parameters.
    Vérifiez que `/health_url_parser` fonctionne.

5.  **Rédigez le `README.md` :**
    Complétez le `README.md` pour décrire l'application, son installation, et l'utilisation de son endpoint, en vous basant sur les sections `#TO BE COMPLETED BY STUDENTS`.

---

## Partie 2 : Vérification des Normes avec Flake8 (Linting)

1.  **Installez Flake8 :**
    ```bash
    pip install flake8
    ```
2.  **Lancez Flake8 :**
    À la racine de votre projet :
    ```bash
    flake8 .
    ```
3.  **Analysez et corrigez** les erreurs ou avertissements de style.

---

## Partie 3 : Implémentation des Tests avec Pytest

1.  **Installez Pytest et HTTPX :** (Si pas déjà fait)
    ```bash
    pip install pytest httpx
    ```
2.  **Complétez le fichier de tests (`tests/test_main.py`) :**
    Ouvrez `tests/test_main.py`. Des squelettes de tests sont fournis :
    *   Pour `test_parse_url_full_complex_url` :
        *   Suivez les `#TODO` pour ajouter des assertions vérifiant que chaque composant de l'URL (scheme, netloc, hostname, port, path, query_string, query_params, fragment) est correctement extrait et correspond aux valeurs attendues pour l'URL complexe donnée.
    *   Pour `test_parse_url_simple_http_url_no_port_no_query_no_fragment` :
        *   Suivez les `#TODO` pour vérifier les composants d'une URL plus simple, en vous assurant que les composants absents sont bien `None` ou vides comme attendu.
    *   Pour `test_parse_url_with_only_query_no_path_no_fragment` :
        *   Suivez les `#TODO` pour un autre cas de figure, en portant une attention particulière au `path` et aux `query_params`.
    *   Les tests de validation Pydantic (`test_parse_url_invalid_url_format_handled_by_pydantic`, `test_parse_url_missing_url_payload`) devraient déjà passer si votre modèle `URLParseRequest` est correct.

3.  **Lancez Pytest :**
    ```bash
    pytest
    ```
    Assurez-vous que tous vos tests passent.

4.  **Passez Flake8 sur vos tests :**
    ```bash
    flake8 tests/test_main.py
    ```

---

## Partie 4 : Analyse de Composition de Logiciels (SCA) avec pip-audit

1.  **Générez/Mettez à jour `requirements.txt` :**
    ```bash
    pip freeze > requirements.txt
    ```
2.  **Installez pip-audit :**
    ```bash
    pip install pip-audit
    ```
3.  **Lancez pip-audit :**
    ```bash
    pip-audit -r requirements.txt
    ```
4.  **Analysez les résultats.**

---

## Partie 5 : Analyse Statique de Sécurité (SAST) avec Bandit

1.  **Installez Bandit :**
    ```bash
    pip install bandit
    ```
2.  **Lancez Bandit :**
    ```bash
    bandit -r . -x venv
    ```
3.  **Analysez les résultats.**

---

## Partie 6 : Intégration Continue avec GitLab CI

1.  **Examinez et complétez le fichier `.gitlab-ci.yml` :**
    *   Remplacez les commentaires `# TODO` dans les sections `script:` par les commandes `flake8 .` et `pytest tests/` (ou `pytest`).

2.  **Commit et Push sur GitLab :**
    ```bash
    git add .
    git commit -m "Implemented URL parser, tests, and CI"
    git push
    ```

3.  **Vérifiez le Pipeline dans GitLab** (CI/CD > Pipelines).

---

## Partie 7 : Vérification de Secrets avec TruffleHog

1.  **Installez TruffleHog :**
    ```bash
    pip install trufflehog
    ```
2.  **(Optionnel) Introduisez un faux secret** dans `main.py`, commitez-le.
3.  **Lancez TruffleHog :**
    ```bash
    trufflehog git file://$(pwd)
    ```
4.  **Analysez les résultats et nettoyez.**

---

Félicitations ! Vous avez mis en place une API d'analyse de composants d'URL, l'avez testée, analysée avec des outils de sécurité, et configuré une CI basique.