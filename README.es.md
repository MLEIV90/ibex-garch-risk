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
  GJR ≈ 0,24 vs 0,18): las caídas en EE.UU. elevan más la volatilidad.
- El **S&P 500 tiene colas más pesadas** (ν de la t ≈ 5 vs ≈ 7 del IBEX).
- La volatilidad es muy persistente en ambos (α+β ≈ 0,92–0,98).

**Validación de riesgo (Etapas 4–5):**
- El eje de la Etapa 5 es un **backtest out-of-sample genuino**: ventana
  expandible, reajustada cada 5 días hábiles, pronosticando un día hacia
  adelante — no un modelo ajustado una sola vez sobre toda la muestra y evaluado
  sobre los mismos datos con los que se ajustó.
- Out-of-sample, **solo 2 de 8** combinaciones (índice, modelo, nivel de
  confianza) pasan limpiamente la cobertura condicional: S&P 500 con GARCH al
  95%, IBEX 35 con GARCH al 99%.
- **GARCH vs. EWMA da un resultado genuinamente mixto out-of-sample, no una
  victoria limpia de GARCH**: GARCH está mejor calibrado al 95% en ambos
  índices, pero al 99% el resultado del S&P 500 se **invierte** — EWMA pasa
  donde GARCH falla.
- **El hallazgo más importante**: el IBEX 35 muestra un agrupamiento de
  violaciones (*clustering*) estadísticamente significativo out-of-sample (test
  de Christoffersen) que un backtest naive, ajustado sobre toda la muestra, no
  detectó — una demostración concreta de por qué el sesgo de anticipación
  (*look-ahead bias*) es peligroso, no solo una advertencia teórica.

**Conclusión honesta:** el VaR paramétrico —incluso con GARCH, t de Student, y
un test genuinamente out-of-sample— no está completamente validado al nivel del
99%, y qué modelo "gana" depende del índice y del nivel de confianza. Es un
hallazgo de validación genuino, no un fracaso: señala al **Expected Shortfall o
a un enfoque EVT** como más prudentes para la cola, y demuestra concretamente
por qué **el testeo out-of-sample, no solo el ajuste in-sample, es el verdadero
objetivo de la validación de modelos**. El proyecto reporta esto
deliberadamente, en vez de forzar un "el modelo pasa".

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
