# **Bachelorthesis - Social Media Analytics**

Dieses Projekt ist Teil der Bachelorthesis "Soziale Medien zur Identifizierung und Verlaufsprognostizierung von Markttrends: Eine Evaluation der Potentiale" am [Lehrstuhl für Wirtschaftsinformatik, insb. Social Computing](https://wiwi.uni-paderborn.de/dep3/trier).

---



## **Getting Started**


### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- Docker-Image (Kontaktieren Sie mich für einen Zugang zum Image)


### Installation & Run
*Load Docker Image*
```bash
docker load -i image.tar
```

*Run Docker Image*
```bash
docker run [-d] -p 8888:8888 btsma_project_lukas
```

*Open Jupyter Notebook*<br>
<pre><a href="http://localhost:8888/">http://localhost:8888/</a></pre>

*Enter following token*
```
btsmalukasschroeder
```

## **Wichtige Hinweise**
Das Projekt umfasst einen Verzeichnisbaum `src/`,  der Skripte enthält, welche die erforderlichen Klassen und Funktionen für die Notebooks bereitstellen. In der Regel werden diese Skripte direkt in den Notebooks importiert und verwendet. In bestimmten Fällen kann es jedoch erforderlich sein, ein Skript manuell über ein Terminal zu starten oder auf einem serverbasierten System ohne Desktop-Umgebung auszuführen.

### Skripte über ein Terminal ausführen
Um Skripte über ein Terminal ausführen zu können, kann einfach ein Terminal innerhalb von Jupyter Notebook gestartet werden. 
> File > New > Terminal

### Skripte über ein Terminal ausführen (HEADLESS)
Wenn Skripte auf einem Gerät ohne grafische Benutzeroberfläche, wie beispielsweise einem Linux-Server, ausgeführt werden sollen, besteht das Problem, dass Jupyter Notebook-Terminals nicht gestartet werden können. Um Skripte dennoch auf solchen Geräten auszuführen, wird folgende Lösung empfohlen:<br>
*Open Container Terminal*
```bash
docker exec -it CONTAINER_ID bash
```
Dies ermöglicht die Ausführung einer interaktiven Bash-Shell innerhalb des Docker-Containers. Über die Bash können nun Headless Skripte ausgeführt werden.



## **FAQ**

#### **"Wie finde ich die CONTAINER_ID?"**
Mit dem Befehl ```docker run [-d] -p 8888:8888 btsma_project_lukas```, wird ein sogenannter Docker Container mit einer `CONTAINER_ID` erstellt. Diese lässt sich mit dem folgenden Befehl ermitteln:
```bash
docker ps -a
```

#### **"Wie beende ich den Container / Jupyter Notebook ordnungsgemäß?"**
Es gibt zwei Möglichkeiten den Container zu beenden:
1. > File > Shut Down
2. <pre>docker stop CONTAINER_ID</pre>

#### **"Der Container wurde beendet. Kann ich diesen erneut starten?"**
Ja! Zunächst muss die `CONTAINER_ID` ermittelt werden. Anschließend kann der Container erneut gestartet werden:
```bash
docker start CONTAINER_ID
```

---

## **Contact**

Lukas Schröder - schlukas@mail.uni-paderborn.de

