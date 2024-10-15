# config.py
COLLECTIONS_CONFIG = {
    "collections": [
        
        {
            "id": "POI_Collection",
            "type": "geojson",
            "file_path": "data/POI_Collection.geojson"
        },
        {
            "id": "State_Boundary",
            "type": "geojson",
            "file_path": "data/state_boundary.geojson"
        }
    ]
}

'''{
            "id": "sql_collection_1",
            "type": "sql",
            "connection_string": "mssql+pyodbc://username:password@server1/database1?driver=ODBC+Driver+17+for+SQL+Server",
            "table": "features"
        },
        {
            "id": "sql_collection_2",
            "type": "sql",
            "connection_string": "mssql+pyodbc://username:password@server2/database2?driver=ODBC+Driver+17+for+SQL+Server",
            "table": "features"
        },'''