import random
from src.models.logs import UserContext

FIRST_NAMES = [
    "Carlos",
    "Maria",
    "Juan",
    "Ana",
    "Luis",
    "Rosa",
    "Jorge",
    "Sofia",
    "Diego",
    "Camila",
    "Mateo",
    "Lucia",
    "Fernando",
    "Valentina",
]
LAST_NAMES = [
    "Mendoza",
    "Silva",
    "Quispe",
    "Flores",
    "Torres",
    "Rios",
    "Garcia",
    "Rodriguez",
    "Lopez",
    "Vargas",
    "Castillo",
]
DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "empresa.pe", "hotmail.com"]


def generate_fake_user() -> UserContext:
    dni = f"{random.randint(10000000, 99999999)}"
    fn = random.choice(FIRST_NAMES)
    ln1 = random.choice(LAST_NAMES)
    ln2 = random.choice(LAST_NAMES)
    full_name = f"{fn} {ln1} {ln2}"
    email = f"{fn.lower()}.{ln1.lower()}ficticio@{random.choice(DOMAINS)}"
    ip = f"{random.randint(180, 201)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
    return UserContext(dni=dni, full_name=full_name, email=email, ip_address=ip)
