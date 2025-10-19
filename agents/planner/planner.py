import json
from collections import defaultdict

class PlannerAgent:
    def __init__(self):
        self.file_claims = defaultdict(list)

    def register_intent(self, agent_id, files):
        for file in files:
            if agent_id not in self.file_claims[file]:
                self.file_claims[file].append(agent_id)

    def arbitrate_conflicts(self):
        conflicts = {k: v for k, v in self.file_claims.items() if len(v) > 1}
        resolutions = {}
        for file, agents in conflicts.items():
            # Simple arbitration: first agent wins
            winner = agents[0]
            resolutions[file] = winner
            print(f"Conflict for {file}: {agents}. Winner: {winner}")
        return resolutions, conflicts

def main():
    # This is a placeholder for a more complete implementation
    # that would likely involve reading events from the backend.
    planner = PlannerAgent()

    # Example intents
    planner.register_intent("agent:jules", ["agents/verifier_agent.py"])
    planner.register_intent("agent:ana", ["agents/verifier_agent.py"])

    resolutions, conflicts = planner.arbitrate_conflicts()

    if conflicts:
        print("\nConflicts Resolved:")
        for file, winner in resolutions.items():
            print(f"  {file}: Assigned to {winner}")
    else:
        print("No conflicts detected.")

if __name__ == "__main__":
    main()
