# Implementation plan — recruiter demonstration

Scope: public, account-free synthetic health-insurance decision-support portfolio. No authentication, roles or user accounts are planned.

Source baseline: 406d0b9c629eaf60c2ba34d8cd544004652bbd22. Implementation branch: feat/recruiter-science-platform. Existing reference artifacts and published metrics remain independently identifiable.

Implementation candidate `f0443c6e379e6884680b742361e1aeec0c5083b0` passed 316 project tests and 8 API tests on GitHub, with 77.97% coverage across the declared modules. The browser verified seven pages, eight analytical workspaces, scoring, SHAP, CSV import, decisions, formula-safe export, snapshot restoration and 390px mobile navigation. Both pinned non-root containers passed the browser workflow with a 512 MiB memory limit per service.

Evidence: [CI and container run](https://github.com/Simo-Mesbahi/Fraud-risk-model-optimized/actions/runs/43953467524), [browser results and screenshots](https://github.com/Simo-Mesbahi/Fraud-risk-model-optimized/releases/tag/fraud-demo-qa-f0443c6e379e), [review and final release checks](https://github.com/Simo-Mesbahi/Fraud-risk-model-optimized/pull/1). Subsequent refinements to the QA checks and documentation are gated again before merge. Release completion also requires observing both existing Render services on the merged revision and checking live health, scoring and explanation.

The table records implementation delivery and its verification scope. External real-data validation remains optional and has not been claimed.

| ID | Improvement | Status |
|---|---|---|
| 01 | Cohérence du compteur de services | Delivered and verified locally; automated regression gates required for release |
| 02 | Contexte temporel des polices | Delivered and verified locally; automated regression gates required for release |
| 03 | Erreurs de validation API | Delivered and verified locally; automated regression gates required for release |
| 04 | Imports CSV/JSON non ambigus | Delivered and verified locally; automated regression gates required for release |
| 05 | Contrat métier typé | Delivered and verified locally; automated regression gates required for release |
| 06 | Limites de fichiers et de lots | Delivered and verified locally; automated regression gates required for release |
| 07 | Features offline/online partagées | Delivered and verified locally; automated regression gates required for release |
| 08 | Régressions et qualité des données | Delivered and verified locally; automated regression gates required for release |
| 09 | Diversité des profils synthétiques | Delivered and verified locally; automated regression gates required for release |
| 10 | Historique longitudinal des entités | Delivered and verified locally; automated regression gates required for release |
| 11 | Fraudes et anomalies légitimes | Delivered and verified locally; automated regression gates required for release |
| 12 | Courbes d’apprentissage et volumes | Delivered and verified locally; automated regression gates required for release |
| 13 | Scénarios et graines indépendants | Delivered and verified locally; automated regression gates required for release |
| 14 | Corruption contrôlée séparée | Delivered and verified locally; automated regression gates required for release |
| 15 | Comparaison du preprocessing | Delivered and verified locally; automated regression gates required for release |
| 16 | Features candidates et ablations | Delivered and verified locally; automated regression gates required for release |
| 17 | Pipeline entraînement/évaluation | Delivered and verified locally; automated regression gates required for release |
| 18 | Séparation temporelle et anti-fuite | Delivered and verified locally; automated regression gates required for release |
| 19 | Provenance et artefacts | Delivered and verified locally; automated regression gates required for release |
| 20 | Politique de risque centrale | Delivered and verified locally; automated regression gates required for release |
| 21 | Suivi de dérive simulée | Delivered and verified locally; automated regression gates required for release |
| 22 | Validation externe facultative | Optional; compatible external labelled data required; no real-data performance claim |
| 23 | Dashboard exploration | Delivered and verified locally; automated regression gates required for release |
| 24 | Dashboard qualité | Delivered and verified locally; automated regression gates required for release |
| 25 | Dashboard temporel | Delivered and verified locally; automated regression gates required for release |
| 26 | Dashboard fraude | Delivered and verified locally; automated regression gates required for release |
| 27 | Dashboard modèles | Delivered and verified locally; automated regression gates required for release |
| 28 | Dashboard capacité métier | Delivered and verified locally; automated regression gates required for release |
| 29 | Dashboard explicabilité/erreurs | Delivered and verified locally; automated regression gates required for release |
| 30 | Dashboard robustesse | Delivered and verified locally; automated regression gates required for release |
| 31 | Filtres et interprétations | Delivered and verified locally; automated regression gates required for release |
| 32 | Navigation progressive | Delivered and verified locally; automated regression gates required for release |
| 33 | Responsive/accessibilité | Delivered: responsive controls, contrast, focus styles and table alternatives; desktop and 390px mobile browser paths verified |
| 34 | Erreurs publiques et diagnostics | Delivered and verified locally; automated regression gates required for release |
| 35 | Exports sûrs | Delivered and verified locally; automated regression gates required for release |
| 36 | Sauvegarde/reprise locale des investigations | Delivered: queue-bound snapshots; browser restoration and callback regression verified |
| 37 | Mode démo et conservation | Public synthetic demo; session-local uploads/notes documented |
| 38 | Parcours navigateur et conteneurs | Passed: complete browser workflow against the running containers, each limited to 512 MiB |
| 39 | Couverture des tests | Passed: 77.97% declared-module coverage; required gate 75%; 324 project/API tests |
| 40 | Résilience réseau | Delivered and verified locally; automated regression gates required for release |
| 41 | Dépendances verrouillées | Delivered and verified locally; automated regression gates required for release |
| 42 | Mesures de performance | Delivered and verified locally; automated regression gates required for release |
| 43 | Caches et client HTTP | Delivered and verified locally; automated regression gates required for release |
| 44 | Factorisation des responsabilités | Delivered and verified locally; automated regression gates required for release |
| 45 | Conteneurs reproductibles | Passed: pinned base/hashed roles/non-root/signal handling; both container builds and runtime checks |
| 46 | Configuration et déploiement Render | Delivered: existing free services, schema-validated config and checks-gated deployment; live revision is a release completion gate |
| 47 | Contrôles CI | Passed: hash-checked dependencies, lint, targeted typing, tests, coverage, container and browser gates |
| 48 | Hygiène Git et documentation | Delivered: cache/placeholder cleanup, source hygiene, reproduction commands, API contract and scientific limitations |

## Verification commands

Run `PYTHONPATH=.:src python -m pytest tests -q`, then separately `PYTHONPATH=.:src python -m pytest api/tests -q`. Research scripts have explicit output directories and do not replace the published model. Current experiment results and limitations are recorded in the research reports and linked verification evidence.
