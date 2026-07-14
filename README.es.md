# IBEX 35 GARCH Risk

**🇪🇸 Español** · [🇬🇧 English](README.md)

**Validación** de un modelo de riesgo de mercado sobre el índice español IBEX 35,
usando el framework ARIMA–GARCH. El objetivo no es rendimiento de trading sino una
pregunta de riesgo: **¿qué modelo de volatilidad produce el Value-at-Risk más
confiable, y sobrevive a un backtesting formal?** Se incluye el S&P 500 como
benchmark comparativo, lo que lo convierte en un estudio cross-market.

Proyecto econométrico con enfoque de Risk Analytics / FRM: cada etapa combina
teoría con la interpretación de los resultados reales.

## Qué hace

Un pipeline de cinco etapas, un notebook por etapa, desde los precios crudos hasta
la validación regulatoria de las medidas de riesgo:

1. **Datos y exploración** (`notebooks/01_exploration.ipynb`) — retornos
   logarítmicos y los hechos estilizados (agrupamiento de volatilidad, colas
   pesadas, no-normalidad) que motivan todo lo demás.
2. **Estacionariedad y media** (`notebooks/02_stationarity_arima.ipynb`) — tests
   ADF/KPSS, modelo de media ARIMA, y el puente a GARCH: los retornos no tienen
   autocorrelación en la media, pero sus residuos al cuadrado sí.
3. **La familia GARCH** (`notebooks/03_garch_family.ipynb`) — GARCH(1,1),
   GJR-GARCH y EGARCH con innovaciones t de Student; persistencia, efecto
   apalancamiento y peso de colas, validado sobre residuos estandarizados.
4. **VaR y Expected Shortfall** (`notebooks/04_var_es.ipynb`) — VaR paramétrico
   dinámico y ES desde los modelos preferidos, comparados contra un baseline
   EWMA/RiskMetrics.
5. **Backtesting de VaR** (`notebooks/05_var_backtesting.ipynb`) — tests de Kupiec
   y Christoffersen implementados desde cero, aplicados tanto a un ajuste naive
   in-sample como a un **backtest out-of-sample genuino con ventana expandible**,
   más el marco semáforo de Basilea, con una lectura honesta de dónde pasa y
   falla cada modelo.

## Hallazgos principales

**Volatilidad cross-market (Etapa 3):**
- El **efecto apalancamiento es más fuerte en el S&P 500** que en el IBEX (γ de
  GJR ≈ 0,23 vs 0,19): las caídas en EE.UU. elevan más la volatilidad.
- El **S&P 500 tiene colas más pesadas** (ν de la t ≈ 5,3 vs ≈ 7,3 del IBEX).
- La volatilidad es muy persistente en ambos (α+β ≈ 0,92–0,98).

**Validación de riesgo (Etapas 4–5):**
- El eje de la Etapa 5 es un **backtest out-of-sample genuino**: ventana
  expandible, reajustada cada 5 días hábiles, pronosticando un día hacia
  adelante — no un modelo ajustado una sola vez sobre toda la muestra y evaluado
  sobre los mismos datos con los que se ajustó.
- Out-of-sample, el resultado se divide **por índice, no por modelo**: **las 4
  celdas del S&P 500** (GARCH y EWMA, 95% y 99%) pasan limpiamente la cobertura
  condicional, mientras que **las 4 celdas del IBEX 35 fallan** — todas por la
  misma razón.
- **El hallazgo más importante**: cada celda del IBEX 35 que falla tiene un
  *buen* conteo de violaciones (Kupiec p hasta 0,99) pero un **agrupamiento de
  violaciones estadísticamente significativo** (test de independencia de
  Christoffersen) — el modelo acierta la frecuencia promedio de días malos pero
  reacciona demasiado lento una vez que un cambio de régimen está en marcha. Un
  backtest naive, ajustado sobre toda la muestra, queda al borde de ocultar
  exactamente este problema.
- **El marco semáforo de Basilea no puede ver esta falla en absoluto**: el VaR
  al 99% de IBEX 35 con GARCH cae cómodamente en la zona verde de Basilea (tasa
  de violación ≈1,01%, casi exactamente la nominal) — la misma celda que falla
  la cobertura condicional por completo al revisar la independencia.

