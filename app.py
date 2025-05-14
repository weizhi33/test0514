import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)


###############################################
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")


# 地理區域
point = ee.Geometry.Point([121.56, 25.03])

# 擷取 Landsat NDVI
image = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterBounds(point) \
    .filterDate("2022-01-01", "2022-12-31") \
    .median()

ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

# 顯示地圖
Map = geemap.Map(center=[25.03, 121.56], zoom=10)
Map.addLayer(ndvi, {"min": 0, "max": 1, "palette": ["white", "green"]}, "NDVI")
Map.to_streamlit(height=600)
