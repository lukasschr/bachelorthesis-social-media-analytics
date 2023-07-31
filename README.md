# **Bachelorthesis - Social Media Analytics**

Dieses Projekt ist Teil der Bachelorthesis "Soziale Medien zur Identifizierung und Verlaufsprognostizierung von Markttrends: Eine Evaluation der Potentiale" am [Lehrstuhl für Wirtschaftsinformatik, insb. Social Computing](https://wiwi.uni-paderborn.de/dep3/trier) der Universität Paderborn.



## **Leitfaden für den Einstieg**


### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Docker-Image (siehe: Digitaler Anhang)


### Installation und Ausführung
Nach der Installation von Docker wird Docker-Desktop im Hintergrund gestartet. Anschließend werden die folgenden Befehle nacheinander in einer Eingabeaufforderung oder Shell ausgeführt.

*1. Docker-Image laden*
```bash
docker load -i pfad/zum/image.tar
```

*2. Docker-Image ausführen*
```bash
docker run -d -p 8888:8888 btsma_project_lukas
```

*3. Jupyter Notebook öffnen*<br>
Den folgenden Link in einem Browser öffnen, um Jupyter Notebook zu öffnen:
<pre><a href="http://localhost:8888/">http://localhost:8888/</a></pre>

*4. Token eingeben*<br>
Nach dem Öffnen von Jupyter Notebook wird ein Token verlangt. Der folgende Token muss in das erste Eingabefeld eingetragen und bestätigt werden:
```
btsmalukasschroeder
```

## **Hinweise**
Das Projekt umfasst einen Verzeichnisbaum `src/`,  der Skripte enthält, welche die erforderlichen Klassen und Funktionen für die Notebooks bereitstellen. In der Regel werden diese Skripte direkt in den Notebooks importiert und verwendet. In bestimmten Fällen kann es jedoch erforderlich sein, ein Skript manuell über ein Terminal zu starten oder auf einem serverbasierten System ohne Desktop-Umgebung auszuführen.

### Skripte über ein Terminal ausführen
Um Skripte über ein Terminal ausführen zu können, kann einfach ein Terminal innerhalb von Jupyter Notebook gestartet werden. 
> File > New > Terminal

### Skripte über ein Terminal ausführen (HEADLESS)
Wenn Skripte auf einem Gerät ohne grafische Benutzeroberfläche, wie beispielsweise einem Linux-Server, ausgeführt werden sollen, besteht das Problem, dass Jupyter Notebook-Terminals nicht gestartet werden können. Um Skripte dennoch auf solchen Geräten auszuführen, wird folgende Lösung empfohlen:<br>
*Öffne Container Terminal*
```bash
docker exec -it CONTAINER_ID bash
```
Dies ermöglicht die Ausführung einer interaktiven Bash-Shell innerhalb des Docker-Containers. Über die Bash können nun Headless Skripte ausgeführt werden.



## **FAQ**

#### **"Wie finde ich die CONTAINER_ID?"**
Mit dem Befehl ```docker run -d -p 8888:8888 btsma_project_lukas```, wird ein sogenannter Docker Container mit einer `CONTAINER_ID` erstellt. Diese lässt sich mit dem folgenden Befehl in einer Eingabeaufforderung oder Shell ermitteln:
```bash
docker ps -a
```

#### **"Wie beende ich den Container / Jupyter Notebook ordnungsgemäß?"**
Es gibt zwei Möglichkeiten den Container zu beenden:
1. > File > Shut Down
2.  <pre>docker stop CONTAINER_ID</pre>

#### **"Der Container wurde beendet. Kann ich diesen erneut starten?"**
Ja! Zunächst muss die `CONTAINER_ID` ermittelt werden. Anschließend kann der Container erneut gestartet werden:
```bash
docker start CONTAINER_ID
```



## **Contact**

Lukas Schröder - schlukas@mail.uni-paderborn.de