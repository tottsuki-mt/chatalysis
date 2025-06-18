from langchain.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.agents import AgentType
from langchain.tools import tool
import pandas as pd
from typing import Dict, Any


def create_agent(df: pd.DataFrame):
    llm = Ollama(model="llama3")

    @tool
    def display_dataframe(head: int = 5) -> str:
        """Display the first few rows of the dataframe"""
        return df.head(head).to_markdown()

    @tool
    def show_data_summary() -> str:
        """Show number of rows, columns and missing values"""
        missing = df.isnull().sum().sum()
        return f"Rows: {len(df)}, Columns: {len(df.columns)}, Missing: {missing}"

    @tool
    def show_descriptive_stats() -> str:
        """Show descriptive statistics"""
        return df.describe().to_markdown()

    @tool
    def show_correlation_matrix() -> str:
        """Compute correlation matrix"""
        return df.corr().to_markdown()

    @tool
    def plot_histogram(column_name: str) -> str:
        """Return histogram data for a column"""
        hist = df[column_name].dropna().hist().get_figure()
        hist_data = hist.to_json()
        return hist_data

    @tool
    def plot_scatterplot(x_column: str, y_column: str) -> str:
        """Return scatterplot data for two columns"""
        fig = df.plot.scatter(x=x_column, y=y_column).get_figure()
        plot_data = fig.to_json()
        return plot_data

    tools = [
        Tool(name="display_dataframe", func=display_dataframe, description="Display part of the dataframe"),
        Tool(name="show_data_summary", func=show_data_summary, description="Show summary of the data"),
        Tool(name="show_descriptive_stats", func=show_descriptive_stats, description="Show descriptive statistics"),
        Tool(name="show_correlation_matrix", func=show_correlation_matrix, description="Compute correlation matrix"),
        Tool(name="plot_histogram", func=plot_histogram, description="Plot histogram for a column"),
        Tool(name="plot_scatterplot", func=plot_scatterplot, description="Plot scatterplot for two columns"),
    ]

    prompt = PromptTemplate.from_template(
        """You are a data analysis assistant. Use the provided tools to answer the user's questions about the data."""
    )

    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False, prompt=prompt)
    return agent
