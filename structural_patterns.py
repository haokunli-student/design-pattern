from abc import ABC, abstractmethod


# ====================================================================
# 1. ADAPTER
# Problem: The orchestrator expects every ComputeNode to expose
#          submit(task_dict), while a legacy on-premise cluster only
#          accepts raw XML strings via dispatch_raw_xml(xml_payload).
# Idea: Create LegacyClusterAdapter implementing ComputeNode to convert
#       dictionaries into the legacy XML format.
# ====================================================================
class ComputeNode(ABC):               # Target interface expected by client
    @abstractmethod
    def submit(self, task_dict: dict) -> str:
        pass


class CloudGPUCluster(ComputeNode):   # Already compatible
    def submit(self, task_dict: dict) -> str:
        return f"CloudGPU accepted task '{task_dict['id']}' ({task_dict['cmd']})"


class LegacyOnPremCluster:            # Third-party / legacy adaptee
    def dispatch_raw_xml(self, xml_payload: str) -> str:
        return f"LegacyOnPrem executed XML payload: {xml_payload}"


class LegacyClusterAdapter(ComputeNode):
    def __init__(self, legacy_cluster: LegacyOnPremCluster):
        self._cluster = legacy_cluster

    def submit(self, task_dict: dict) -> str:
        # Translate structured dict into legacy XML string
        xml_payload = f"<task id='{task_dict['id']}'>{task_dict['cmd']}</task>"
        return self._cluster.dispatch_raw_xml(xml_payload)


class Orchestrator:
    def schedule(self, node: ComputeNode, task_dict: dict) -> str:
        return node.submit(task_dict)


# ====================================================================
# 2. DECORATOR
# Problem: An LLM inference service needs optional middlewares (logging,
#          caching, safety filtering) in any runtime combination.
# Idea: Wrap BaseLLMService in stackable decorator objects that share
#       the InferenceService interface.
# ====================================================================
class InferenceService(ABC):
    @abstractmethod
    def predict(self, prompt: str) -> str:
        pass


class BaseLLMService(InferenceService):
    def predict(self, prompt: str) -> str:
        return f"Generated answer for: '{prompt}'"


class ServiceDecorator(InferenceService):  # Base wrapper
    def __init__(self, service: InferenceService):
        self._service = service            # Protected attribute for subclasses

    def predict(self, prompt: str) -> str:
        return self._service.predict(prompt)


class LoggingDecorator(ServiceDecorator):
    def predict(self, prompt: str) -> str:
        result = self._service.predict(prompt)
        return f"[LOG: len={len(prompt)}] {result}"


class CacheDecorator(ServiceDecorator):
    def __init__(self, service: InferenceService):
        super().__init__(service)
        self._cache = {}

    def predict(self, prompt: str) -> str:
        if prompt in self._cache:
            return f"[CACHE HIT] {self._cache[prompt]}"
        response = self._service.predict(prompt)
        self._cache[prompt] = response
        return response


class SafetyFilterDecorator(ServiceDecorator):
    def predict(self, prompt: str) -> str:
        if "forbidden" in prompt.lower():
            return "[BLOCKED] Unsafe prompt detected."
        return self._service.predict(prompt)


# ====================================================================
# Demo
# ====================================================================
if __name__ == "__main__":
    print("--- 1. Adapter")
    orchestrator = Orchestrator()
    job = {"id": "job-42", "cmd": "train.py --epochs 10"}
    print(orchestrator.schedule(CloudGPUCluster(), job))
    print(orchestrator.schedule(LegacyClusterAdapter(LegacyOnPremCluster()), job))

    print("\n--- 2. Decorator")
    # Stack multiple behaviors dynamically without modifying BaseLLMService
    service = SafetyFilterDecorator(LoggingDecorator(CacheDecorator(BaseLLMService())))
    print(service.predict("Explain SOLID principles"))
    print(service.predict("Explain SOLID principles"))  # Triggers cache hit
    print(service.predict("Run forbidden command"))     # Triggers safety block"""Structural patterns: compose classes and objects into larger structures.

