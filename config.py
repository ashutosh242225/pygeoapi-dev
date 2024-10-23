# config.py
COLLECTIONS_CONFIG = {
    "collections": [
        {
            "id": "POI_Collection",
            "title": "Points of Interest Collection",
            "type": "geojson",
            "file_path": "app/data/POI_Collection1.geojson"
        },
        {
            "id": "State_Boundary",
            "title": "State Boundary Collection",
            "type": "geojson",
            "file_path": "app/data/dis_boundary1.geojson"
        }
    ]
}

'''
{
    "id": "sql_collection_1",
    "title": "SQL Collection 1",
    "type": "sql",
    "connection_string": "mssql+pyodbc://username:password@server1/database1?driver=ODBC+Driver+17+for+SQL+Server",
    "table": "features"
},
{
    "id": "sql_collection_2",
    "title": "SQL Collection 2",
    "type": "sql",
    "connection_string": "mssql+pyodbc://username:password@server2/database2?driver=ODBC+Driver+17+for+SQL+Server",
    "table": "features"
},
'''