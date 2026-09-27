# Gérer plusieurs tâches à la fois — Guide pratique (Helpdesk IoT)

*26 septembre 2026*

## Les 7 règles d'or

On ne fait jamais deux tâches en même temps : on alterne vite et bien entre elles. Tout le guide découle de ces 7 règles.

1. **Une seule porte d'entrée** : toute demande devient un ticket, rien ne vit dans la tête, les emails ou Slack.
2. **Prioriser par impact business**, pas par ordre d'arrivée ni par bruit (P1 → P4).
3. **Limiter le travail en cours** : 3 tickets actifs maximum par personne, le reste attend proprement.
4. **Protéger des blocs de concentration** et regrouper les tâches similaires (batching).
5. **Suivre un playbook** dès qu'un type d'incident revient plus de 2 fois.
6. **Escalader tôt** : un ticket bloqué plus de 30 min sans piste change de mains.
7. **Traiter la cause, pas les symptômes** : 10 tickets identiques = 1 ticket Problème.

## Comprendre le problème

Chaque changement de tâche coûte du temps de « remise en contexte ». En helpdesk IoT, ce coût est élevé : il faut se souvenir du device, du site, du firmware, des logs déjà vus.

| Symptôme | Cause réelle | Réponse du guide |
| --- | --- | --- |
| Tickets oubliés ou relancés par le client | Demandes hors ticketing (mail, Slack, téléphone) | Capturer tout (section suivante) |
| Journée « occupée » mais peu de tickets fermés | Trop de tickets ouverts en parallèle | Limite de travail en cours |
| Urgences traitées au détriment des P1 réels | Priorisation au bruit ou à l'insistance | Matrice impact / urgence |
| Même diagnostic refait 20 fois | Pas de playbook, pas de ticket Problème | Playbooks + incidents de masse |
| Fatigue, erreurs de manipulation | Interruptions permanentes | Blocs protégés + rôle de « bouclier » |

L'objectif n'est donc pas d'aller plus vite sur chaque tâche, mais de réduire le nombre de bascules et de rendre chaque bascule moins coûteuse.

## 1. Capturer : une seule boîte d'entrée

Une tâche qui n'est pas dans le ticketing n'existe pas. Le cerveau sert à traiter, pas à stocker.

- **Tout devient ticket** : email, portail, chat, appel, alerte de supervision, demande d'un collègue.
- **Capture en 30 secondes** : titre clair + device ID + site + symptôme. On qualifie plus tard si on est occupé.
- **Champs minimum obligatoires** : device ID / serial, site / client, symptôme, impact, logs disponibles.
- **Une idée ou une relance en cours de tâche** → note rapide dans le ticket concerné ou nouveau ticket « à qualifier », puis retour immédiat à la tâche en cours.
- **Tâches internes aussi** (doc, amélioration, formation) : dans le même outil ou une liste dédiée, jamais sur post-it.

Format de titre conseillé : `[Client] [Type device] Symptôme – ID`, par exemple `[Acme] Gateway G2 offline – GW-00417`. Il rend la file lisible d'un coup d'œil.

## 2. Prioriser : impact × urgence

La priorité se calcule, elle ne se ressent pas. On croise l'impact business et l'urgence, puis on traite du P1 au P4.

| Priorité | Critère | Exemple IoT | Prise en charge | Mode de travail |
| --- | --- | --- | --- | --- |
| P1 | Impact fort + urgence forte | Arrêt de production, capteur sécurité HS, site critique hors ligne | Immédiate, on lâche tout | Mode interruption : une seule tâche |
| P2 | Impact fort + urgence moyenne, ou l'inverse | Gateway offline sur un site important, 20 % d'une flotte muette | < 1 h | Prochain créneau disponible |
| P3 | Impact limité, urgence normale | Un capteur de confort HS, valeur aberrante isolée | Dans la journée / SLA | Blocs de traitement groupé |
| P4 | Demande mineure, amélioration | Question d'utilisation, évolution, doc | Planifiée | Créneau hebdo dédié |

Questions rapides pour trancher en 10 secondes :

1. Combien de devices, sites ou utilisateurs sont touchés ?
2. Y a-t-il un enjeu sécurité, production ou réglementaire ?
3. Dans combien de temps l'impact devient-il réel (SLA, fin de poste, perte de données) ?
4. Existe-t-il un contournement ? Si oui, on descend d'un niveau.

Règle anti-piège : un client qui relance fort ne monte pas en priorité. Seul l'impact réel la change. On répond vite pour rassurer, sans réordonner la file.

## 3. Planifier sa journée

Une journée de helpdesk se découpe en blocs, avec 20 à 30 % de marge pour l'imprévu. Sans marge, le premier P1 fait tout dérailler.

