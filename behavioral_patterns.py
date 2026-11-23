from abc import ABC, abstractmethod


# ====================================================================
# 1. STRATEGY
# Problem: A load balancer routes requests across inference servers using
#          different policies. Hardcoding if/elif branches violates Open/Closed.
# Idea: Define a RoutingStrategy interface and swap concrete strategies
#       at runtime via set_strategy().
# ====================================================================
class RoutingStrategy(ABC):
    @abstractmethod
    def select_server(self, servers: list[dict]) -> dict:
        pass


class FirstAvailableStrategy(RoutingStrategy):
    def select_server(self, servers: list[dict]) -> dict:
        return servers[0]


class LowestLatencyStrategy(RoutingStrategy):
    def select_server(self, servers: list[dict]) -> dict:
        return min(servers, key=lambda s: s["latency_ms"])


class LoadBalancer:
    def __init__(self, strategy: RoutingStrategy = None):
        self._strategy = strategy or FirstAvailableStrategy()

    def set_strategy(self, strategy: RoutingStrategy) -> None:
        self._strategy = strategy

    def route_request(self, servers: list[dict]) -> str:
        chosen = self._strategy.select_server(servers)
        return f"Routed to {chosen['name']} (latency={chosen['latency_ms']}ms)"


# ====================================================================
# 2. TEMPLATE METHOD
# Problem: Multiple RAG document ingestors follow the exact same pipeline
#          (read -> normalize -> extract -> save), differing only in how
#          they read and extract structured records.
# Idea: DocumentIngestor.ingest() fixes the execution sequence; subclasses
#       implement the abstract steps and optionally override hooks.
# ====================================================================
class DocumentIngestor(ABC):
    def ingest(self) -> list[str]:
        """Template method: defines the invariant pipeline skeleton."""
        raw_text = self.read()
        clean_text = self.normalize(raw_text)
        records = self.extract(clean_text)
        self.save(records)
        return records

    @abstractmethod
    def read(self) -> str:                 # Required step
        pass

    def normalize(self, raw_text: str) -> str:  # Default hook
        return raw_text.strip()

    @abstractmethod
    def extract(self, clean_text: str) -> list[str]:  # Required step
        pass

    def save(self, records: list[str]) -> None:       # Default hook
        print(f"Saved {len(records)} records -> {records}")


class MarkdownIngestor(DocumentIngestor):
    def read(self) -> str:
        return "  # Intro\n# Architecture\nPlain paragraph  "

    def extract(self, clean_text: str) -> list[str]:
        # Extract only Markdown headings
        return [line.lstrip("# ") for line in clean_text.splitlines() if line.startswith("#")]


class LogIngestor(DocumentIngestor):
    def read(self) -> str:
        return "INFO: started\nERROR: timeout\nERROR: disk full"

    def extract(self, clean_text: str) -> list[str]:
        # Extract only ERROR lines
        return [line for line in clean_text.splitlines() if line.startswith("ERROR")]

    def save(self, records: list[str]) -> None:
        # Custom export override
        print("ALERT LOGS:", " | ".join(records))


# ====================================================================
# Demo
# ====================================================================
if __name__ == "__main__":
    print("--- 1. Strategy")
    nodes = [
        {"name": "eu-west-1", "latency_ms": 48},
        {"name": "eu-central-1", "latency_ms": 14},
        {"name": "us-east-1", "latency_ms": 95},
    ]
    lb = LoadBalancer()
    print("Default:", lb.route_request(nodes))

    lb.set_strategy(LowestLatencyStrategy())
    print("Switched:", lb.route_request(nodes))

    print("\n--- 2. Template Method")
    MarkdownIngestor().ingest()
    LogIngestor().ingest()