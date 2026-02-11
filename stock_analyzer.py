import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(prices, window=14):
    """
    Calcula el RSI (Relative Strength Index)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    # Avoid division by zero
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calcula el MACD (Moving Average Convergence Divergence)
    """
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def download_stock_data(symbol, period='1y'):
    """
    Descarga datos de una acción usando yfinance
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error descargando datos para {symbol}: {str(e)}")
        return None

def calculate_bollinger_bands(prices, window=20, num_std=2):
    """
    Calcula las Bandas de Bollinger
    """
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return sma, upper_band, lower_band

def create_technical_chart(symbols, period='1y'):
    """
    Crea gráfico técnico con múltiples indicadores
    """
    if not symbols:
        st.warning("Por favor selecciona al menos una acción")
        return

    # Crear subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Precio y Media Móvil 21', 'RSI', 'MACD', 'Volumen'),
        row_heights=[0.5, 0.2, 0.2, 0.1]
    )

    colors = px.colors.qualitative.Set1

    for i, symbol in enumerate(symbols):
        data = download_stock_data(symbol, period)
        if data is None or data.empty:
            continue

        color = colors[i % len(colors)]

        # Calcular indicadores
        ma21 = data['Close'].rolling(window=21).mean()
        rsi = calculate_rsi(data['Close'])
        macd, signal_line, histogram = calculate_macd(data['Close'])
        sma, upper_band, lower_band = calculate_bollinger_bands(data['Close'])

        # Gráfico de precios con media móvil y bandas de Bollinger
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                name=f'{symbol} - Precio',
                line=dict(color=color, width=2),
                opacity=0.8
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ma21,
                name=f'{symbol} - MA21',
                line=dict(color=color, width=1, dash='dash'),
                opacity=0.6
            ),
            row=1, col=1
        )

        # Bandas de Bollinger
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=upper_band,
                name=f'{symbol} - BB Superior',
                line=dict(color=color, width=1, dash='dot'),
                opacity=0.3,
                showlegend=False
            ),
            row=1, col=1
        )

        # Convert color to rgba for fill
        if color.startswith('#'):
            # Hex color format
            rgb = px.colors.hex_to_rgb(color)
            fillcolor = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.1)'
        elif color.startswith('rgb'):
            # Already in rgb format, convert to rgba
            fillcolor = color.replace('rgb', 'rgba').replace(')', ', 0.1)')
        else:
            # Named color or other format
            fillcolor = color

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=lower_band,
                name=f'{symbol} - BB Inferior',
                line=dict(color=color, width=1, dash='dot'),
                opacity=0.3,
                fill='tonexty',
                fillcolor=fillcolor,
                showlegend=False
            ),
            row=1, col=1
        )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=rsi,
                name=f'{symbol} - RSI',
                line=dict(color=color, width=2),
                opacity=0.8
            ),
            row=2, col=1
        )

        # MACD
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=macd,
                name=f'{symbol} - MACD',
                line=dict(color=color, width=2),
                opacity=0.8
            ),
            row=3, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=signal_line,
                name=f'{symbol} - Señal',
                line=dict(color=color, width=1, dash='dash'),
                opacity=0.6
            ),
            row=3, col=1
        )

        # Histograma MACD
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=histogram,
                name=f'{symbol} - Histograma',
                marker_color=color,
                opacity=0.3,
                showlegend=False
            ),
            row=3, col=1
        )

        # Volumen
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name=f'{symbol} - Volumen',
                marker_color=color,
                opacity=0.5
            ),
            row=4, col=1
        )

    # Agregar líneas horizontales para RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)

    # Configurar layout
    fig.update_layout(
        title="Análisis Técnico de Acciones",
        xaxis_title="Fecha",
        height=800,
        showlegend=True,
        template="plotly_white"
    )

    # Configurar ejes Y
    fig.update_yaxes(title_text="Precio ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Volumen", row=4, col=1)

    return fig

def main():
    st.set_page_config(
        page_title="Analizador de Acciones",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 Analizador Técnico de Acciones")
    st.markdown("Análisis de acciones con media móvil de 21 períodos, RSI, MACD y más indicadores técnicos")

    # Sidebar para configuración
    st.sidebar.header("Configuración")

    # Input para símbolos
    symbols_input = st.sidebar.text_input(
        "Símbolos de acciones (separados por comas)",
        value="AAPL,MSFT,GOOGL",
        help="Ejemplo: AAPL,MSFT,GOOGL,TSLA"
    )

    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

    # Selector de período
    period = st.sidebar.selectbox(
        "Período de análisis",
        options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=3,
        help="Período de tiempo para el análisis"
    )

    # Botón para actualizar
    if st.sidebar.button("🔄 Actualizar Datos", type="primary"):
        st.rerun()

    # Información sobre los símbolos seleccionados
    if symbols:
        st.sidebar.markdown("### Acciones Seleccionadas:")
        for symbol in symbols:
            st.sidebar.markdown(f"• {symbol}")

    # Crear y mostrar el gráfico
    if symbols:
        with st.spinner('Descargando datos y generando gráficos...'):
            fig = create_technical_chart(symbols, period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        # Mostrar estadísticas resumidas
        st.header("📊 Estadísticas Resumidas")

        stats_data = []
        for symbol in symbols:
            data = download_stock_data(symbol, period)
            if data is not None and not data.empty:
                current_price = data['Close'].iloc[-1]
                ma21 = data['Close'].rolling(window=21).mean().iloc[-1]
                rsi_current = calculate_rsi(data['Close']).iloc[-1]

                # Calcular dispersión (desviación estándar relativa)
                std_21 = data['Close'].rolling(window=21).std().iloc[-1]
                dispersion = (std_21 / ma21) * 100 if ma21 != 0 else 0

                # Calcular cambio porcentual
                if len(data) > 1:
                    price_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                else:
                    price_change = 0.0

                stats_data.append({
                    'Símbolo': symbol,
                    'Precio Actual': f"${current_price:.2f}",
                    'MA21': f"${ma21:.2f}",
                    'Dispersión (%)': f"{dispersion:.2f}%",
                    'RSI': f"{rsi_current:.1f}",
                    'Cambio Diario (%)': f"{price_change:+.2f}%"
                })

        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)

        # Explicación de indicadores
        with st.expander("ℹ️ Explicación de Indicadores"):
            st.markdown("""
            **Media Móvil 21 (MA21)**: Promedio de los últimos 21 períodos. Útil para identificar tendencias.

            **Dispersión**: Desviación estándar relativa de los últimos 21 períodos. Mide la volatilidad del precio.

            **RSI (Relative Strength Index)**:
            - Valores > 70: Posible sobrecompra
            - Valores < 30: Posible sobreventa
            - Rango ideal: 30-70

            **MACD (Moving Average Convergence Divergence)**:
            - Línea MACD por encima de la línea de señal: Momentum alcista
            - Línea MACD por debajo de la línea de señal: Momentum bajista

            **Bandas de Bollinger**:
            - Precio cerca de la banda superior: Posible sobrecompra
            - Precio cerca de la banda inferior: Posible sobreventa
            """)

    else:
        st.info("👆 Ingresa símbolos de acciones en la barra lateral para comenzar el análisis")

if __name__ == "__main__":
    main()