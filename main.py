import argparse
from agent.chat import SimpleAgent
from rich.console import Console
from rich.markdown import Markdown

def main():
    parser = argparse.ArgumentParser(
        prog="Simple Agent",
        description="A simple agent"
    )

    parser.add_argument("-t", "--temperature", help="Set the temperature of the model", type=float, default=0.0)
    parser.add_argument("-m", "--model", help="Set the model string to use.", type=str, default="openai/gpt-4o-mini")

    args = parser.parse_args()

    agent = SimpleAgent(
        temperature=args.temperature,
        model=args.model
    )

    console = Console()

    while True:
        prompt = input("> ")
        if prompt == "/exit":
            break

        response = agent.prompt(prompt)
        console.print(Markdown(response))

if __name__ == "__main__":
    main()