**Conclusión honesta:** el VaR paramétrico —incluso con GARCH, t de Student, y
un test genuinamente out-of-sample— se valida limpiamente para un mercado
(S&P 500) y falla para otro (IBEX 35), por una razón específica e
identificable (agrupamiento de violaciones, no una cobertura mal calibrada).
Es un hallazgo de validación genuino, no un fracaso: señala al **Expected
Shortfall, una especificación de varianza que reaccione más rápido, o un
enfoque EVT** como respuestas más prudentes, y demuestra concretamente por qué
**el testeo out-of-sample —incluyendo la independencia de las violaciones, no
solo su conteo— es el verdadero objetivo de la validación de modelos**. El
proyecto reporta esto deliberadamente, en vez de forzar un "el modelo pasa".

## Por qué no es otro repo genérico de ARIMA-GARCH

Los notebooks genéricos de "ajusto GARCH y grafico la volatilidad" abundan y son
casi siempre descriptivos o de trading. Este juega otro partido: **validación de
modelos con enfoque regulatorio / FRM**, sobre un **mercado no anglosajón**, con
**backtesting formal de VaR** y un **baseline honesto (EWMA)** — las partes que la
mayoría de los repos omiten. El hilo conductor con el resto de mi portfolio: un
proyecto de credit scoring validó un modelo de PD; este valida un modelo de VaR.

## Notas metodológicas

- **Precios ajustados** (`auto_adjust=True`): corregidos por splits/dividendos
  para evitar volatilidad artificial. ^IBEX y ^GSPC son índices de precio,
  correctos para modelar volatilidad.
- **Sin sesgo de supervivencia:** analizar la serie del índice (no sus
  componentes) hereda una historia que ya contabilizó a las empresas que
  salieron.
- **Solo días de trading comunes:** el IBEX 35 y el S&P 500 no comparten
  calendario de festivos; rellenar los huecos hacia adelante (*forward-fill*)
  fabricaría retornos cero artificiales para el mercado que estaba cerrado.
  Todos los notebooks conservan solo los días en que ambos mercados operaron
  (`dropna(how="any")`), así cada retorno es un movimiento de precio real.
- **Reproducible por diseño:** cada notebook usa una fecha de corte fija
  (`2026-07-01`) en vez de "hoy", para que los resultados documentados no
  cambien cada vez que se re-ejecuta un notebook. Los warnings se filtran de
  forma puntual (dos mensajes nombrados y conocidos como benignos) en vez de
  silenciarse en bloque, así que warnings genuinos de convergencia o
  numéricos seguirían apareciendo.
- **Ventana de ~10 años:** amplia para GARCH, incluye el estrés del COVID-2020;
  regímenes más viejos excluidos deliberadamente. Un análisis de sensibilidad
  5/10/15 años es una extensión de robustez anotada.
- **Validación out-of-sample:** la Etapa 5 reajusta GARCH sobre una ventana
  expandible (≈60% de entrenamiento inicial, reajuste cada 5 días hábiles) en
  vez de depender de un único ajuste sobre toda la muestra, que de otro modo
  dejaría al modelo "ver" el futuro —incluido el COVID-2020— antes de hacer el
  backtest sobre él.

## Uso

```bash
pip install -r requirements.txt
jupyter lab
```

Cada notebook es autocontenido: descarga sus propios datos con `yfinance` y se
corre de principio a fin.

## Stack

Python · pandas · numpy · scipy · statsmodels · arch (Kevin Sheppard) · pmdarima
· yfinance · matplotlib — econometría pura: ARIMA, GARCH/EGARCH/GJR, VaR,
Expected Shortfall, Kupiec y Christoffersen.

## Limitaciones y extensiones posibles

- El VaR paramétrico subestima la cola; un tratamiento con **EVT / Expected
  Shortfall** sería el paso natural siguiente.
- **Análisis de sensibilidad** por longitud de ventana (5/10/15 años, incluyendo
  2008).
- Un **challenger de machine learning** opcional (ej. LSTM o gradient boosting
  sobre volatilidad realizada) como comparación honesta — fuera del núcleo para
  no diluir el foco de validación de riesgo.
