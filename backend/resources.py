import webbrowser

# Sample skill gap list (In real use case, this would come from the skill gap analysis logic)
skill_gap_list = [
    "Power BI",
    "SQL",
    "Natural Language Processing",
    "Docker",
    "Time Series Forecasting"
]

# Mapping of skills to learning resources
skill_resources = {
    "Power BI": [
        "https://www.youtube.com/playlist?list=PLrRPvpgDmw0nZXL5xjmEooD1WkA8U8Dsv",
        "https://radacad.com/power-bi-from-rookie-to-rock-star",
        "https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/"
    ],
    "SQL": [
        "https://www.w3schools.com/sql/",
        "https://www.youtube.com/playlist?list=PLillGF-RfqbbiTGgA77tGO426V3hRF9iE",
        "https://www.khanacademy.org/computing/computer-programming/sql"
    ],
    "Natural Language Processing": [
        "https://www.coursera.org/learn/language-processing",
        "https://www.youtube.com/playlist?list=PLZyvi_9gamL-EE3zQJbU5N5z6LbMmhz3m",
        "https://nlp.stanford.edu/IR-book/"
    ],
    "Docker": [
        "https://www.youtube.com/playlist?list=PL9ooVrP1hQOGvX4bOSAmMWvQj2mY3t-7L",
        "https://docs.docker.com/get-started/",
        "https://www.udemy.com/course/docker-mastery/"
    ],
    "Time Series Forecasting": [
        "https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF",
        "https://otexts.com/fpp3/",
        "https://www.machinelearningplus.com/time-series/time-series-analysis-python/"
    ]
}

def show_learning_resources(skill_gap_list):
    print("\n📚 Learning Resources for Skill Gaps:\n")
    for skill in skill_gap_list:
        print(f"🔹 {skill}")
        resources = skill_resources.get(skill, ["No resources found."])
        for res in resources:
            print(f"   • {res}")
        print()

# Function call to display the resources
show_learning_resources(skill_gap_list)

