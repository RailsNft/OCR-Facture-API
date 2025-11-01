# Tests - OCR Facture API

## 🧪 Exécution des tests

### Installation des dépendances de test

```bash
pip install pytest pytest-asyncio httpx
```

### Exécuter tous les tests

```bash
pytest
```

### Exécuter un fichier de test spécifique

```bash
pytest tests/test_ocr_extraction.py
```

### Exécuter avec verbose

```bash
pytest -v
```

### Exécuter avec couverture de code

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## 📋 Structure des tests

### Tests unitaires

- `test_ocr_extraction.py` - Tests d'extraction de données OCR
- `test_rate_limiting.py` - Tests de rate limiting
- `test_cache.py` - Tests du système de cache

### Tests d'intégration

- `test_api_endpoints.py` - Tests des endpoints API

## 🔧 Configuration

Le fichier `pytest.ini` configure pytest :
- Chemins de test : `tests/`
- Format de sortie : verbose
- Marqueurs : unit, integration, slow

## 📝 Ajouter de nouveaux tests

1. Créer un fichier `test_*.py` dans `tests/`
2. Créer des classes `Test*` ou fonctions `test_*`
3. Utiliser les fixtures de `conftest.py` si nécessaire

Exemple :

```python
def test_my_feature():
    """Test d'une fonctionnalité"""
    result = my_function()
    assert result == expected_value
```

## 🚀 CI/CD

Les tests peuvent être intégrés dans GitHub Actions :

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

