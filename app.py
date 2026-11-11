
import os
import streamlit as st

from tavily import TavilyClient
from databricks_openai import DatabricksOpenAI
from databricks.sdk import WorkspaceClient

from agent import cricket_agent


# ----------------------------------
# 1. PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="CricketIQ",
    page_icon="🏏",
    layout="wide"
)


# ----------------------------------
# 2. INITIALIZE CONNECTIONS
# ----------------------------------

@st.cache_resource
def initialize_clients():

    # Retrieve Tavily key from Databricks App resource
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not tavily_key:
        raise ValueError("Tavily API key is not configured.")

    tavily = TavilyClient(api_key=tavily_key)

    # Authenticate using the Databricks App identity
    workspace_client = WorkspaceClient()

    client = DatabricksOpenAI(
        workspace_client=workspace_client,
        base_url=(
            os.environ["DATABRICKS_HOST"]
            + "/ai-gateway/mlflow/v1"
        )
    )

    return tavily, client


# ----------------------------------
# 3. APPLICATION HEADER
# ----------------------------------

st.title("🏏 CricketIQ")

st.markdown(
    "### Your AI-powered Cricket Research Assistant"
)

st.write(
    "Search for any cricket player and explore "
    "their biography, career statistics, achievements "
    "and recent performances."
)

st.divider()


# ----------------------------------
# 4. PLAYER INPUT
# ----------------------------------

player_name = st.text_input(
    "Enter Cricket Player Name",
    placeholder="Example: Virat Kohli"
)

search_button = st.button(
    "🔍 Search Player",
    type="primary"
)


# ----------------------------------
# 5. CALL THE CRICKET AGENT
# ----------------------------------

if search_button:

    if not player_name.strip():

        st.warning("Please enter a cricket player's name.")

    else:

        try:

            tavily, client = initialize_clients()

            with st.spinner(
                f"Researching {player_name}... Please wait."
            ):

                result = cricket_agent(
                    player_name=player_name.strip(),
                    tavily=tavily,
                    client=client
                )

            st.success("Player research completed!")

            st.divider()

            # Display AI-generated report

            st.header(
                f"🏏 {result['player_name']}"
            )

            st.markdown(result["report"])

            # Display original search sources

            st.divider()

            st.subheader("🔗 Research Sources")

            for i, source in enumerate(
                result["sources"], 1
            ):

                if source["url"]:
                    st.markdown(
                        f"{i}. [{source['title']}]"
                        f"({source['url']})"
                    )

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )


# ----------------------------------
# 6. FOOTER
# ----------------------------------

st.divider()

st.caption(
    "CricketIQ | Powered by Databricks AI Gateway, "
    "GPT OSS 120B and Tavily"
)
