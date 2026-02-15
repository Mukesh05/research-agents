from agents import create_research_agent, run_agent


def main():
    """Main entry point for the research assistant."""
    query = input("What can I help you research? ")
    
    # Create agent with model selected based on query complexity
    agent, parser = create_research_agent(query)
    response = run_agent(agent, parser, query)
    
    if response:
        print(response)


if __name__ == "__main__":
    main()
