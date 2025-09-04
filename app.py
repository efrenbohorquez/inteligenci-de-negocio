
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página de Streamlit
st.set_page_config(layout="wide", page_title="Análisis de Ventas")

# Título principal de la aplicación
st.title("Dashboard de Análisis de Ventas")

# --- Carga y Limpieza de Datos ---
@st.cache_data
def load_data():
    """
    Carga, limpia y prepara los datos del archivo CSV de ventas.
    """
    # Cargar los datos
    file_path = "C:\\Users\\efren\\GEMINI\\DATA\\reporte_ventas_final.csv"
    df = pd.read_csv(file_path)

    # --- Limpieza de Datos ---
    # Eliminar espacios en blanco de los nombres de las columnas
    df.columns = df.columns.str.strip()

    # Limpiar espacios en las columnas de texto
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

    # Manejar fechas faltantes usando forward fill
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['order_date'] = df['order_date'].ffill()

    # Convertir columnas a tipo numérico, los errores se convierten en NaN
    numeric_cols = ['quantity', 'unit_price_cop', 'ingreso_neto_item']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Eliminar filas donde el ingreso neto es nulo, ya que son cruciales para el análisis
    df.dropna(subset=['ingreso_neto_item'], inplace=True)
    
    # Asegurarse de que la cantidad no tenga nulos
    df['quantity'].fillna(0, inplace=True)
    df['quantity'] = df['quantity'].astype(int)

    return df

# Cargar los datos usando la función cacheada
data = load_data()

# --- Barra Lateral de Navegación ---
st.sidebar.header("Navegación")
selection = st.sidebar.radio(
    "Ir a:",
    ["Vista General", "Análisis de Ventas", "Análisis de Productos y Fabricantes"]
)

# --- Sección: Vista General ---
if selection == "Vista General":
    st.header("Vista General del Negocio")
    
    # Métricas clave (KPIs)
    total_revenue = data['ingreso_neto_item'].sum()
    total_items_sold = data['quantity'].sum()
    total_orders = data['order_id'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales (COP)", f"${total_revenue:,.0f}")
    col2.metric("Total de Artículos Vendidos", f"{total_items_sold:,}")
    col3.metric("Total de Órdenes", f"{total_orders:,}")

    st.markdown("---")
    st.subheader("Datos de Ventas Limpios")
    st.dataframe(data)

# --- Sección: Análisis de Ventas ---
elif selection == "Análisis de Ventas":
    st.header("Análisis Profundo de Ventas")

    # Ingresos a lo largo del tiempo
    st.subheader("Ingresos Netos a lo Largo del Tiempo")
    data['month_year'] = data['order_date'].dt.to_period('M').astype(str)
    sales_over_time = data.groupby('month_year')['ingreso_neto_item'].sum().reset_index()
    fig_time = px.line(sales_over_time, x='month_year', y='ingreso_neto_item', title="Ingresos Mensuales", labels={"month_year": "Mes", "ingreso_neto_item": "Ingresos Netos (COP)"})
    st.plotly_chart(fig_time, use_container_width=True)

    # Ventas por Categoría y Ciudad
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ventas por Categoría")
        sales_by_category = data.groupby('category')['ingreso_neto_item'].sum().reset_index().sort_values(by='ingreso_neto_item', ascending=False)
        fig_cat = px.bar(sales_by_category, x='category', y='ingreso_neto_item', title="Ingresos por Categoría de Producto", labels={"category": "Categoría", "ingreso_neto_item": "Ingresos Netos (COP)"})
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("Ventas por Ciudad")
        sales_by_city = data.groupby('ciudad_cliente')['ingreso_neto_item'].sum().reset_index().sort_values(by='ingreso_neto_item', ascending=False)
        fig_city = px.bar(sales_by_city, x='ciudad_cliente', y='ingreso_neto_item', title="Ingresos por Ciudad", labels={"ciudad_cliente": "Ciudad", "ingreso_neto_item": "Ingresos Netos (COP)"})
        st.plotly_chart(fig_city, use_container_width=True)

# --- Sección: Análisis de Productos y Fabricantes ---
elif selection == "Análisis de Productos y Fabricantes":
    st.header("Análisis de Productos y Fabricantes")

    # Top 10 Productos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Productos por Ingresos")
        top_products_revenue = data.groupby('product_name')['ingreso_neto_item'].sum().nlargest(10).reset_index()
        st.dataframe(top_products_revenue)

    with col2:
        st.subheader("Top 10 Productos por Cantidad Vendida")
        top_products_quantity = data.groupby('product_name')['quantity'].sum().nlargest(10).reset_index()
        st.dataframe(top_products_quantity)
    
    st.markdown("---")

    # Rendimiento por Fabricante
    st.subheader("Ingresos por Fabricante")
    sales_by_manufacturer = data.groupby('manufacturer')['ingreso_neto_item'].sum().reset_index().sort_values(by='ingreso_neto_item', ascending=False)
    fig_mfg = px.bar(sales_by_manufacturer, x='manufacturer', y='ingreso_neto_item', title="Ingresos Totales por Fabricante", labels={"manufacturer": "Fabricante", "ingreso_neto_item": "Ingresos Netos (COP)"})
    st.plotly_chart(fig_mfg, use_container_width=True)
