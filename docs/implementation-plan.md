# Implementation plan — recruiter demonstration

Scope: public, account-free synthetic health-insurance decision-support portfolio. No authentication, roles or user accounts are planned.

Source baseline: 406d0b9c629eaf60c2ba34d8cd544004652bbd22. Implementation branch: feat/recruiter-science-platform. Existing reference artifacts and published metrics remain independently identifiable.

Current checkpoint: core input/history corrections implemented; 260 existing/new tests passed before the additional research tests. The small end-to-end research fixture now passes. Full corpus runs, analytical UI, browser verification and deployment are still in progress.

| ID | Improvement | Status |
|---|---|---|
| 01 | Cohérence du compteur de services | Implemented; final regression pass pending |
| 02 | Contexte temporel des polices | Implemented; final regression pass pending |
| 03 | Erreurs de validation API | Implemented; final regression pass pending |
| 04 | Imports CSV/JSON non ambigus | Implemented; final regression pass pending |
| 05 | Contrat métier typé | Implemented; final regression pass pending |
| 06 | Limites de fichiers et de lots | Implemented; final regression pass pending |
| 07 | Features offline/online partagées | Implemented; final regression pass pending |
| 08 | Régressions et qualité des données | Implemented; final regression pass pending |
| 09 | Diversité des profils synthétiques | Research code implemented; full experiment pending |
| 10 | Historique longitudinal des entités | Research code implemented; full experiment pending |
| 11 | Fraudes et anomalies légitimes | Research code implemented; full experiment pending |
| 12 | Courbes d’apprentissage et volumes | Research code implemented; full experiment pending |
| 13 | Scénarios et graines indépendants | Research code implemented; full experiment pending |
| 14 | Corruption contrôlée séparée | Research code implemented; full experiment pending |
| 15 | Comparaison du preprocessing | Research code implemented; full experiment pending |
| 16 | Features candidates et ablations | Research code implemented; full experiment pending |
| 17 | Pipeline entraînement/évaluation | Research code implemented; full experiment pending |
| 18 | Séparation temporelle et anti-fuite | Research code implemented; full experiment pending |
| 19 | Provenance et artefacts | Research code implemented; full experiment pending |
| 20 | Politique de risque centrale | In progress |
| 21 | Suivi de dérive simulée | Planned |
| 22 | Validation externe facultative | Optional; compatible external labelled data required, no real-data performance claim |
| 23 | Dashboard exploration | Planned |
| 24 | Dashboard qualité | Planned |
| 25 | Dashboard temporel | Planned |
| 26 | Dashboard fraude | Planned |
| 27 | Dashboard modèles | Planned |
| 28 | Dashboard capacité métier | Planned |
| 29 | Dashboard explicabilité/erreurs | Planned |
| 30 | Dashboard robustesse | Planned |
| 31 | Filtres et interprétations | Planned |
| 32 | Navigation progressive | Planned |
| 33 | Responsive/accessibilité | Planned |
| 34 | Erreurs publiques et diagnostics | In progress |
| 35 | Exports sûrs | In progress |
| 36 | Sauvegarde/reprise locale des investigations | Planned |
| 37 | Mode démo et conservation | Planned |
| 38 | Parcours navigateur et conteneurs | Planned |
| 39 | Couverture des tests | Planned |
| 40 | Résilience réseau | Planned |
| 41 | Dépendances verrouillées | Planned |
| 42 | Mesures de performance | Planned |
| 43 | Caches et client HTTP | In progress |
| 44 | Factorisation des responsabilités | In progress |
| 45 | Conteneurs reproductibles | Planned |
| 46 | Configuration et déploiement Render | Planned |
| 47 | Contrôles CI | Planned |
| 48 | Hygiène Git et documentation | In progress |

## Verification commands

Run `PYTHONPATH=.:src python -m pytest tests -q`, then separately `PYTHONPATH=.:src python -m pytest api/tests -q`. Research scripts have explicit output directories and do not replace the published model. Final results and limitations will be recorded here.