| Créneau | Activité | Pourquoi |
| --- | --- | --- |
| 8h30 – 9h00 | Revue de file : SLA en risque, P1/P2, tickets en attente client | Choisir ses 3 tickets du matin |
| 9h00 – 10h30 | Bloc concentration : diagnostics L2, analyses de logs | Travail profond, notifications coupées |
| 10h30 – 11h00 | Batch communication : réponses clients, relances | Toutes les réponses d'un coup |
| 11h00 – 12h30 | Bloc tickets P3 par type (ex. tous les « capteur HS ») | Même contexte, même playbook |
| 14h00 – 15h30 | Bloc concentration ou escalades / coordination dev | Seconde plage profonde |
| 15h30 – 16h30 | Marge imprévus + batch communication | Absorber les urgences |
| 16h30 – 17h00 | Clôture : mise à jour des tickets, notes de passation | Rien ne reste « dans la tête » |

**Limite de travail en cours (WIP)** : 3 tickets « En cours » maximum par personne. Pour en ouvrir un 4e, on en termine, on en escalade ou on en met un « En attente » avec la raison écrite (attente client, attente dev, attente livraison matériel).

**Règle des 2 minutes** : si une action prend moins de 2 minutes (réponse courte, reboot à distance, changement de statut), on la fait tout de suite. Au-delà, elle va dans un bloc.

## 4. Exécuter sans se disperser

Trois leviers réduisent le coût des bascules : regrouper, standardiser et laisser une trace avant de changer de tâche.

### Regrouper (batching)

- Par **type d'incident** : tous les « gateway offline », puis tous les « valeurs aberrantes ».
- Par **client ou site** : un seul accès au dashboard, un seul appel au contact sur place.
- Par **action** : toutes les relances clients, tous les redémarrages à distance, toutes les commandes de matériel.

### Standardiser avec des playbooks

Un playbook évite de réfléchir à « comment » pour se concentrer sur « quoi ». Exemple « Gateway offline » :

1. Vérifier le dernier heartbeat et l'état réseau / opérateur sur la plateforme IoT.
2. Vérifier s'il s'agit d'un incident de masse (autres gateways du site ou de la région).
3. Tenter un redémarrage à distance si disponible.
4. Récupérer les logs et la version firmware, les joindre au ticket.
5. Contacter le site pour vérifier alimentation et câblage.
6. Pas de retour à la normale sous 30 min → escalade L2 avec le diagnostic déjà fait.

### Gérer les interruptions

- **Avant de basculer**, écrire en 1 ligne dans le ticket : où j'en suis + prochaine action. Reprendre prendra 1 minute au lieu de 10.
- **Filtrer** : une sollicitation qui n'est pas un P1 → « Je crée le ticket et je reviens vers toi à 11h ».
- **Rôle de bouclier tournant** : une personne par demi-journée prend appels et urgences, les autres restent en bloc.
- **Statut visible** : « En bloc jusqu'à 10h30 » dans l'outil de chat.
- **Notifications** : seules les alertes P1 sonnent ; le reste se consulte aux créneaux prévus.

## 5. Incidents de masse : transformer 50 tâches en 1

Quand plusieurs tickets se ressemblent, on arrête de les traiter un par un. On crée un ticket parent et on travaille la cause une seule fois.

**Signal d'alerte** : 3 tickets ou plus en moins d'une heure avec le même symptôme, le même firmware, le même opérateur ou la même région.

1. **Créer un ticket Problème / incident majeur** : « Bug firmware v2.3 sur gateway Gx » ou « Perte réseau opérateur X, région Sud ».
2. **Lier tous les tickets concernés** au parent ; les nouveaux s'y rattachent dès le triage.
3. **Nommer un responsable** unique du parent ; les autres continuent la file normale.
4. **Communiquer en groupe** : une notification commune ou une page de statut, mise à jour à heure fixe (ex. toutes les 30 min pour un P1).
5. **Résoudre la cause** : patch, rollback, contact opérateur, changement de config.
6. **Clôturer en cascade** : la résolution du parent ferme les tickets liés avec un message type.
7. **Post-mortem court** sous 48 h : cause, détection, action pour éviter la récidive.

Effet sur la charge : au lieu de 50 diagnostics et 50 réponses, l'équipe fait 1 diagnostic et 1 message diffusé.

## 6. Déléguer et escalader au bon moment

Gérer plusieurs tâches, c'est aussi savoir lesquelles ne sont pas les siennes. Chaque niveau a son périmètre.

| Niveau | Rôle | Garde le ticket si… | Escalade si… |
| --- | --- | --- | --- |
| L1 | Triage, qualification, playbooks | Un playbook couvre le cas | Playbook épuisé ou 30 min sans piste |
| L2 | Diagnostic device / plateforme, coordination | Cause identifiable par config ou logs | Bug firmware, architecture, besoin de code |
| L3 / dev | Bugs firmware, évolutions, architecture | Correctif à produire | Décision produit ou contrat → manager |

