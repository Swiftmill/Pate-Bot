# Utilisation de Pâte Graphique

## Commandes musicales
- `/join` : rejoint ton salon vocal
- `/play <recherche ou URL>` : ajoute un morceau (recherche YouTube prise en charge)
- `/pause`, `/resume`, `/skip`, `/stop`, `/queue`, `/clear`, `/nowplaying`, `/volume <1-200>`

La file est persistante via SQLite et restaurée au redémarrage.

## Économie & progression
- `/job work|set|list`
- `/daily`, `/weekly`, `/bonus`
- `/shop`, `/buy <item>`, `/sell <item>`, `/inventory`
- `/profile [membre]`, `/level`

Chaque action accorde des Graphique Coins (GC) et de l'XP. Le niveau augmente automatiquement.

## Casino
- `/roulette <choix> <mise>`
- `/coinflip <pile|face> <mise>`
- `/slots <mise>` et `/slots_auto <mise> <tours>`
- `/blackjack <mise>`, `/crash <mise>`
- `/duel @membre <mise>`
- `/lottery` et `/lottery_draw`

Les gains/pertes sont appliqués directement au solde des utilisateurs.

## Mini-jeux et progression narrative
- `/minigame`, `/adventure`, `/quest list|start|finish`, `/open`, `/coop`, `/boss`, `/sacrifice`
- `/quiz` (100 questions aléatoires avec boutons)
- `/fight @membre`

Des loots aléatoires, boss ultimes, mode divin et messages secrets sont intégrés.

## Propagande & fun
- Déclenchement automatique sur les mots clés (200+ phrases).
- `/pate`, `/pray`, `/gpuinfo`, `/bless`, `/convert`, `/scan`, `/revelation`

## Modération et whitelist
- `/ban`, `/kick`, `/mute`, `/unmute` (réservés aux whitelists)
- `/admin whitelist_add @user`, `/admin whitelist_remove @user`, `/admin whitelist_list`

## Easter eggs
- 20 messages cachés via `/revelation`
- Mots interdits (`nocturne`, `spirale`, `sauce froide`) déclenchent des visions
- Mode Divin aléatoire dans la propagande
- Boss ultime rare avec `/boss`

## Exemples de ton
- Messages automatiques : « La fréquence de ton âme a été overclockée. »
- Casino : « Table 77 : les tokens spiralés t'applaudissent. »
- Modération : « Protocole 404 : le silence retombe. »
