# domainscraper

Générateur de noms de domaine + vérificateur de disponibilité, en Go.

Combine des milliers de mots-clés anglais (musique, rock, cuisine, food,
travel, agency, tech, sport, fashion, finance, health, home, pet, kids, art,
game, nature, legal, education, realestate, beauty, automotive...) avec des
préfixes/suffixes génériques (`my`, `get`, `pro`, `hub`, `zone`, `hq`, ...) et
une liste de TLD, puis vérifie en parallèle via RDAP (protocole moderne qui
remplace WHOIS, sans clé API) quels domaines sont libres.

## Build

```bash
go build -o domainscraper ./cmd/domainscraper
```

## Utilisation

```bash
# lister les catégories disponibles
./domainscraper -list

# voir combien de candidats seraient générés, sans rien vérifier
./domainscraper -dry-run -categories music,rock,cook -tlds com,io,co

# lancer un scan réel
./domainscraper \
  -categories music,rock,cook,food,travel,agency \
  -tlds com,net,io,co \
  -workers 60 \
  -limit 5000 \
  -only-available \
  -out available.csv
```

## Flags principaux

| Flag              | Description                                              |
|--------------------|-----------------------------------------------------------|
| `-categories`      | catégories à inclure (vide = toutes)                      |
| `-tlds`             | TLD à tester, séparés par des virgules                    |
| `-prefix/-suffix/-plain/-double` | quels styles de combinaison générer          |
| `-workers`          | nombre de vérifications RDAP en parallèle                 |
| `-limit`            | nombre max de domaines testés                              |
| `-shuffle`          | mélange les candidats avant de tester                     |
| `-only-available`   | n'affiche que les domaines libres                          |
| `-out`              | fichier CSV de résultats (écrit en continu)                |
| `-dry-run`          | affiche juste le nombre de candidats générés               |

Le CSV de sortie contient `domain,status` avec `status` parmi `AVAILABLE`,
`registered`, `unknown`, `error`. Résultat colorisé en vert dans le terminal
pour les domaines disponibles.

## Ajouter des mots-clés

Toutes les catégories sont dans `internal/keywords/keywords.go`. Ajouter un
mot dans une catégorie existante, ou une nouvelle `Category{}`, suffit — le
générateur les prend automatiquement en compte.
