<!-- Build copy of draft-build.md, made by scripts/convert_markdown_script.py. Edit the original and convert again. -->
[INTRODUCCIÓN: El modelo que no entrena]

[B-ROLL: Página del artículo en arXiv, título y afiliación «Linkup, Paris». Corte a una captura de la ficha de RoBERTa, sin números inventados.]

NARRADOR: Si tomas RoBERTa-Large y lo entrenas como buscador al estilo SPLADE, el entrenamiento no arranca. Sin un ajuste en las puntuaciones iniciales, ese modelo no entrena [1].

Los buscadores por vectores sí han pasado a redes más nuevas. Los de palabras, no. Un equipo de Linkup, en París, explica por qué, y cómo se arregla con tres cambios [1].

[PARTE 1: Cómo busca un sistema de IA]

[B-ROLL: Un agente de IA consultando un archivo de documentos. Corte a una lista de trozos recuperados, y luego a la respuesta.]

NARRADOR: Hoy, cuando un agente de IA consulta un archivo, no se lee todos los documentos. Primero busca los trozos que parecen pertinentes. Esa primera búsqueda es el retriever, el buscador.

[VFX / GRÁFICO EN PANTALLA: Dos columnas. Izquierda, «Búsqueda densa»: un texto que se convierte en un punto en un espacio, y puntos cercanos. Derecha, «Búsqueda dispersa»: el mismo texto como una lista de palabras con un peso, dentro de un índice invertido.]

NARRADOR: Lo habitual es la búsqueda densa: cada texto se convierte en un vector, un punto en un espacio, y se buscan los más cercanos.

La búsqueda dispersa aprendida hace otra cosa. Representa cada texto como un conjunto de palabras con un peso. Es un índice invertido, como el de toda la vida, pero el modelo aprende qué términos importan y cuáles añadir. Según el artículo, eso permite coincidir con precisión en palabras raras, y buscar con la eficiencia de un índice [1].

[PARTE 2: El atasco]

[B-ROLL: El PDF del artículo, autores y fecha. Corte a nombres de modelos en pantalla: SPLADE, ModernBERT, Ettin, RoBERTa.]

NARRADOR: Durante años, la referencia ha sido la familia SPLADE, de Formal y sus coautores. Formal firma también este trabajo [1].

Mientras tanto, la búsqueda densa y la de interacción tardía, late interaction, del estilo ColBERT, han seguido mejorando con redes de base más nuevas (backbones), como ModernBERT o Ettin, y con datos más recientes. La dispersa no ha dado ese salto. Esos modelos no se transfieren bien a la receta de SPLADE [1].

Dos trabajos recientes apuntaban al vocabulario de los tokenizadores modernos, o a la escala de las cabezas del modelo [1]. Este artículo mira otra cosa: cómo están repartidas, al empezar, las puntuaciones que el modelo asigna a cada término del vocabulario. Esas puntuaciones se llaman logits [1].

[VFX / GRÁFICO EN PANTALLA: Figura 1, panel izquierdo, tal cual está en el paper. Distribución de logits en 200.000 pasajes de MS MARCO v1. Curvas: bert-base-uncased y distilbert-base-uncased más a la izquierda; modernbert-lateon y ettin-150m más a la derecha; roberta-large, la más desplazada. Pie: «Figura 1, izquierda. 200.000 pasajes de MS MARCO v1».]

NARRADOR: En el preentrenamiento habitual, sumar una constante a todas no cambia el resultado. El modelo no tiene por qué dejarlas en un rango concreto. Pero SPLADE convierte esas puntuaciones de una forma que sí depende de la escala. Si la mayoría salen positivas, el vector inicial es denso: se activan demasiados términos. Las diferencias se comprimen, y la señal para aprender se debilita [1].

La figura 1 lo mide en 200.000 pasajes de MS MARCO. Los BERT clásicos están más a la izquierda: menos puntuaciones positivas, una representación ya en parte dispersa. ModernBERT y Ettin están más a la derecha. RoBERTa-Large es el más desplazado. Y es con el que el entrenamiento no arranca, si no se corrige [1].

[PARTE 3: Tres cambios]

[CÁMARA EN PLANO MEDIO → PERSONAJE IA: el maniquí de Juan; el canal no sale a cámara] NARRADOR: Los autores proponen una receta de tres piezas, para esas redes modernas, sin una fase extra de preentrenamiento [1].

[PARTE 4: Cambio 1: desplazar las puntuaciones]

[VFX / GRÁFICO EN PANTALLA: Figura 1, panel derecho. Arriba, varias redes con y sin desplazamiento; rotular la nota del paper: «RoBERTa no entrena sin el desplazamiento». Abajo, ModernBERT con umbrales 15, 11, 9 y 0. No inventar medias ni un valor «+25».]

NARRADOR: La primera es el desplazamiento de logits. Antes de convertir las puntuaciones en pesos, se resta un umbral. La regla práctica: situarlo alrededor del percentil 99,9 de la distribución inicial. En ModernBERT y Ettin, usan 15. En RoBERTa-Large, 56. Con eso, la representación arranca más dispersa, y RoBERTa-Large vuelve a entrenar [1].

