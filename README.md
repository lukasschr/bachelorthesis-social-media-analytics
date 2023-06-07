# **Bachelorthesis - Social Media Analytics**

Dieses Projekt ist Teil meiner Bachelorthesis "Soziale Medien zur Identifizierung und Verlaufsprognostizierung von Markttrends: Eine Evaluation der Potentiale" am [Lehrstuhl für Wirtschaftsinformatik, insb. Social Computing](https://wiwi.uni-paderborn.de/dep3/trier).

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
docker run [-d] -p 8888:8888 bt_project
```
Wenn der optionale Parameter "-d" angegeben wird, wird der Docker-Container im Hintergrund gestartet und der Befehl kehrt sofort zur Eingabeaufforderung zurück, ohne dass die Container-Ausgabe angezeigt wird.

*Open Jupyter Notebook*<br>
<pre><a href="http://localhost:8888/">http://localhost:8888/</a></pre>

*Enter following token*
```
btsmalukasschroeder
```


### Hinweise
Das Projekt verfügt über einen `src/` Ordner, welcher Skripte enthält die notwendige Klassen und Funktionen für die Notebooks bereitstellen. Zumeist werden diese direkt über die Notebooks importiert und verwendet. In Spezialfällen kann es notwendig sein, dass ein Skript manuell über ein Terminal gestartet werden muss oder auf einem Server ohne Desktop-Umgebung laufen muss.

#### Skripte über ein Terminal ausführen
Um Skripte über ein Terminal ausführen zu können, kann einfach ein Terminal innerhalb von Jupyter Notebook gestartet werden. 
> Files > New > Terminal

#### Headless Anwendungen
Headless Anwendungen sind Skripte, die auf einem Gerät ohne grafische Benutzeroberfläche ausgeführt werden können, bspw. einem Linux-Server. Da auf einem Gerät ohne Benutzeroberfläche Jupyter Notebook Terminals nicht gestartet werden können (um Skripte über Jupyter Notebook Terminals auszuführen), benötigt es folgende Lösung:<br>
*Open Container Terminal*
```bash
docker exec -it CONTAINER_ID bash
```
Dies ermöglicht die Ausführung einer interaktiven Bash-Shell innerhalb des Docker-Containers. Über die Bash können nun Headless Scripte ausgeführt werden.



## **FAQ**

#### **"Wie finde ich die CONTAINER_ID?"**
Mit dem Befehl ```docker run [-d] -p 8888:8888 bt_project```, wird ein sogenannter Docker Container mit einer `CONTAINER_ID` erstellt. Diese lässt sich mit dem folgenden Befehl ermitteln:
```bash
docker ps -a
```

#### **"Wie beende ich den Container / Jupyter Notebook ordnungsgemäß?"**
Es gibt zwei Möglichkeiten den Container zu beenden:
1. Beenden über Button "Quit" in Jupyter
2. <pre>docker stop CONTAINER_ID</pre>

#### **"Der Container wurde beendet. Kann ich diesen erneut starten?"**
Ja! Zunächst muss die `CONTAINER_ID` ermittelt werden. Anschließend kann der Container erneut gestartet werden:
```bash
docker start CONTAINER_ID
```



## **Contact**

Lukas Schröder - schlukas@mail.uni-paderborn.de

