# Upstream Canary issue remediation backlog

Cel: analizować i naprawiać w `blakinio/canary` aktualnie otwarte problemy zgłaszane w `opentibiabr/canary`, bez wysyłania zmian do repozytorium upstream.

## Zasady

- Osobna gałąź i PR dla każdej logicznej poprawki albo małej grupy ściśle powiązanych błędów.
- Kolejność: `Critical`, `High`, `Medium`, `Low`, `Enhancement`, `Missing Content`.
- Każde zgłoszenie musi zostać zweryfikowane względem aktualnego `main` w tym repozytorium.
- Duplikaty, problemy nieaktualne i błędy niemożliwe do odtworzenia nie będą naprawiane w ciemno.
- Problemy wymagające mapy, assetów albo niepublicznych danych będą oddzielone od poprawek C++ i Lua.

## Pierwsza partia

- [ ] upstream #3986 — `playerSaySpell` blokuje rzucanie czarów podczas paraliżu
  - branch: `fix/issue-3986-paralyze-spell-casting`
- [ ] upstream #3458 — Soulpit nie przechodzi dalej przy summonach
- [ ] upstream #3534 — szczeliny Beregar nie reagują na kilof
- [ ] upstream #3724 — zapis i duplikacja gemów Wheel of Destiny
- [ ] upstream #4013 — zachowanie automatycznego server save

## Status

Ten plik jest nadrzędnym trackerem, ponieważ GitHub Issues są wyłączone w `blakinio/canary`.
