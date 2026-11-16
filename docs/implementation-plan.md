# Implementation plan — recruiter demonstration

Scope: public, account-free synthetic health-insurance decision-support portfolio. No authentication, roles or user accounts are planned.

Source baseline: 406d0b9c629eaf60c2ba34d8cd544004652bbd22. Implementation branch: feat/recruiter-science-platform. Existing reference artifacts and published metrics remain independently identifiable.

Current checkpoint: core corrections and two full research experiments are implemented. Eight analytical workspaces, independent-world sensitivity tests and local decision snapshots are available. Last completed suite: 306 project tests plus 7 API tests; declared broad-module coverage 77.46%. Final browser/container verification and deployment are pending.

| ID | Improvement | Status |
|---|---|---|
| 01 | Cohérence du compteur de services | Implemented and locally verified |
| 02 | Contexte temporel des polices | Implemented and locally verified |
| 03 | Erreurs de validation API | Implemented and locally verified |
| 04 | Imports CSV/JSON non ambigus | Implemented and locally verified |
| 05 | Contrat métier typé | Implemented and locally verified |
| 06 | Limites de fichiers et de lots | Implemented and locally verified |
| 07 | Features offline/online partagées | Implemented and locally verified |
| 08 | Régressions et qualité des données | Implemented and locally verified |
| 09 | Diversité des profils synthétiques | Implemented and locally verified |
| 10 | Historique longitudinal des entités | Implemented and locally verified |
| 11 | Fraudes et anomalies légitimes | Implemented and locally verified |
| 12 | Courbes d’apprentissage et volumes | Implemented and locally verified |
| 13 | Scénarios et graines indépendants | Implemented and locally verified |
| 14 | Corruption contrôlée séparée | Implemented and locally verified |
| 15 | Comparaison du preprocessing | Implemented and locally verified |
| 16 | Features candidates et ablations | Implemented and locally verified |
| 17 | Pipeline entraînement/évaluation | Implemented and locally verified |
| 18 | Séparation temporelle et anti-fuite | Implemented and locally verified |
| 19 | Provenance et artefacts | Implemented and locally verified |
| 20 | Politique de risque centrale | Implemented and locally verified |
| 21 | Suivi de dérive simulée | Implemented and locally verified |
| 22 | Validation externe facultative | Optional; compatible external labelled data required; no real-data performance claim |
| 23 | Dashboard exploration | Implemented and locally verified |
| 24 | Dashboard qualité | Implemented and locally verified |
| 25 | Dashboard temporel | Implemented and locally verified |
| 26 | Dashboard fraude | Implemented and locally verified |
| 27 | Dashboard modèles | Implemented and locally verified |
| 28 | Dashboard capacité métier | Implemented and locally verified |
| 29 | Dashboard explicabilité/erreurs | Implemented and locally verified |
| 30 | Dashboard robustesse | Implemented and locally verified |
| 31 | Filtres et interprétations | Implemented and locally verified |
| 32 | Navigation progressive | Implemented and locally verified |
| 33 | Responsive/accessibilité | Contrast improved; real desktop/mobile browser checks pending |
| 34 | Erreurs publiques et diagnostics | Implemented and locally verified |
| 35 | Exports sûrs | Implemented and locally verified |
| 36 | Sauvegarde/reprise locale des investigations | Implemented; unit tests passed, browser round-trip pending |
| 37 | Mode démo et conservation | Public synthetic demo; session-local uploads/notes documented |
| 38 | Parcours navigateur et conteneurs | Browser/container workflow prepared; execution pending |
| 39 | Couverture des tests | 77.46% across declared broad modules; 75% gate passed locally |
| 40 | Résilience réseau | Implemented and locally verified |
| 41 | Dépendances verrouillées | Implemented and locally verified |
| 42 | Mesures de performance | Implemented and locally verified |
| 43 | Caches et client HTTP | Implemented and locally verified |
| 44 | Factorisation des responsabilités | Implemented and locally verified |
| 45 | Conteneurs reproductibles | Pinned base/hashed roles/non-root/signal handling implemented; container build pending |
| 46 | Configuration et déploiement Render | Existing free services identified; Blueprint schema validated; deployment pending |
| 47 | Contrôles CI | CI strengthened; remote run pending |
| 48 | Hygiène Git et documentation | Caches/placeholders removed; README, protocol and API docs updated |

## Verification commands

Run `PYTHONPATH=.:src python -m pytest tests -q`, then separately `PYTHONPATH=.:src python -m pytest api/tests -q`. Research scripts have explicit output directories and do not replace the published model. Final results and limitations will be recorded here.
