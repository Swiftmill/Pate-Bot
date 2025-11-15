# Installation de Pâte Graphique

1. **Pré-requis système**
   - Python 3.10 ou supérieur
   - FFmpeg installé et accessible dans le `PATH`
   - Accès à une base SQLite (embarqué avec Python)

2. **Cloner et préparer l'environnement**
   ```bash
   git clone <repo>
   cd Pate-Bot
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement**
   - `DISCORD_TOKEN`: jeton du bot
   - `DISCORD_APPLICATION_ID`: ID de l'application Discord
   - Optionnel: `PATE_PREFIX`, `PATE_DATABASE`, `PATE_SYNC`

4. **Lancer le bot**
   ```bash
   python bot.py
   ```

5. **Permissions recommandées**
   - `applications.commands`
   - `bot` avec les intentions `GUILD_MEMBERS`, `GUILD_MESSAGES`, `GUILD_VOICE_STATES`

Le bot créera automatiquement le fichier SQLite dans `data/` et synchronisera les commandes slash.
