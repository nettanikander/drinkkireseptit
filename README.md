# Drinkkireseptit

* Sovelluksessa käyttäjät pystyvät jakamaan drinkkireseptejään. Reseptissä lukee tarvittavat ainekset ja teko-ohje.
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään reseptejä ja muokkaamaan ja poistamaan niitä.
* Käyttäjä näkee sovellukseen lisätyt reseptit.
* Käyttäjä pystyy etsimään reseptejä hakusanalla.
* Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
* Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkoholiton, alkoholillinen, shotit, boolit, cocktailit).
* Käyttäjä pystyy kommentoimaan reseptejä sekä antamaan arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.
* Käyttäjä pystyy lisäämään reseptiin kuvia ja poistamaan ne.

## Sovelluksen asennus

Asenna 'flask' -kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
