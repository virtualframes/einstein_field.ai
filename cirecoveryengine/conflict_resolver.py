from collections import defaultdict

class ConflictResolver:
    def __init__(self):
        self.file_claims = defaultdict(list)

    def register_intent(self, agent_id, files):
        for file in files:
            if agent_id not in self.file_claims[file]:
                self.file_claims[file].append(agent_id)

    def resolve(self):
        conflicts = {k: v for k, v in self.file_claims.items() if len(v) > 1}
        resolutions = {}
        for file, agents in conflicts.items():
            # Simple arbitration: first agent wins
            winner = agents[0]
            resolutions[file] = winner
            print(f"Conflict for {file}: {agents}. Winner: {winner}")
        return resolutions, conflicts

if __name__ == "__main__":
    resolver = ConflictResolver()
    resolver.register_intent("agent:jules", ["shared_file.py"])
    resolver.register_intent("agent:ana", ["shared_file.py"])
    resolutions, conflicts = resolver.resolve()
    if conflicts:
        print("\nConflicts Resolved:")
        for file, winner in resolutions.items():
            print(f"  {file}: Assigned to {winner}")
    else:
        print("No conflicts detected.")
