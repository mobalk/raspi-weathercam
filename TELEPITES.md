# Részletes telepítési útmutató

## Kellékek
### Hardware

* Raspberry Pi mini számítógép
  * Tesztelve [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)
    és [Raspberry Pi 3A](https://www.raspberrypi.com/products/raspberry-pi-3-model-a-plus/) modellekkel.
    Minden valószínűség szerint az újabb modellekkel is együtt tud működni, de ha csak erre használod,
    bőven elég a régebbi -- olcsóbb -- modell.
* Camera HQ

- [ ] **TODO** képek

### Software
- [ ] **TODO**

## Raspberry Pi üzembe helyezése
### Raspberry Pi OS telepítése
https://www.raspberrypi.com/software/

* Raspberry Pi Imager telepítése számítógépre
* Raspberry Pi OS (32bit) kiválasztása
* Mentése helye: SD kártya
* "Write"
* Távolítsuk el az SD kártyát biztonságos módon (Lehetséges, hogy a Windows a megírt kártyát mint ismeretlen esztköz azonosítja)

### A Raspberry Pi összeszerelése
1. Helyezzük az SD káryát a Raspberry Pi 3 kártya foglalatába
2. Csatlakoztassuk az USB dongle-t
3. Csatlakoztassuk a monitor HDMI csatlakozóját
4. Dugjuk rá a tápot.

--> piros led felvillan, és a monitoron megjelenik a RaspberryPi OS betöltő-képernyője

### Az OS beállítása
* ország, nyelv, időzóna megadása az első elindulás után
* változtassuk meg az alapértelmezett jelszót
* csatlakozzunk a WiFi hálózatra
** az OS frissítéseket fog keresni

Start menü (bal felső sarokban a málna ikon) --> Beállítások --> "Raspberry Pi Configuration"
* "Interfaces" fül: 
	* Camera: Enable
	* SSH: Enable
	* VNC: Enable
* "Performance" fül:
	* GPU Memory: 256 Mb
* "OK" --> indítsuk újra az eszközt

### Az eszköz távoli elérése
* VNC segítségével
	* Lásd még hivatalos leírás:
	https://www.raspberrypi.com/documentation/computers/remote-access.html#virtual-network-computing-vnc
	* Telepítsük a VNC klienset a számítógépre:
	https://www.realvnc.com/en/connect/download/viewer/
	* Ha a beállításokban engedélyeztük, akkor újraindítás után elindul a RPi-n a VNC szerver.
	A jobb felső sarokban lévő VNC ikonra kattintva láthatjuk az IP címet amire a számítógépünkkel csatlakozhatunk.
	
	

### Kamera összeszerelése
Lásd még a hivatalos leírást:
https://projects.raspberrypi.org/en/projects/getting-started-with-picamera

HQ Camera-t  csavarjuk az állványra, a védő kupakot távolítsuk el.
A vásárolt lencsénktől függően lehet, hogy a védőkupak mögötti közgyűrűt is ki kell csavarnunk.
Lencse hátsó kupakját szintén távolítsuk el és csavarjuk be a lencsét a menetbe.

Állítsuk le a RPi-t és áramtalanítsuk.
Az alaplapon keressük meg a "CAMERA" feliratú kábelbemenetet.
A fekete reteszt a tetején körömmel vagy lapos csavarhúzóval emeljük ki.
Illesszük be a szalagkábelt úgy, hogy a fényes erezete a csatlakozók felé nézzen (a kékre festett felület a fekete retesz felé).
Toljuk vissza a reteszt.
Indítsuk újra a RPi-t

LXTerminal ablakba írjuk be:
raspistill -o Desktop/foto.jpg

Ha minden jól megy, egy pár másodperc után elkészül az első -- homályos -- fotónk.

Indítsuk el ismét a fotó alkalmazást, de most nem készítünk képet, csak az élő képet szeretnék tartósan megjeleníteni (1 percig)

raspistill -t 60000
Ha egy perc sem elég, indítsuk el az élőképet időkorlát nélkül:
raspistill -t 0
Ilyenkor Ctrl + C megnyomásával lehet a programból kilépni.

Ha továbbra sem sikerül az élességállítás, mert a lencsétől néhány mm-re rajzol csak éles képet, akkor valószínűleg bennmaradt a közgyűrű. Vegyük ki.

## Időjárás figyelő telepítése
- [ ] **TODO**
