# Hylkyilmoitus backend

[![GitHub Actions](https://github.com/Sukellusilmoitus/backend/workflows/CI/badge.svg)](https://github.com/Sukellusilmoitus/backend/actions)
[![codecov](https://codecov.io/gh/Sukellusilmoitus/backend/branch/master/graph/badge.svg)](https://app.codecov.io/gh/Sukellusilmoitus/backend)

## Heroku

Serveri on hostattuna [Herokussa](https://sukellusilmoitus-staging-back.herokuapp.com/).

## Asennus

Varmista, että laitteellasi on Python 3.8 tai uudempi. Luo virtuaaliympäristö ja asenna riippuvuudet

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ./requirements.txt
```

Tämän jälkeen voit käynnistää palvelimen

```bash
python3 src/index.py
```

Jos `curl http://localhost:5000/api/healthcheck` ei tuota virhettä, palvelin toimii.

## Komentoja

### Testaus

```bash
pytest
```

### Pylint

```bash
pylint src
```

### Koodin formatointi

```bash
autopep8 --in-place --aggressive --aggressive --recursive src
```

## Definition of done

Scrumin mukaisesti projektissa toteutetaan backlogista löytyvät user storyt,
joille on jokaiselle määritelty hyväksymiskriteerit.
Projektin product- ja sprint-backlogit ja siten myös hyväksymiskriteerit löytyvät tästä sheetistä: [backlogit](https://helsinkifi-my.sharepoint.com/:x:/g/personal/amikko_ad_helsinki_fi/EaUHpV9XQy1BmeSrSOFVoi8BKp4hDY_YXGRn8sG6nbl1oA?rtime=T01JVzDb2Ug)

Hyväksymiskriteerit testataan käyttäen Cypressia.
Koodia testataan kattavasti myös unit testeillä.
Koodityyli noudattaa lintin avulla määriteltyjä sääntöjä.

Asiakas voi seurata koodin ja testien tilannetta CI-palvelusta:

- Frontend: [codecov](https://app.codecov.io/gh/Sukellusilmoitus/frontend)
- Backend: [codecov](https://app.codecov.io/gh/Sukellusilmoitus/backend)

Koodin arkkitehtuuri on suunniteltua ja perusteltua,
pyrkimyksenä on mahdollisimman hyvä ylläpidettävyys pitämällä koodi selkeänä.

### Tarkistuslista User Storylle

- Tuotettu koodia suunnitelluille toiminnallisuuksille
- User storyn vaatimuksiin vastattu
- Projekti käynnistyy ilman virheitä
- Unit testit kirjoitettu ja läpäisty
- Toiminnallisuus on testattu hyväksymistesteillä
- Refraktorointi on valmis
- Product ownerin mielestä toiminnallisuus on valmis

### Tarkistuslista Sprintille

- Definition of done sprintin user storyille täytetty
- Kaikki unit testit läpäisty
- Linttaus läpäisty
- Backlog on päivitetty
- Kaikki bugit on korjattu
- Sprintin toteutettu toiminallisuus käyty läpi Product Ownerin kanssa
- Sprinttiin liittyvät "to do" asiat valmiita

### Tarkistuslista viimeiselle Releaselle

- Koodi on valmista
- Kaikki testit läpäisevät
- Kaikki hyväksymiskriteerit täyttyvät
- Ryhmä on hyväksynyt releasen
- Ei keskeneräistä työtä releasen mukana
- Kaikki DoD asetetut vaatimukset täyttyvät

## Ohjelman viimeisin versio

...
tähän mennessä valmiit ominaisuudet on listattu projektin backlogeissa.

## Ohjelman käyttöohje

......

### Asennus ja käynnistys

.....

### Käyttöliittymä

......
