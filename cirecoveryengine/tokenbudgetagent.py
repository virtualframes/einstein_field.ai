class TokenBudgetAgent:
    def __init__(self, max_tokens=4096):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def check_budget(self, requested_tokens):
        """
        Checks if the requested number of tokens is within the budget.
        """
        return self.used_tokens + requested_tokens <= self.max_tokens

    def use_tokens(self, tokens):
        """
        Records the usage of tokens.
        """
        if self.check_budget(tokens):
            self.used_tokens += tokens
            return True
        return False

    def get_remaining_budget(self):
        """
        Returns the number of remaining tokens.
        """
        return self.max_tokens - self.used_tokens

if __name__ == "__main__":
    budget_agent = TokenBudgetAgent()
    print(f"Initial budget: {budget_agent.get_remaining_budget()} tokens")

    if budget_agent.use_tokens(1024):
        print("Used 1024 tokens.")
    else:
        print("Could not use 1024 tokens.")

    print(f"Remaining budget: {budget_agent.get_remaining_budget()} tokens")
