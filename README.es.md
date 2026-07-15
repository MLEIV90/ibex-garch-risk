# IBEX 35 GARCH Risk

**🇪🇸 Español** · [🇬🇧 English](README.md)

**Validación** de un modelo de riesgo de mercado sobre el índice español IBEX 35
con el framework ARIMA–GARCH. El objetivo no es rendimiento de trading sino una
pregunta de riesgo: **¿este modelo de VaR habría funcionado en tiempo real, y
sobrevive a un backtesting formal?** Se incluye el S&P 500 como benchmark, lo que
lo convierte en un estudio cross-market.

Proyecto econométrico con enfoque de Risk Analytics / FRM: cada etapa combina
teoría con la interpretación de los resultados reales, y las limitaciones se
declaran explícitamente.

## Qué hace

Cinco etapas, un notebook cada una, desde los precios crudos hasta la validación
regulatoria:

1. **Datos y exploración** (`01_exploration.ipynb`) — retornos logarítmicos y los
   hechos estilizados (agrupamiento de volatilidad, colas pesadas, no-normalidad)
   que motivan todo lo demás.
2. **Estacionariedad y media** (`02_stationarity_arima.ipynb`) — ADF/KPSS, modelo
   de media ARIMA, y el puente a GARCH: los retornos no tienen autocorrelación en
   la media, pero sus residuos al cuadrado sí.
3. **La familia GARCH** (`03_garch_family.ipynb`) — GARCH(1,1), GJR-GARCH y
   EGARCH con innovaciones t de Student; persistencia, apalancamiento y peso de
   colas, validado sobre residuos estandarizados.
4. **VaR y Expected Shortfall** (`04_var_es.ipynb`) — VaR paramétrico dinámico y
   ES, contra un baseline EWMA/RiskMetrics (mismo cuantil t, para que la
   comparación aísle el método de volatilidad).
5. **Backtesting de VaR** (`05_var_backtesting.ipynb`) — Kupiec y Christoffersen
   implementados desde cero, sobre un backtest **out-of-sample** genuino (ventana
   expansiva, modelo reajustado solo con datos del pasado).

## Metodología: el backtest out-of-sample

Los resultados principales vienen de un backtest que simula lo que un gestor de
riesgo realmente habría hecho: el primer 60% de la muestra es la ventana de
estimación inicial; para cada uno de los 995 días restantes el modelo se
reestima **solo con datos hasta t−1** y produce un pronóstico de volatilidad a un
paso (reajuste cada 5 días hábiles, un compromiso computacional documentado).
También se reporta un backtest in-sample —etiquetado explícitamente como
sesgado— para hacer visible la diferencia.

## Hallazgos principales

**Volatilidad cross-market (Etapa 3, 2.486 obs):**
- El **apalancamiento es más fuerte en el S&P 500** (γ de GJR = 0,233) que en el
  IBEX (0,189).
- El **S&P tiene colas más pesadas** (ν ≈ 5,4 vs ≈ 7,6 del IBEX).
- La **volatilidad es más persistente en el S&P** (0,97–0,98 vs 0,92–0,93).
- Preferidos por AIC: **GJR-GARCH para el IBEX, EGARCH para el S&P** — los
  modelos asimétricos superan al GARCH simple en ambos mercados.

**Validación de riesgo (Etapa 5, out-of-sample, 995 obs con el split 60/40
principal):**
- **Las cuatro combinaciones del S&P 500 pasan** la cobertura condicional; **las
  cuatro del IBEX 35 fallan.** El resultado se separa por *mercado*, no por
  modelo — **pero este veredicto solo se sostiene en un periodo de test
  tranquilo, ver más abajo.**
- **El IBEX falla por agrupamiento, no por cantidad.** El IBEX con GARCH al 99%
  tiene una cobertura incondicional casi perfecta (10 violaciones vs 10
  esperadas; Kupiec p = 0,987, el mejor valor de la tabla) pero falla el test de
  independencia (p = 0,003): sus violaciones llegan en racimos. El modelo acierta
  *cuántas* veces fallará, pero no *cuándo*.
- El GARCH produce menos violaciones que el EWMA en ambos mercados, pero en el
  IBEX ni el GARCH logra dispersarlas: el problema del mercado español no se
  resuelve cambiando el modelo de volatilidad.
- **Sometido a estrés contra su propia metodología, dos veces.** El backtest
  principal reajusta cada 5 días y usa un split 60/40, ambas elecciones
  arbitrarias, así que ambas se sometieron a estrés: (1) frecuencia de reajuste
  a 1, 10 y 20 días — la tendencia al agrupamiento del IBEX sobrevive a cada
  frecuencia (la p de independencia nunca supera 0,085; la del S&P nunca baja
  de 0,075), pero el veredicto exacto de aprobado/reprobado es sensible a la
  frecuencia en ambos mercados; (2) **el propio split train/test — la prueba de
  robustez más importante de este proyecto.**