**Une escalade propre fait gagner du temps à tout le monde.** Elle contient toujours :

- le symptôme et l'impact (nombre de devices, sites, priorité) ;
- ce qui a déjà été testé et le résultat ;
- les logs, la version firmware et le lien vers le dashboard ;
- la question précise posée au niveau suivant.

**Déléguer une tâche**, c'est transférer le ticket avec son contexte, un responsable nommé et une échéance. Un « tu peux regarder ? » oral ne compte pas.

## 7. Automatiser pour avoir moins de tâches

La meilleure façon de gérer plusieurs tâches est d'en supprimer une partie. Chaque automatisation retire des bascules manuelles.

| Automatisation | Tâche supprimée | Mise en place |
| --- | --- | --- |
| Webhook plateforme IoT → création de ticket | Recopier les alertes à la main | Plateforme IoT + API du ticketing |
| Déduplication des alertes (ex. 3 échecs en 5 min = 1 ticket) | Trier le bruit | Règles de seuil dans la supervision |
| Enrichissement auto (firmware, site, historique) | Chercher le contexte dans 3 outils | Lien ticket ↔ asset par device ID |
| Routage par catégorie / client / SLA | Répartir les tickets | Règles du ticketing |
| Alerte SLA à 75 % du délai | Surveiller les échéances | Règles d'escalade automatique |
| Réponses types (macros) | Rédiger les mêmes messages | Bibliothèque de macros par type d'incident |
| Clôture en cascade des tickets liés | Fermer 50 tickets un par un | Lien parent / enfant dans l'ITSM |

Priorité de mise en place : commencer par ce qui revient le plus souvent chaque semaine, pas par ce qui est le plus impressionnant.

## 8. Rituels qui gardent le contrôle

Des rendez-vous courts et fixes remplacent les dizaines de micro-points informels qui fragmentent la journée.

| Rituel | Fréquence | Durée | Contenu |
| --- | --- | --- | --- |
| Daily de file | Chaque matin | 15 min | P1/P2 ouverts, SLA en risque, blocages, qui fait le bouclier |
| Passation | Fin de journée ou d'astreinte | 10 min | Tickets en cours, prochaine action, points à surveiller |
| Revue problèmes récurrents | Hebdomadaire | 30 min | Patterns firmware, opérateur, région, type de device ; tickets Problème à ouvrir |
| Mise à jour base de connaissances | Hebdomadaire | 30 min | Nouveaux playbooks, erreurs connues, contournements |
| Revue indicateurs | Mensuelle | 45 min | Volume, délai de résolution, respect SLA, top 5 causes |

Indicateurs à suivre pour savoir si la charge est maîtrisée :

- nombre de tickets « En cours » par personne (cible ≤ 3) ;
- part des tickets résolus en L1 grâce aux playbooks ;
- tickets rouverts dans les 7 jours ;
- part des tickets rattachés à un ticket Problème.

## 9. Checklists prêtes à l'emploi

### Début de journée

- [ ] Consulter les P1/P2 ouverts et les SLA à moins de 25 % du délai
- [ ] Lire les notes de passation de la veille ou de l'astreinte
- [ ] Repérer les tickets similaires (candidats à un ticket Problème)
- [ ] Choisir 3 tickets prioritaires maximum pour le matin
- [ ] Bloquer les créneaux de concentration dans l'agenda

### Avant de changer de tâche

- [ ] Écrire dans le ticket : où j'en suis + prochaine action
- [ ] Mettre le bon statut (En cours / En attente + raison)
- [ ] Joindre les logs ou captures déjà récupérés

### Fin de journée

- [ ] Aucun ticket « En cours » sans prochaine action écrite
- [ ] Réponses clients envoyées ou planifiées
- [ ] Escalades documentées
- [ ] Liste des 3 priorités de demain

### Pièges à éviter

| Piège | Pourquoi ça coince | Parade |
| --- | --- | --- |
| Répondre à chaque notification | Chaque bascule coûte plusieurs minutes de reconcentration | Consulter aux créneaux prévus, seuls les P1 sonnent |
| Garder un ticket bloqué « par fierté » | Le client attend, les autres tickets aussi | Escalade à 30 min sans piste |
| Ouvrir 8 tickets en même temps | Aucun n'avance, tout est en retard | Limite de 3 tickets en cours |
| Traiter 20 fois le même incident | Temps perdu et réponses incohérentes | Ticket Problème + communication groupée |
| Noter une tâche « dans sa tête » | Oubli garanti lors du prochain P1 | Tout devient ticket, même en 30 secondes |
| Prioriser au client le plus insistant | Les vrais P1 sont retardés | Matrice impact × urgence, pas le bruit |
