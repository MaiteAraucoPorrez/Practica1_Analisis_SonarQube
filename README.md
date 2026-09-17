# Práctica 1: Análisis Estático con SonarQube

**Materia:** Gestión de Calidad de Sistemas (SIS-312)
**Equipo:** Gabriela Maite Arauco Porrez y Alexander Xavier Rojas Arce

## AUT (Application Under Test)
PideloYa: aplicación web de delivery construida con Flask y MongoDB.

## Tech Stack
- Backend: Python/Flask
- Base de datos: MongoDB
- Frontend: HTML5, CSS3 (plantilla Nicepage)

## Herramientas de análisis
- SonarQube Community Build (local, localhost:9000)
- SonarScanner CLI
- SonarQube for IDE (SonarLint) en VSCode - herramienta adicional

## Cómo ejecutar el análisis
1. Levantar SonarQube local en `http://localhost:9000`
2. Desde la raíz del proyecto: sonar-scanner -D"sonar.token=TU_TOKEN"
La configuración está en `sonar-project.properties`.

## Enlaces
- Repositorio: https://github.com/MaiteAraucoPorrez/Practica1_Analisis_SonarQube
- Tablero Trello: https://trello.com/b/NT6cPLj2/analisisestaticosonarqube