**El resultado principal de arriba es un hallazgo de periodo tranquilo, y eso
importa enormemente.** El periodo de test del split 60/40 (desde mediados de
2022) excluye el COVID-2020, que cae dentro de la ventana de *entrenamiento* en
su lugar. Repetir el mismo backtest con una ventana inicial lo bastante pequeña
para meter el COVID-2020 en el periodo de test hace que **fallen las 8
combinaciones** — incluidas las cuatro del S&P 500 que antes pasaban limpio — y
el modo de fallo del S&P pasa a ser cobertura incondicional genuina (tasas de
violación cercanas al doble de lo nominal al 99%), no solo agrupamiento. Lo que
sí sobrevive a un periodo de test que incluye una crisis real: el problema de
agrupamiento del IBEX (la independencia falla en todos los splits probados, con
o sin COVID) y la ausencia de ese problema en el S&P (la independencia nunca
falla, ni siquiera durante el COVID) — esa diferencia cross-market específica es
el único resultado que sobrevive a todas las pruebas de este proyecto.

**La conclusión de un validador:** el VaR paramétrico con GARCH del S&P 500 está
validado **en mercados tranquilos**, pero no (en cobertura incondicional) una vez
que una crisis real entra en el periodo de test; el IBEX 35 no está validado en
ningún régimen, y falla específicamente porque sus violaciones se agrupan — el
modo de fallo más peligroso que puede tener un modelo de riesgo (fallar
repetidamente durante una crisis real). Un backtest que nunca prueba un periodo
de estrés no puede hacer esta distinción, y el "aprobado" de un modelo de riesgo
carece casi de sentido sin saber si su ventana de test contenía uno. Líneas de
acción recomendadas: modelos de cambio de régimen, Expected Shortfall, o un
tratamiento EVT de la cola.

## Por qué no es otro repo genérico de ARIMA-GARCH

Los notebooks de "ajusto GARCH y grafico la volatilidad" abundan y son casi
siempre descriptivos o de trading. Este juega otro partido: **validación de
modelos con enfoque regulatorio / FRM**, sobre un **mercado no anglosajón**, con un
**backtest out-of-sample genuino**, tests estadísticos implementados desde cero, y
un **benchmark EWMA justo** — las partes que la mayoría de los repos omite. El hilo
conductor con el resto de mi portfolio: un proyecto de credit scoring validó un
modelo de PD; este valida un modelo de VaR.

## Notas metodológicas

- **Precios ajustados** (`auto_adjust=True`): corregidos por splits/dividendos.
  ^IBEX y ^GSPC son índices de precio, correctos para modelar volatilidad.
- **Sin sesgo de supervivencia:** analizar la serie del índice (no sus
  componentes) hereda una historia que ya contabilizó a las empresas que
  salieron.
- **Solo días de negociación comunes:** los dos mercados se alinean sobre sesiones
  compartidas en lugar de rellenar hacia adelante, lo que crearía retornos cero
  artificiales.
- **Ventana fija** hasta 2026-07-01 (~10 años, 2.486 obs) para que los resultados
  sean reproducibles; incluye el estrés del COVID-2020 dentro de la muestra,
  aunque el split OOS 60/40 principal lo deja en entrenamiento y no en el
  periodo de test — ver Etapa 5, Sección 13.

## Limitaciones

Declaradas explícitamente en los notebooks: horizonte de 1 día únicamente (sin
VaR multi-día); univariado (sin riesgo de portafolio ni dependencia de colas vía
cópulas); t de Student simétrica (una skew-t podría ajustar mejor los retornos
accionarios); el VaR paramétrico subestima la cola extrema (EVT la modelaría
directamente); ventana única de 10 años (la sensibilidad 5/10/15 años queda como
brecha de robustez abierta, aunque la Sección 13 la explora parcialmente
variando dónde cae el corte train/test dentro de esa ventana); tanto la
frecuencia de reajuste (1/5/10/20 días) como el split train/test (35/50/60%,
con y sin crisis en el periodo de test) se sometieron a estrés — ver Etapa 5,
Secciones 12-13 — en vez de quedar como supuestos sin probar; y el VaR es una
medida estadística — excluye riesgo de liquidez y de modelo.

## Uso

```bash
pip install -r requirements.txt
jupyter lab
```

Las funciones compartidas viven en `src/utils.py`; cada notebook importa de allí
y se corre de principio a fin.

## Stack

Python · pandas · numpy · scipy · statsmodels · arch (Kevin Sheppard) · pmdarima
· yfinance · matplotlib — ARIMA, GARCH/EGARCH/GJR, VaR, Expected Shortfall,
Kupiec y Christoffersen.
