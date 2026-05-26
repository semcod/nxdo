# TODO

## Priorytet wysoki
- [ ] Refaktoryzacja funkcji o wysokim CC (Cyclomatic Complexity):
  - [ ] _build_tree (CC=11) - critical
  - [ ] read_git_context (CC=9)
  - [ ] analyze_project (CC=9)
  - [ ] _parse_commits (CC=8)
  - [ ] _parse_response (CC=7)
- [ ] Poprawić pokrycie testów dla __main__.py (obecnie 0%)
- [ ] Implementować TestQL scenarios zdefiniowane w testql-scenarios/

## Priorytet średni
- [ ] Skonfigurować goal.yaml dla automatycznego release management
- [ ] Dodać GitHub Actions CI workflow (został usunięty)
- [ ] Zaimplementować testy integracyjne dla CLI komend
- [ ] Poprawić pokrycie CLI z 89% do 95%+

## Priorytet niski
- [ ] Refaktoryzacja hotspots:
  - [ ] _parse_response (fan=19)
  - [ ] cmd_plan (fan=12)
  - [ ] _build_tree (fan=11)
  - [ ] cmd_print_context (fan=10)
- [ ] Dodać wsparcie dla więcej typów projektów (Go, Java, etc.)
- [ ] Poprawić dokumentację API dla provider abstraction
