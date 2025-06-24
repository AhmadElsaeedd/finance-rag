

from models.state import State


class ChatService:
    @staticmethod
    def get_user_input() -> str:
        """Get user input from terminal with proper formatting."""
        return input("\n🤖 Ask me about your finances (or type 'help' for commands): ").strip()


    @staticmethod
    def display_response(*, state: State) -> None:
        """Display the response in a formatted way."""
        if state.answer is None:
            print("\n💬 No answer found.")
            return
        
        print(f"\n💬 Answer: {state.answer}")