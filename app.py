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
point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 擷取 Landsat 
my_image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')\
    .filterBounds(point)\
    .filterDate('2021-01-01', '2022-01-01')\
    .sort('CLOUDY_PIXEL_PERCENTAGE')\
    .first()\
    .select('B.*')
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

training001 = my_image.sample(
    **{
        'region': my_image.geometry(),  # 若不指定，則預設為影像my_image的幾何範圍。
        'scale': 30,
        'numPixels': 10000,
        'seed': 0,
        'geometries': True,  # 設為False表示取樣輸出的點將忽略其幾何屬性(即所屬網格的中心點)，無法作為圖層顯示，可節省記憶體。
    }
)
n_clusters = 7
clusterer_wekaKMeans = ee.Clusterer.wekaKMeans(nClusters=n_clusters).train(training001)
result001 = my_image.cluster(clusterer_wekaKMeans)
legend_dict = {
     'A': '#10d22c',
    'B': '#1c5f2c',
    'C': '#ffff52',
    'D': '#ffff52',
    'E': '#ab6c28',
    'F': '#0000ff',
    'G': '#868686'
}
palette = list(legend_dict.values())
vis_params_001 = {'min': 0, 'max': 4, 'palette': palette}

Map = geemap.Map(center=[24.081653403304525, 120.5583462887228 ], zoom=9)
left_layer = geemap.ee_tile_layer(image, vis_params, "Sentinel-2")
right_layer = geemap.ee_tile_layer(result001, vis_params_001, "KMeans clustered land cover")
Map.split_map(left_layer, right_layer)
Map.add_legend(title='Land Cover Cluster (KMeans)', legend_dict=legend_dict, draggable=False, position='bottomright')
Map.to_streamlit(height=600)
