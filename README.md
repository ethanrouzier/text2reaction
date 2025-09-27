# 🧪 Text→Reaction (Mistral)

Extraction intelligente de procédures expérimentales depuis des articles scientifiques (PDF/HTML/TXT) vers un format JSON structuré, via l'API **Mistral AI**. Interface web moderne avec visualisation des résultats.

## ✨ Fonctionnalités

- 🔍 **Extraction automatique** des sections expérimentales
- 🎨 **Interface visuelle moderne** pour afficher les réactions
- 📥 **Export JSON** des données extraites
- 🧪 **Support multi-format** : PDF, HTML, TXT
- 🌐 **Upload par URL** ou fichier local
- ⚡ **Validation Pydantic** pour des données cohérentes

## 🚀 Installation rapide

```bash
# Cloner le projet
git clone <your-repo-url>
cd text2reaction

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp env.example .env
# Éditer .env et ajouter votre MISTRAL_API_KEY
export $(grep -v '^#' .env | xargs)
```

## 🎯 Utilisation

### Interface web
```bash
# Lancer l'application
make run
# ou
python -m flask --app app.main run --debug

# Ouvrir http://127.0.0.1:5000
```

### Test rapide
Uploader le fichier d'exemple : `tests/samples/sample_procedure.txt`

## 📊 Données extraites

Chaque réaction extraite contient :
- **Réactifs et réagents** avec quantités et équivalents
- **Conditions réactionnelles** (température, temps, atmosphère)
- **Travail en amont** (étapes de purification)
- **Résultats** (rendement, nom du produit)
- **Notes** additionnelles

## 🏗️ Architecture

```
app/
├── main.py          # Interface Flask et routes
├── models.py        # Modèles Pydantic pour validation
├── extractor.py     # Client Mistral AI
├── prompts.py       # Prompts optimisés pour l'extraction
├── readers.py       # Lecture PDF/HTML/TXT
└── section_finder.py # Détection des sections expérimentales
```

## 🧪 Test

```bash
# Tests unitaires
make test
# ou
pytest -q

# Test d'intégration
curl -X POST -F "file=@tests/samples/sample_procedure.txt" -F "max_sections=1" http://127.0.0.1:5000/extract
```

## 🔧 Configuration

Variables d'environnement dans `.env` :
- `MISTRAL_API_KEY` : Clé API Mistral (requis)
- `SECRET_KEY` : Clé secrète Flask (optionnel)
- `PORT` : Port de l'application (défaut: 5000)
- `MISTRAL_MODEL` : Modèle Mistral (défaut: mistral-large-latest)

## 🚀 Déploiement

### Heroku
```bash
# Ajouter un Procfile
echo "web: python -m flask --app app.main run --host=0.0.0.0 --port=\$PORT" > Procfile

# Déployer
git push heroku main
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "-m", "flask", "--app", "app.main", "run", "--host=0.0.0.0", "--port=5000"]
```

## 🔮 Évolutions futures

- 🗺️ **Mapping direct vers ORD** protobufs
- 🔍 **Détection améliorée** des sections (layout, police)
- ⚖️ **Normalisation d'unités** et calcul d'équivalents
- 🧠 **LLM Judge** pour validation/correction
- 📊 **Dashboard** d'analyse des données
- 🔗 **API REST** pour intégration

## 📝 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request
