AIR_QUALITY_DEVICE_TYPE = "Air Quality Sensor"

PM25_INFO = [
    {
        "range": "0.0 to 12.0",
        "category": "Excellent",
        "message": "Air quality is considered satisfactory, and air pollution poses little or no risk.",
        "code": 1,
    },
    {
        "range": "12.1 to 35.4",
        "category": "Good",
        "message": "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.",
        "code": 2,
    },
    {
        "range": "35.5 to 55.4",
        "category": "Fair",
        "message": "Members of sensitive groups may experience health effects. The general public is not likely to be affected.",
        "code": 3,
    },
    {
        "range": "55.5 to 150.4",
        "category": "Inferior",
        "message": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.",
        "code": 3,
    },
    {
        "range": "150.5 to 250.4",
        "category": "Poor",
        "message": "Health alert: everyone may experience more serious health effects.",
        "code": 4,
    },
    {
        "range": "250.5 to 99999999",
        "category": "Hazardous",
        "message": "Health warnings of emergency conditions. The entire population is more likely to be affected.",
        "code": 5,
    },
]

PM10_INFO = [
    {
        "range": "0 to 54",
        "category": "Excellent",
        "message": "Air quality is considered satisfactory, and air pollution poses little or no risk.",
        "code": 1,
    },
    {
        "range": "55 to 154",
        "category": "Good",
        "message": "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.",
        "code": 2,
    },
    {
        "range": "155 to 254",
        "category": "Fair",
        "message": "Members of sensitive groups may experience health effects. The general public is not likely to be affected.",
        "code": 3,
    },
    {
        "range": "255 to 354",
        "category": "Inferior",
        "message": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.",
        "code": 3,
    },
    {
        "range": "355 to 424",
        "category": "Poor",
        "message": "Health alert: everyone may experience more serious health effects.",
        "code": 4,
    },
    {
        "range": "425 to 99999999",
        "category": "Hazardous",
        "message": "Health warnings of emergency conditions. The entire population is more likely to be affected.",
        "code": 5,
    },
]
