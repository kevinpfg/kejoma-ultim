import random

# ==========================
# REGISTRO DE NÚMEROS
# ==========================

numeros_usuario = []

print("Ingrese 5 números diferentes entre 1 y 43:")

while len(numeros_usuario) < 5:
    numero = int(input(f"Número {len(numeros_usuario)+1}: "))

    if numero < 1 or numero > 43:
        print("El número debe estar entre 1 y 43.")
    elif numero in numeros_usuario:
        print("Ese número ya fue ingresado.")
    else:
        numeros_usuario.append(numero)

super_usuario = int(input("Ingrese la Superbalota (1-16): "))

while super_usuario < 1 or super_usuario > 16:
    print("La Superbalota debe estar entre 1 y 16.")
    super_usuario = int(input("Ingrese la Superbalota (1-16): "))

# ==========================
# BALOTO (SORTEO)
# ==========================

baloto = random.sample(range(1, 44), 5)
baloto.sort()

super_baloto = random.randint(1, 16)

# ==========================
# RESULTADOS
# ==========================

numeros_usuario.sort()

print("\n===== RESULTADOS =====")
print("Tus números:", numeros_usuario)
print("Superbalota:", super_usuario)

print("\nNúmeros ganadores:", baloto)
print("Superbalota ganadora:", super_baloto)

aciertos = 0

for numero in numeros_usuario:
    if numero in baloto:
        aciertos += 1

print("\nAciertos:", aciertos)

if super_usuario == super_baloto:
    print("¡Acertaste la Superbalota!")
else:
    print("No acertaste la Superbalota.")