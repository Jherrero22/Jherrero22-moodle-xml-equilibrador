# Jherrero22-moodle-xml-equilibrador
# Equilibrador de bancos Moodle XML (opciones y orden)

Herramienta para **equilibrar la longitud** de opciones en preguntas *multichoice* de Moodle XML:
- Amplía automáticamente las **opciones más cortas** (con matices reales del dominio).
- **Reordena** aleatoriamente las opciones, conservando cuál es la correcta.
- Exporta un **XML** listo para Moodle y (en Colab) un **PDF** de revisión.

## Uso rápido (local / CLI)
Requisitos:
```bash
pip install beautifulsoup4 lxml
## 🚀 Abrir directamente en Google Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<jherrero22>/<moodle-xml-equilibrador>/blob/main/notebook/Equilibrar_Moodle_XML.ipynb)
