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
   y Christoffersen implementados desde cero, más el marco semáforo de Basilea,
   con una lectura honesta de dónde pasa y falla cada modelo.

## Hallazgos principales

**Volatilidad cross-market (Etapa 3):**
- El **efecto apalancamiento es más fuerte en el S&P 500** que en el IBEX (γ de
  GJR ≈ 0,24 vs 0,18): las caídas en EE.UU. elevan más la volatilidad.
- El **S&P 500 tiene colas más pesadas** (ν de la t ≈ 5 vs ≈ 7 del IBEX).
- La volatilidad es muy persistente en ambos (α+β ≈ 0,92–0,98).

**Validación de riesgo (Etapas 4–5):**
- Al 99%, **GARCH queda en zona verde de Basilea** en ambos índices (≈3,1 y ≈3,9
  excepciones escaladas por 250 días) mientras el **baseline EWMA queda en
  amarilla** (≈5,3–5,6): la complejidad del modelo se justifica.
- **Solo una de ocho combinaciones (índice, modelo, nivel) pasa limpiamente** la
  cobertura condicional: IBEX 35 con GJR-GARCH al 99% (Kupiec p = 0,24).
- La mayoría de las fallas son por **exceso de violaciones, no por agrupamiento**:
  los modelos reaccionan bien a los cambios de régimen, pero el **VaR paramétrico
  subestima el riesgo de cola**, sobre todo al 95%.

**Conclusión honesta:** el VaR paramétrico —incluso con GARCH y t de Student—
subestima sistemáticamente el riesgo en esta muestra. Es un hallazgo de
validación genuino, no un fracaso: señala al **Expected Shortfall o a un enfoque
EVT** como más prudentes para la cola. El proyecto reporta esto deliberadamente,
en vez de forzar un "el modelo pasa".

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
