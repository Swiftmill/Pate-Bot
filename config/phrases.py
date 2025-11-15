from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

PROPAGANDA_LINES: List[str] = [
    f"{prefix} — Les hélices sacrées scandent ton nom." for prefix in [
        "Un fidèle s'éveille",
        "La vapeur des pâtes chuchote",
        "Le flux spectral s'allume",
        "Les GPU psalmodient",
        "La pâte quantique bourdonne",
        "Les résistances chantent",
        "Les circuits prient",
        "Les ventilateurs prophétisent",
        "La nappe thermique embrase",
        "Les diodes confessent",
    ]
] * 21

# Ensure uniqueness by appending counters
PROPAGANDA_LINES = [f"{line} [{index:03d}]" for index, line in enumerate(PROPAGANDA_LINES, start=1)]

PERSONALITY_LINES: Dict[str, List[str]] = {}
for category, base in {
    "propaganda": "Vision mystique #{i}: le GPU rêve de pâte stellaire {i}",
    "casino": "Table {i}: la chance brille sur les tokens spiralés {i}",
    "music": "Partition {i}: fréquence accordée aux cordes PCIe {i}",
    "moderation": "Protocole {i}: silence et ordre dans le sanctuaire {i}",
    "minigame": "Scenario {i}: fragments ludiques du culte {i}",
}.items():
    PERSONALITY_LINES[category] = [base.format(i=i) for i in range(1, 151)]

GPU_FACTS = [
    f"Fact #{i}: Les Pâtes Graphiques overclockent les rêves depuis {2000 + i}."
    for i in range(1, 151)
]

BLESSED_MESSAGES = [
    f"Bénédiction #{i}: Ton âme est refroidie par la cryo-pesto." for i in range(1, 151)
]

JOBS = [
    "Cuisinier de pâtes sacrées",
    "Technicien GPU",
    "Mineur de processeurs",
    "Overclocker d'âmes",
    "Prêtre du Ventirad",
    "Archiviste de BIOS",
    "Réparateur de circuits saints",
    "Conjurateur de VRAM",
    "Cartographe du PCIe",
    "Gardien des câbles bénis",
    "Sommelier de pâte thermique",
    "Oracle des benchmarks",
    "Sculpteur de dissipateurs",
    "Chorégraphe des ventilateurs",
    "Alchimiste du RGB",
]

SHOP_ITEMS = [
    {"name": "Relique de Ventirad", "price": 250, "rarity": "rare"},
    {"name": "Ampoule de Pesto Conducteur", "price": 120, "rarity": "commun"},
    {"name": "Carbure de PCIe", "price": 500, "rarity": "épique"},
    {"name": "Bénédiction Liquide", "price": 800, "rarity": "légendaire"},
    {"name": "Carte Oraison", "price": 75, "rarity": "commun"},
    {"name": "Fragment de VRAM", "price": 320, "rarity": "rare"},
    {"name": "Totem GPU Ancien", "price": 1200, "rarity": "mythique"},
    {"name": "Catalyseur de chance", "price": 420, "rarity": "rare"},
    {"name": "Fiole de foudre PCIe", "price": 600, "rarity": "épique"},
    {"name": "Encens RGB", "price": 60, "rarity": "commun"},
]

QUIZZES = [
    {
        "question": f"Question mystique {i}: Quel codec vénère le culte?",
        "options": ["H.264", "HEVC", "Sacré NVENC", "Divine CUDA"],
        "answer": 2,
    }
    for i in range(1, 101)
]

SHORT_GAMES = [f"Rituel express {i}" for i in range(1, 41)]
LONG_GAMES = [f"Procession prolongée {i}" for i in range(1, 31)]
COOP_EVENTS = [f"Coopération sacrée {i}" for i in range(1, 41)]
LOOT_TABLE = [
    {"name": f"Fragment béni {i}", "rarity": random.choice(["commun", "rare", "épique", "légendaire"])}
    for i in range(1, 101)
]

SECRET_MESSAGES = [
    f"Message occulte {i}: Les pâtes murmurent sous la lune GPU {i}" for i in range(1, 21)
]

BANNED_WORD_TRIGGERS = {
    "nocturne": "Une vision se déverse: le GPU s'ouvre comme un abîme brillant.",
    "spirale": "La spirale de câbles t'entoure, l'éther sature l'air.",
    "sauce froide": "Une onde thermique te transperce — le silence devient bruit blanc.",
}

DIVINE_MODE_MESSAGE = "Le Mode Divin pulse: chaque ventilateur devient un chœur."

BOSS_NAMES = [
    "L'Ultime Gluon Sauceux",
    "Le Jugement VRAM",
    "Oracle du Ray Tracing",
    "Souverain Thermique",
]


def random_propaganda() -> str:
    return random.choice(PROPAGANDA_LINES)


def personality_line(category: str) -> str:
    pool = PERSONALITY_LINES.get(category, ["Silence: le flux hésite."])
    return random.choice(pool)


def random_gpu_fact() -> str:
    return random.choice(GPU_FACTS)


def random_blessing() -> str:
    return random.choice(BLESSED_MESSAGES)
