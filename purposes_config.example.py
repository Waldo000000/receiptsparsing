# Example configuration for transaction categorization
# Copy this file to purposes_config.py and customize with your personal patterns

purposesMap = { 
    'Revenue': {
        'Salary': {
            'Job 1': [
                "EMPLOYER NAME",
            ],
            'Job 2': [ 
                "SECOND EMPLOYER",
            ]
        },
        'Transfer': {
            "Internal transfer",
            "Transfer Deposit",
            "Funds Transfer to",
            "Sweep from",
            "Sweep into",
        },
        'Interest': {
            "Interest for",
            "Interest earned",
        }
    },
    'Bills': {
        'House': {
            'Rates': [
                "COUNCIL",
            ],
            'Utilities': [
                "ELECTRICITY COMPANY",
                "GAS COMPANY",
                "WATER COMPANY",
            ],
        },
        'Health': [
            "PHARMACY",
            "MEDICAL CENTRE",
        ],
        'Telecom': {
            'Internet': [
                "ISP NAME",
            ],
            'Mobile': [
                "MOBILE PROVIDER",
            ],
            'Streaming': [
                "NETFLIX",
                "SPOTIFY",
            ],
        },
    },
    'Groceries': [
        "SUPERMARKET CHAIN",
        "LOCAL GROCERY",
        "ORGANIC STORE",
    ],
    'Discretionary': {
        'Entertainment': [
            "CINEMA",
            "RESTAURANT NAME",
        ],
        'Shopping': [
            "DEPARTMENT STORE",
            "CLOTHING STORE",
        ]
    },
    'Transport': {
        'Public Transport': [
            "BUS COMPANY",
            "TRAIN SERVICE",
        ],
        'Fuel': [
            "PETROL STATION",
        ],
        'Rideshare': [
            "UBER",
            "TAXI",
        ],
    },
}