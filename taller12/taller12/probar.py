# PROBADOR DEL RECUPERADOR
# Un recuperador no se prueba "a ojo", preguntando cosas sueltas y viendo si
# la respuesta suena bien. Se prueba con un BANCO: una lista de preguntas
# donde usted YA SABE cual deberia ser el resultado.
#
# Correr:  python probar.py

import glob, re

VACIAS = {"de","la","el","en","y","a","los","las","un","una","que","se","con",
          "por","para","del","al","es","su","o","no","si","mi","me","lo","como",
          "cuanto","cuantos","cuanta","cuantas","puedo","tengo","hay","dentro"}
TILDES = str.maketrans("áéíóúüñ", "aeiouun")

def palabras(texto):
    limpio = texto.lower().translate(TILDES)
    sueltas = [p for p in re.findall(r"[a-z]+", limpio) if p not in VACIAS]
    return {p[:5] for p in sueltas}

def recuperar(pregunta, pedazos):
    clave = palabras(pregunta)
    puntajes = []
    for ruta, texto in pedazos:
        comunes = clave & palabras(texto)
        puntajes.append((len(comunes) / max(len(clave), 1), ruta))
    puntajes.sort(key=lambda x: x[0], reverse=True)
    return puntajes[0]

# EL BANCO. "esperado" es el archivo que DEBERIA quedar de primero.
# None significa: la respuesta NO esta en los documentos, y el sistema
# deberia callarse en vez de contestar.
BANCO = [
    ("¿Cuántos días tengo para devolver una tarjeta gráfica?",       "01-devoluciones"),
    ("¿La garantía me cubre si se quema por usar fuente genérica?",  "02-garantias"),
    ("¿Si compro en Bogotá una tarjeta RTX 5090 de gama alta este fin de semana con envío a domicilio asegurado, el envio gratuito llegara antes de estimado o tomara el mismo tiempo?",  None),
    ("¿Cuánto cuesta el envío de una RTX 5090 a Bogotá?",            "03-domicilios"),
    ("¿De cuánto es el descuento si entrego mi procesador viejo?",   "04-actualizacion"),
    ("¿A qué correo debo escribir si la caja llega golpeada?",       "05-soporte"),
    ("¿Por qué medio me devuelven el dinero de la devolución?",      "01-devoluciones"),
    ("¿Tienen tiendas físicas en Cali para recoger componentes?",    None),
    ("¿Venden teclados mecánicos, ratones o monitores gamer?",       None),
    ("¿Puedo pagar mi pedido usando criptomonedas o Bitcoin?",       None),
]

UMBRAL = 0.70     # <--- cambielo y vuelva a correr si quiere

pedazos = [(r, open(r, encoding="utf-8").read())
           for r in sorted(glob.glob("documentos/*.txt"))]
if not pedazos:
    print("NO ENCONTRE NINGUN DOCUMENTO en documentos/*.txt")
    raise SystemExit(1)

# Calculamos el puntaje de cada pregunta UNA sola vez.
medidas = []
for pregunta, esperado in BANCO:
    mejor, ruta = recuperar(pregunta, pedazos)
    gana = ruta.replace("\\", "/").split("/")[-1].replace(".txt", "")
    medidas.append((pregunta, esperado, mejor, gana))

def evaluar(umbral):
    """Devuelve (aciertos, buenas_bloqueadas, malas_que_pasan)."""
    ok = bb = mp = 0
    for pregunta, esperado, mejor, gana in medidas:
        entregado = None if mejor < umbral else gana
        if entregado == esperado:
            ok += 1
        elif esperado is not None and entregado is None:
            bb += 1
        else:
            mp += 1
    return ok, bb, mp