1. Adapter   : bridge two incompatible interfaces without altering source code
2. Decorator : dynamically attach responsibilities by wrapping objects
"""

from abc import ABC, abstractmethod


# ====================================================================
# 1. ADAPTER
# Problem: The orchestrator expects every ComputeNode to expose
#          submit(task_dict), while a legacy on-premise cluster only
#          accepts raw XML strings via dispatch_raw_xml(xml_payload).
# Idea: Create LegacyClusterAdapter implementing ComputeNode to convert
#       dictionaries into the legacy XML format.
# ====================================================================
class ComputeNode(ABC):               # Target interface expected by client
    @abstractmethod
    def submit(self, task_dict: dict) -> str:
        pass


class CloudGPUCluster(ComputeNode):   # Already compatible
    def submit(self, task_dict: dict) -> str:
        return f"CloudGPU accepted task '{task_dict['id']}' ({task_dict['cmd']})"


class LegacyOnPremCluster:            # Third-party / legacy adaptee
    def dispatch_raw_xml(self, xml_payload: str) -> str:
        return f"LegacyOnPrem executed XML payload: {xml_payload}"


class LegacyClusterAdapter(ComputeNode):
    def __init__(self, legacy_cluster: LegacyOnPremCluster):
        self._cluster = legacy_cluster

    def submit(self, task_dict: dict) -> str:
        # Translate structured dict into legacy XML string
        xml_payload = f"<task id='{task_dict['id']}'>{task_dict['cmd']}</task>"
        return self._cluster.dispatch_raw_xml(xml_payload)


class Orchestrator:
    def schedule(self, node: ComputeNode, task_dict: dict) -> str:
        return node.submit(task_dict)


# ====================================================================
# 2. DECORATOR
# Problem: An LLM inference service needs optional middlewares (logging,
#          caching, safety filtering) in any runtime combination.
# Idea: Wrap BaseLLMService in stackable decorator objects that share
#       the InferenceService interface.
# ====================================================================
class InferenceService(ABC):
    @abstractmethod
    def predict(self, prompt: str) -> str:
        pass


class BaseLLMService(InferenceService):
    def predict(self, prompt: str) -> str:
        return f"Generated answer for: '{prompt}'"


class ServiceDecorator(InferenceService):  # Base wrapper
    def __init__(self, service: InferenceService):
        self._service = service            # Protected attribute for subclasses

    def predict(self, prompt: str) -> str:
        return self._service.predict(prompt)


class LoggingDecorator(ServiceDecorator):
    def predict(self, prompt: str) -> str:
        result = self._service.predict(prompt)
        return f"[LOG: len={len(prompt)}] {result}"


class CacheDecorator(ServiceDecorator):
    def __init__(self, service: InferenceService):
        super().__init__(service)
        self._cache = {}

    def predict(self, prompt: str) -> str:
        if prompt in self._cache:
            return f"[CACHE HIT] {self._cache[prompt]}"
        response = self._service.predict(prompt)
        self._cache[prompt] = response
        return response


class SafetyFilterDecorator(ServiceDecorator):
    def predict(self, prompt: str) -> str:
        if "forbidden" in prompt.lower():
            return "[BLOCKED] Unsafe prompt detected."
        return self._service.predict(prompt)


# ====================================================================
# Demo
# ====================================================================
if __name__ == "__main__":
    print("--- 1. Adapter")
    orchestrator = Orchestrator()
    job = {"id": "job-42", "cmd": "train.py --epochs 10"}
    print(orchestrator.schedule(CloudGPUCluster(), job))
    print(orchestrator.schedule(LegacyClusterAdapter(LegacyOnPremCluster()), job))

    print("\n--- 2. Decorator")
    # Stack multiple behaviors dynamically without modifying BaseLLMService
    service = SafetyFilterDecorator(LoggingDecorator(CacheDecorator(BaseLLMService())))
    print(service.predict("Explain SOLID principles"))
    print(service.predict("Explain SOLID principles"))  # Triggers cache hit
    print(service.predict("Run forbidden command"))     # Triggers safety block