
from datetime import date


def cricket_agent(player_name, tavily, client):

    # STEP 1: Search the internet

    search_results = tavily.search(
        query=f"""
        {player_name} cricket career biography,
        latest international cricket statistics,
        Test ODI T20I batting records,
        recent performances and achievements
        """,
        search_depth="advanced",
        max_results=8
    )

    # STEP 2: Prepare search context

    search_context = ""

    for i, item in enumerate(search_results["results"], 1):

        search_context += f"""
        SOURCE {i}

        Title: {item.get('title', '')}

        URL: {item.get('url', '')}

        Information: {item.get('content', '')[:1800]}

        -------------------------
        """

    # STEP 3: Send information to GPT OSS 120B

    response = client.chat.completions.create(

        model="system.ai.gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": """
                You are an expert cricket analyst.

                Prepare a comprehensive cricket player report.

                Rules:
                1. Use web search results as your primary information.
                2. Never invent cricket statistics.
                3. Mention when information cannot be verified.
                4. Separate Test, ODI and T20I statistics.
                5. Mention the applicable date for statistics.
                6. Include source references.
                7. Identify conflicting information.

                Report sections:

                - Player Biography
                - Batting and Bowling Style
                - International Career
                - Test Statistics
                - ODI Statistics
                - T20I Statistics
                - Major Achievements
                - Recent Performances
                - Playing Strengths
                """
            },
            {
                "role": "user",
                "content": f"""
                Prepare a detailed cricket report for {player_name}.

                Current date: {date.today()}

                Web search results:

                {search_context}
                """
            }
        ],

        max_tokens=3000
    )

    # STEP 4: Extract final report

    final_report = response.choices[0].message.content

    # STEP 5: Return report and sources

    sources = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", "")
        }
        for item in search_results["results"]
    ]

    return {
        "player_name": player_name,
        "report": final_report,
        "sources": sources
    }