El truco no es nuevo: ya aparecía en el trabajo de Geng y Yang. Aquí muestran cómo fijar el umbral, y que basta para desbloquear redes que antes fallaban o rendían por debajo [1].

[PARTE 5: Cambio 2: limitar el abanico]

[VFX / GRÁFICO EN PANTALLA: Figura 2. Eje horizontal, no ceros por documento. Eje vertical, nDCG a diez en BEIR-13. Curvas de fan-out frente a solo regularizador. Rótulo: «f = 12». θ = 15 en todas las series, como en el paper.]

NARRADOR: La segunda es el control de abanico, el fan-out. Cada palabra de entrada solo puede activar, como mucho, doce términos del vocabulario, antes de agrupar el documento. Si se deja libre, cada posición puede disparar una cola larga de términos que no aportan, y eso mete ruido [1].

Un límite de 8 o de 12 gana a no poner ninguno. Y gana también a limitarse a apretar el regularizador de escasez: ese camino sí deja vectores más dispersos, pero pierde más calidad a igual escasez [1].

[PARTE 6: Cambio 3: plegar el vocabulario]

[VFX / GRÁFICO EN PANTALLA: La palabra «Paris» se abre en cuatro entradas: paris, Paris, Ġparis y ĠParis. Luego se pliegan en una. Rótulo: «ModernBERT: de unas 50.000 dimensiones a unas 34.000».]

NARRADOR: La tercera es el plegado del vocabulario. Los tokenizadores modernos, BPE a nivel de byte, distinguen mayúsculas de minúsculas, y si un token empieza palabra o va en medio. Una sola palabra, «Paris», puede ocupar hasta cuatro entradas: paris, Paris, y las dos con la marca de inicio de palabra [1].

En un buscador denso, esa redundancia queda en segundo plano. En uno disperso, un término de la consulta solo coincide con la forma exacta. El modelo tiene que repartir el peso entre variantes, o aceptar que se le escapen coincidencias [1].

Geng y Yang lo resolvían cambiando el vocabulario y reentrenando. Aquí lo resuelven solo en la salida, sin parámetros nuevos, en el entrenamiento y en la inferencia. En ModernBERT, el espacio pasa de unas 50.000 dimensiones a unas 34.000. Sin ese plegado, el resultado medio en BEIR-13 baja de 56,4 a 55,0 [1].

[PARTE 7: Los resultados]

[B-ROLL: Primera página del informe, «Linkup, Paris», y la línea del modelo en Hugging Face tal como aparece en el paper: Linkup-Platform/linkup-sparseup-embed-v1.]

NARRADOR: Aplican la receta a la red de base de LateOn, una variante de ModernBERT, y al conjunto abierto Embeddings-Fine-Tuning. El modelo se llama SPARSEUP. Lo firman Thibault Formal, Pierre Erbacher y Cosimo Rulli, de Linkup, en París, con contribución igual. Se publicó en arXiv el 6 de noviembre de 2026. Los pesos están en Hugging Face [1].

[VFX / GRÁFICO EN PANTALLA: Tabla 1, simplificada. Tres barras o una fila: «SPARSEUP, 56,4». «OS-NSE doc-v3, 54,6». «Mejor disperso público con vocabulario, menos de 150 millones de parámetros, según los autores». Pie: «nDCG a diez medio en BEIR-13, sin destilación».]

NARRADOR: En BEIR-13, trece pruebas de búsqueda, el nDCG a diez medio, que mide si lo pertinente sale arriba en la lista, es 56,4. Es, según los autores, el mejor resultado que conocen entre los encoders dispersos públicos de vocabulario, por debajo de 150 millones de parámetros. 1,8 puntos por encima del comparable más fuerte, OS-NSE doc-v3. Sin destilación [1].

[VFX / GRÁFICO EN PANTALLA: Misma red y mismos datos. «SPARSEUP, 56,4». «DenseOn, 57,9». «LateOn, 58,9». Debajo, un segundo bloque: «BEIR descontaminada: SPARSEUP 57,5. DenseOn 57,7».]

NARRADOR: Como comparten red y datos con DenseOn y LateOn, la comparación es justa. SPARSEUP queda a 1,5 puntos de DenseOn, que saca 57,9, y a 2,5 de LateOn, que saca 58,9 [1].

Hay un matiz: el entrenamiento incluye particiones de algunas colecciones de evaluación. En la BEIR descontaminada, sin las consultas que ya estaban en el entrenamiento, SPARSEUP saca 57,5 y DenseOn 57,7. Quedan casi empatados [1].

[VFX / GRÁFICO EN PANTALLA: Tabla 2, solo las cifras que se dicen. «BRIGHT-Pro, nDCG a diez: SPARSEUP 34,5. DenseOn 29,6. +4,9, sin destilación». «FreshStack, alfa-nDCG a diez: 23,3 frente a 19,6». «Legal y finanzas, MTEB (AILA-casedocs, FinQA, FinanceBench): 50,3 frente a 49,9, sin destilación». «ChemTEB: recall a 100, 97,5 frente a 96,9. nDCG a diez: 70,8 frente a 76,4».]

