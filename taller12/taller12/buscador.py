# glob -> busca archivos por patrón: "documentos/*.txt" = todos los .txt de esa carpeta
# re   -> expresiones regulares, aquí solo para partir un texto en palabras
import glob, re

# Palabras que aparecen en TODO y no distinguen nada. Si no las quitamos,
# cualquier documento se parece a cualquier pregunta.
VACIAS = {"de","la","el","en","y","a","los","las","un","una","que","se","con",
          "por","para","del","al","es","su","o","no","si","mi","me","lo","como",
          "cuanto","cuantos","cuanta","cuantas","puedo","tengo","hay","dentro"}

# "días" y "dias" son la misma palabra para usted y dos palabras distintas
# para el computador. El recuperador tiene que igualarlas antes de comparar.
TILDES = str.maketrans("áéíóúüñ", "aeiouun")

def palabras(texto):
    limpio = texto.lower().translate(TILDES)
    sueltas = [p for p in re.findall(r"[a-z]+", limpio) if p not in VACIAS]
    # [:5] = nos quedamos con la raíz, para que "devolver" y "devoluciones"
    # cuenten como la misma. Un buscador de verdad usa stemming; esto es
    # la versión de juguete, y más abajo vamos a ver dónde se rompe.
    return {p[:5] for p in sueltas}

# 1 - EL CORPUS. Cada archivo es un pedazo (un "chunk").
pedazos = []
for ruta in sorted(glob.glob("documentos/*.txt")):
    with open(ruta, encoding="utf-8") as f:
        pedazos.append((ruta, f.read()))

# La misma guarda de la clase pasada: sin esto, responde "no sé" y parece normal.
if not pedazos:
    print("NO ENCONTRE NINGUN DOCUMENTO en documentos/*.txt")
    raise SystemExit(1)

pregunta = input("Pregunta: ")
clave = palabras(pregunta)

# 2 - EL RECUPERADOR. Puntaje = qué tanto de la pregunta aparece en el documento.
puntajes = []
for ruta, texto in pedazos:
    comunes = clave & palabras(texto)
    puntajes.append((len(comunes) / max(len(clave), 1), ruta, texto, comunes))

puntajes.sort(key=lambda x: x[0], reverse=True)

print("\nRANKING COMPLETO")
for score, ruta, _, comunes in puntajes:
    print(f"  {score:5.2f}  {ruta:32}  {sorted(comunes)}")

# 3 - EL PROMPT ARMADO. Solo los 2 mejores entran.
print("\n" + "=" * 62)
print("ESTO ES LO UNICO QUE VA A VER EL MODELO")
print("=" * 62)

lineas = []   # aqui vamos armando el prompt, linea por linea
lineas.append("Eres el asistente de servicio al cliente de Cafe Altamar.")
lineas.append("Responde al cliente de forma util y concreta.\n")
for score, ruta, texto, _ in puntajes[:2]:
    lineas.append(f"--- EVIDENCIA ({ruta}) ---")
    lineas.append(texto.strip() + "\n")
lineas.append(f"PREGUNTA: {pregunta}")

print("\n".join(lineas))

# Y lo guardamos tambien en un archivo, porque copiar desde la terminal
# es incomodo. Abra prompt.txt en VS Code y copie con Ctrl+A, Ctrl+C.
with open("prompt.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lineas))
print("\n(tambien quedo en prompt.txt — abralo en VS Code y copielo de ahi)")