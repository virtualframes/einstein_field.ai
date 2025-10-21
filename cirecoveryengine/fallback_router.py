class FallbackRouter:
    def __init__(self, primary_model="codex", fallback_model="gemini"):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        # In a real implementation, you would have a more robust way
        # of tracking model availability.
        self.model_availability = {
            "codex": True,
            "gemini": True,
            "claude": True,
        }

    def route(self, prompt):
        """
        Routes a prompt to the primary model, falling back to the
        fallback model if the primary is unavailable.
        """
        if self.model_availability.get(self.primary_model, False):
            print(f"Routing to primary model: {self.primary_model}")
            return self.primary_model
        elif self.model_availability.get(self.fallback_model, False):
            print(f"Primary model unavailable. Routing to fallback model: {self.fallback_model}")
            return self.fallback_model
        else:
            raise RuntimeError("All models are unavailable.")

if __name__ == "__main__":
    router = FallbackRouter()

    # Simulate the primary model being available
    print("--- Primary model available ---")
    selected_model = router.route("Translate 'hello' to French.")
    print(f"Selected model: {selected_model}")

    # Simulate the primary model being unavailable
    print("\n--- Primary model unavailable ---")
    router.model_availability["codex"] = False
    selected_model = router.route("Translate 'hello' to French.")
    print(f"Selected model: {selected_model}")
