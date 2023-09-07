# Dudas TP1

- ¿Como definir la probabilidad de distracción y en que debería afectar la misma? (se nos ocurrió quizas buscar la cantidad de choques en la gral paz en un período de tiempo y ajustar el valor de la distracción para obtener resultados similares a esa distribución pero creemos que tiene mas que ver con lo último que estamos viendo que esta enfocado a otro tipo de problemas).
- Como hacemos que vayan ingresando los agentes al carril, ¿con que valores de velocidad, aceleración deberían entrar al carril? ¿como definimos si entra una persona o no?
- Usando el criterio de "seguridad": estar a 2s del de adelante, ¿qué fórmula/función usamos para ver cuanto es el delta de la aceleración? 


# Notas

- Manejo de choques
    - ¿Tiene sentido separar choques leves de choques fuertes?
    - ¿Que diferencias hay?
        - Tiempo que se frena el carril, ¿siguen avanzando o "se corren a la banquina"?

- Tuning de parametros
    - Cuanto ruido es razonable en aceleración.
    - ¿Tiene sentido insertar ruido en velocidad y/o posición?

- Tiempo
    - Un día (86400 segundos de time_limit) tarda mucho en correr y nosotros querríamos hacer promedios de días, ¿cómo podemos hacer fracciones mas cortas de tiempo y que sea representativo?
    
- Curvas
    - ¿Bajar velocidad?