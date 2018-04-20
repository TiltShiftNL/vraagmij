# Jeugdzorg

Jeugdzorg is een project van de Gemeente Amsterdam. Meer informatie over dit project is te vinden op de website van het Datalab van de Gemeente Amsterdam

Meer informatie datapunt.ois@amsterdam.nl

## Waarom is deze code gedeeld

Het FIXXX-team van de Gemeente Amsterdam ontwikkelt software voor de gemeente. Veel van deze software wordt vervolgens als open source gepubliceerd zodat andere gemeentes, organisaties en burgers de software als basis en inspiratie kunnen gebruiken om zelf vergelijkbare software te ontwikkelen. De Gemeente Amsterdam vindt het belangrijk dat software die met publiek geld wordt ontwikkeld ook publiek beschikbaar is.

## Onderhoud en security

Deze repository bevat een "as-is" kopie van het project op moment van publiceren.

## Wat mag ik met deze code

De Gemeente Amsterdam heeft deze code gepubliceerd onder de Mozilla Public License v2.
Een kopie van de volledige licentie tekst is opgenomen in het bestand LICENSE.

Het FIXXX-team heeft de verdere doorontwikkeling van deze software overgedragen
aan de probleemeigenaar. De code in deze repository zal dan ook niet actief worden
bijgehouden door het FIXXX-team.

## Installeren (development)
```
__Installatie Docker__
https://www.docker.com

__Start project__
git clone git@github.com:amsterdam/jeugdzorg.git
cd jeugdzorg
docker-compose up
navigeer naar http://localhost:8000/

__Applicatie beheer__
http://localhost:8000/admin/
gebruikersnaam: dj_username / wachtwoord: dj_password

__Postgres beheer__
navigeer naar http://localhost:5050/
gebruikersnaam: postgres / wachtwoord: postgres
```