NARRADOR: En BRIGHT-Pro, una batería de búsqueda que exige razonamiento, saca 34,5 de nDCG a diez, 4,9 puntos por encima de DenseOn, sin destilación [1]. En FreshStack, documentos técnicos, 23,3 frente a 19,6 en alfa-nDCG a diez [1].

En el bloque legal y financiero de MTEB obtiene, sin destilación, el mejor nDCG a diez de esa comparación, 50,3, frente a 49,9 de DenseOn [1]. En química, ChemTEB, gana en exhaustividad, el recall a cien documentos, con 97,5 frente a 96,9. No gana en nDCG: DenseOn saca 76,4 y SPARSEUP, 70,8 [1].

[PARTE 8: Los límites]

[VFX / GRÁFICO EN PANTALLA: LoTTE Forum y LoTTE Search. SPARSEUP por debajo de DenseOn, LateOn y SlideOn, con las cifras de la tabla 2 si se rotulan, sin inventar la causa.]

NARRADOR: No gana en todas partes. En LoTTE, tanto en foros como en búsqueda, queda por detrás de los modelos densos y de interacción tardía [1]. El artículo no explica el motivo.

[VFX / GRÁFICO EN PANTALLA: Figura 4, ejemplo del café y el «cleaver». El token «cle» emite «cle», «cleavage», «le», «cre», «ce», «Cole» y «cane». Pie: «Figura 4. Pesos disparatados, wacky weights». No dibujar una cadena «cleaver → cle → cleavage».]

NARRADOR: Las representaciones tampoco son limpias. Como el tokenizador parte las palabras en subpiezas, a veces se activan términos que no vienen a cuento. En un ejemplo, el trozo «cle», de «cleaver», dispara también «cleavage», «Cole» o «cane». Son los llamados wacky weights, pesos disparatados. El abanico lo mitiga en parte, pero no lo quita. Las representaciones se ven menos limpias que las de Splade-v3, dicen, aunque el modelo rinde más [1].

El punto de partida también cuenta. Si arrancan de un ModernBERT sin el preentrenamiento de LateOn, el resultado en BEIR-13 baja a 54,3 [1].

[CÁMARA EN PLANO MEDIO → PERSONAJE IA: el maniquí de Juan; el canal no sale a cámara] NARRADOR: El dato de velocidad hay que tomarlo con lo que hay. El artículo afirma que recupera en menos de un milisegundo por consulta, con el motor Seismic. No detalla el hardware, el tamaño de la colección ni el protocolo de esa medida [1].

Tampoco es el único enfoque disperso reciente. SlideOn supera a DenseOn y a SPARSEUP en BEIR-13, con más dimensiones distintas de cero [1]. Laconic, con alrededor de mil millones de parámetros, le saca 2,3 puntos [1].

[PARTE 9: Para qué puede servir]

[VFX / GRÁFICO EN PANTALLA: «Con destilación. BEIR-13: solo +0,1». «Legal y finanzas: de 50,3 a 52,6».]

NARRADOR: Si añaden destilación a partir de un reranker, el salto en BEIR-13 es de solo una décima. Fuera de dominio sí se nota: en legal y finanzas, el nDCG a diez sube de 50,3 a 52,6 [1].

El artículo no prescribe usos. Sí muestra, a igualdad de datos y de red, que esta búsqueda aguanta el tipo en la búsqueda general y gana en varias pruebas técnicas, jurídicas y financieras. Encaja con lo que recuerdan al principio: coincidir con precisión en palabras raras [1].

[CÁMARA EN PLANO MEDIO → PERSONAJE IA: el maniquí de Juan; el canal no sale a cámara] NARRADOR: Un ejemplo, solo ilustrativo, no una afirmación del artículo. En derecho, el nombre de una sentencia. En finanzas, el ticker de una empresa. Son términos que o están o no están. Un vector denso puede aproximarlos. Un índice de palabras puede exigir la coincidencia exacta.

Para un agente que lanza muchas subconsultas sobre un corpus, el tiempo de cada búsqueda cuenta. El artículo habla de menos de un milisegundo [1].

[CONCLUSIÓN: Dos décimas]

[VFX / GRÁFICO EN PANTALLA: Dos cifras solas. «BEIR descontaminada. SPARSEUP 57,5. DenseOn 57,7». Debajo, más pequeño: «BRIGHT-Pro, sin destilación: 34,5 frente a 29,6».]

[CÁMARA EN PLANO CORTO → PERSONAJE IA: el maniquí de Juan; el canal no sale a cámara] NARRADOR: En la BEIR descontaminada, con los mismos datos y la misma red de base, la diferencia con la búsqueda densa es de dos décimas. En BRIGHT-Pro y en FreshStack, queda por delante del modelo denso entrenado con los mismos datos. Con la receta habitual de SPLADE, esas redes modernas rendían por debajo o ni siquiera entrenaban. Con esta, el artículo las convierte en encoders dispersos eficaces.