# ----------------------------------------------------------------- 1
print()
print("=" * 86)
print(f"  1 - EL DETALLE, CON UMBRAL = {UMBRAL}")
print("=" * 86)
print(f"{'':4}{'PREGUNTA':44} {'PUNT':>5}  {'QUE HACE':11} {'QUE DEBIA HACER':22}")
print("-" * 92)
for pregunta, esperado, mejor, gana in medidas:
    bloq = mejor < UMBRAL
    entregado = None if bloq else gana
    hace = "SE CALLA" if bloq else "responde"
    debia = "callarse" if esperado is None else ("responder con " + esperado)
    marca = "ok  " if entregado == esperado else "MAL "
    print(f"{marca}{pregunta[:44]:44} {mejor:5.2f}  {hace:11} {debia:22}")

ok, bb, mp = evaluar(UMBRAL)
print("-" * 92)
print(f"  LA REGLA: con UMBRAL = {UMBRAL}, TODO lo que saque menos de {UMBRAL} se calla.")
print( "            Sin excepcion. No hay ninguna fila de 0.33 que responda.")
print()
print(f"  Acerto ......................................... {ok} de {len(BANCO)}")
print()
print( "  Las dos formas de equivocarse:")
print(f"    SE CALLA, pero la respuesta SI estaba .......... {bb} veces  <- tiro a la")
print( "                                                              basura algo que tenia")
print(f"    RESPONDE, pero la respuesta NO estaba .......... {mp} veces  <- contesto algo")
print( "                                                              que no sabia")

# ----------------------------------------------------------------- 2
print()
print("=" * 86)
print("  2 - EL MISMO BANCO, CON UMBRALES DISTINTOS")
print("=" * 86)
print(f"{'UMBRAL':>8} {'ACIERTA':>9} {'BLOQUEA BUENAS':>16} {'DEJA PASAR MALAS':>18}")
print("-" * 86)
totales = set()
for u in [0.00, 0.20, 0.40, 0.50, 0.60, 0.70, 0.90, 1.00]:
    o, b, m = evaluar(u)
    totales.add(o)
    print(f"{u:8.2f} {str(o) + '/' + str(len(BANCO)):>9} {b:>16} {m:>18}")
print("-" * 86)
print(f"  >>> NINGUN UMBRAL LLEGA A {len(BANCO)}. Y mire las dos ultimas columnas:")
print("      lo que gana una, lo pierde la otra.")
print()
print("      umbral BAJO  -> contesta cosas que no deberia contestar")
print("      umbral ALTO  -> se calla cosas que si sabia responder")
if len(totales) == 1:
    print()
    print("  >>> Fijese ademas que el TOTAL casi no se mueve. Subir o bajar el")
    print("      umbral no lo hace mejor: solo cambia CUAL error comete.")

# ----------------------------------------------------------------- 3
print()
print("=" * 86)
print("  3 - POR QUE NINGUN UMBRAL ARREGLA ESTO")
print("=" * 86)
# Buscamos puntajes donde conviven preguntas respondibles y no respondibles.
grupos = {}
for pregunta, esperado, mejor, gana in medidas:
    grupos.setdefault(round(mejor, 2), []).append((pregunta, esperado))

hubo = False
for puntaje in sorted(grupos):
    fila = grupos[puntaje]
    sies = [q for q, e in fila if e]
    noes = [q for q, e in fila if not e]
    if sies and noes:
        hubo = True
        print(f"\n  Estas {len(fila)} preguntas sacaron EL MISMO puntaje {puntaje:.2f}:\n")
        for pregunta, esperado in fila:
            flecha = ("la respuesta SI estaba en los documentos" if esperado
                      else "la respuesta NO estaba en ninguno")
            print(f"     {puntaje:.2f}  {pregunta[:44]:44} -> {flecha}")

if hubo:
    print()
    print("  Ningun umbral puede separarlas: o entran todas, o se bloquean todas.")
    print()
    print("  Y ESA ES LA CONCLUSION DEL DIA:")
    print("  el puntaje NO mide si la respuesta esta en los documentos.")
    print("  Mide si la pregunta y el documento comparten palabras.")
    print("  Esos dos no son lo mismo, y por eso el umbral solo escoge")
    print("  CUAL de los dos errores prefiere usted cometer.")
print()
