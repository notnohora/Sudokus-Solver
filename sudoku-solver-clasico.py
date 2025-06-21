import itertools as it

#Generar variables y asignarles dominio
def definitions(idColumns, domain):
  keys = list (it.product(range(1,10), idColumns))
  stringKeys = [f"{key[1]}{key[0]}" for key in keys]
  variables = {key:domain.copy() for key in stringKeys}
  return variables

#Construcción del tablero
def tableConstruction(boardname, variables):
  with open(boardname, 'r') as file:
      for line in file:

        valor = line.strip()

        for key in variables.keys():
            value =file.readline().strip()

            if value.isdigit() and len(value) == 1:
              variables[key] = {int(value)}

  return variables

#Definir restricciones para las columnas
def defColumnConstraints(idColumns,domain):
  columnConstraints=[]
  for id in idColumns:
    constraintVariables = [f"{id}{i}" for i in domain]
    columnConstraints.append(constraintVariables)
  return columnConstraints

#Definir restricciones para las filas
def defRowsConstraints(idColumns,domain):
  rowConstraints=[]
  for i in domain:
    constraintVariables = [f"{id}{i}" for id in idColumns]
    rowConstraints.append(constraintVariables)
  return rowConstraints

#Definir restricciones para los subcuadros 3x3
def defBoxesContraints(idColumns,domain):
    BoxesConstraints  = []
    for row_start in range(1, 10, 3):
        for col_start in range(0, 9, 3):
            variablesBox = []
            for i in range(3):
                for j in range(3):
                    row = row_start + i
                    col = idColumns.index(idColumns[col_start]) + j
                    variablesBox.append(f"{idColumns[col]}{row}")
            BoxesConstraints.append(variablesBox)
    return BoxesConstraints

#Función para aplicar consistencia, de manera que si se halla un valor fijo,
#este se elimina de las casillas correspondientes a las restricciones
def consistenceDifference(constraints, variablesDomain):
  changes = False

  #Se recorren todas las restricciones
  for constraint in constraints:

    #Por cada restriccion se deben recorrer las variables asociadas, buscando una variable con valor asociado (dominio con un unico valor)
    #y eliminar de los dominios de las otras variables asociadas en la restriccion el valor asociado a la variable actual.
    #Asi sucesivamente con todas y cada una de las variables de la restriccion.
    for var in constraint:

      #Si tiene valor asociado fijo
      if len(variablesDomain[var]) == 1:
        for varAux in constraint:

          #Se verifica que el valor no se elimine de si misma
          if varAux != var:
            oldDom = variablesDomain[varAux].copy()
            variablesDomain[varAux].discard (list(variablesDomain[var])[0])

            #Si se presentaron cambios en el dominio
            if variablesDomain[varAux] != oldDom:
              changes = True
  return changes

#Funcion generalizada para hallar cualquier conjunto de n celdas
#con un dominio común de n valores, y elimina esos valores de las demás celdas del grupo.
def equalDomains(all_constraints, vars):
    change = False

    for constraint in all_constraints:
      domain_groups = {}

      for var in constraint:
          dom = tuple(sorted(vars[var]))
          if len(dom) > 1:
              if not(dom in domain_groups):
                  domain_groups[dom] = []
              domain_groups[dom].append(var)

      for dom, variables in domain_groups.items():
          if len(dom) == len(variables):
              for var in constraint:
                  if not(var in variables):
                      old_domain = vars[var].copy()
                      vars[var] -= set(dom)
                      if vars[var] != old_domain:
                          change = True

    return change

#Funcion para iterar sobre las funciones de consistencia
#buscando resolver el sudoku
def iterations(Constraints, VarDoms, funciones):
    change = True
    iteration = 1

    #Siempre y cuando haya habido algun cambio
    while change:
        print(f"\n--- Iteration #{iteration} ---")
        change = False
        for funcion in funciones:
            print(f"Applying {funcion.__name__}...")
            change = funcion(Constraints, VarDoms) or change

        iteration += 1
        print()
        printSudoku(variables)
        if iteration > 20:
            break


#Imprimir el sudoku visualmente
def printSudoku(vars, idCols = "ABCDEFGHI"):
    for row in range(1, 10):
        if (row - 1) % 3 == 0 and row != 1:
            print("-" * 40)  # línea horizontal separadora

        for col_index, col in enumerate(idCols):
            if col_index % 3 == 0 and col_index != 0:
                print("|", end=' ')  # línea vertical separadora

            key = f"{col}{row}"
            val = vars[key]
            if len(val) == 1:
                print(f" {next(iter(val))} ", end=' ')
            else:
                print(" . ", end=' ')
        print()  # salto de línea al final de cada fila

def select_most_constrained_value(Vars, assignment):
    # Selecciona la variable no asignada con el dominio más pequeño
    unassigned = [v for v in Vars if v not in assignment]
    return min(unassigned, key=lambda v: len(Vars[v]))

def forward_checking(Vars, var, value, Constraints):
    inferences = {}
    for constraint in Constraints:
        if var in constraint:
            for neighbor in constraint:
                if neighbor != var and len(Vars[neighbor]) > 1:
                    if value in Vars[neighbor]:
                        if neighbor not in inferences:
                            inferences[neighbor] = Vars[neighbor].copy()
                        Vars[neighbor].remove(value)
                        if len(Vars[neighbor]) == 0:
                            return False  # Fallo temprano
    return True

def search_with_forward_checking(Vars, Constraints, assignment={}):
    if len(assignment) == len(Vars):
        return assignment  # Solución encontrada

    var = select_most_constrained_value(Vars, assignment)

    for value in list(Vars[var]):
        # Guardar estado actual para poder retroceder
        old_domains = {v: Vars[v].copy() for v in Vars}

        # Asignar el valor
        assignment[var] = value
        Vars[var] = {value}

        # Hacer forward checking
        fc_result = forward_checking(Vars, var, value, Constraints)

        if fc_result:
            result = search_with_forward_checking(Vars, Constraints, assignment)
            if result is not None:
                return result

        # Restaurar dominios si falla
        for v in Vars:
            Vars[v] = old_domains[v].copy()
        assignment.pop(var, None)

    return None  # No solution found

#Definiciones iniciales
#NOTA: cargar el archivo de sudoku sin ninguna edición, por favor NO quitar los espacios al incio y al final
idColumns = "ABCDEFGHI"
domain = set(range(1,10))
variables = definitions(idColumns, domain)
sudoku = tableConstruction("imposible.txt", variables)
print(sudoku)
printSudoku(variables)

#Restricciones
constraintVariables = defColumnConstraints(idColumns, domain) + defRowsConstraints(idColumns, domain) + defBoxesContraints(idColumns, domain)

#Llamado a las funciones
funtions = [consistenceDifference, equalDomains]
iterations(constraintVariables, variables, funtions)

solution = search_with_forward_checking(variables, constraintVariables)

# Mostrar solución
if solution:
    print("\nSolución encontrada:")
    printSudoku(variables)
    print(sudoku)
else:
    print("\nNo se encontró solución para este sudoku.")
