Login met de postgres user:
```
sudo su postgres
```
Open een psql environment:
```
psql
```
Selecteer de database van je app (dbtutor in dit geval, ```\l``` voor alle databases):
```
\c dbtutor
```
Laat alle relations zien:
```
\dt
```
Bekijk de inhoud van quotes:
```
Select * From quotes;
```
Verwijder de quotes met een id > 6:
```
Delete From quote where id > 6;
```
