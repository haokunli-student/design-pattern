"""Creational patterns: control how objects are instantiated and configured.

1. Singleton       : ensure a class has only one global instance
2. Factory Method  : delegate concrete product creation to subclasses
3. Builder         : construct complex objects step by step
"""

from abc import ABC, abstractmethod


# ====================================================================
# 1. SINGLETON
# Problem: Multiple modules need access to the same global model registry
#          without reloading heavy configuration settings.
# Idea: Override __new__ to allocate the instance once and return it on
#       every subsequent call.
# ====================================================================
class ModelRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {
                "default_model": "llama-3-70b",
                "max_tokens": 2048,
                "device": "cuda:0",
            }
        return cls._instance


# ====================================================================
# 2. FACTORY METHOD
# Problem: The deployment pipeline uploads artifacts to different cloud
#          providers (S3, GCS), and new providers will be added later.
# Idea: StorageUploader defines the workflow in deploy_artifact() and
#       relies on subclasses to implement create_client().
# ====================================================================
class StorageClient(ABC):             # Product interface
    @abstractmethod
    def upload(self, filename: str) -> str:
        pass


class S3Client(StorageClient):
    def upload(self, filename: str) -> str:
        return f"[AWS S3] Uploaded '{filename}' to s3://ml-artifacts/"


class GCSClient(StorageClient):
    def upload(self, filename: str) -> str:
        return f"[Google Cloud] Uploaded '{filename}' to gs://ml-artifacts/"


class StorageUploader(ABC):           # Creator base class
    @abstractmethod
    def create_client(self) -> StorageClient:
        pass

    def deploy_artifact(self, filename: str) -> str:
        # Decoupled from concrete storage classes
        client = self.create_client()
        return client.upload(filename)


class S3Uploader(StorageUploader):
    def create_client(self) -> StorageClient:
        return S3Client()


class GCSUploader(StorageUploader):
    def create_client(self) -> StorageClient:
        return GCSClient()


# ====================================================================
# 3. BUILDER
# Problem: A distributed TrainingJob has many optional parameters; a
#          telescoping constructor with 6+ arguments is error-prone.
# Idea: JobBuilder exposes chainable setter methods, and JobDirector
#       encapsulates common hardware presets.
# ====================================================================
class TrainingJob:                    # Complex product
    def __init__(self):
        self.model_name = None
        self.gpu_type = "CPU"
        self.batch_size = 16
        self.use_mixed_precision = False

    def __str__(self) -> str:
        return (
            f"TrainingJob(model={self.model_name}, gpu={self.gpu_type}, "
            f"batch_size={self.batch_size}, fp16={self.use_mixed_precision})"
        )


class JobBuilder:
    def __init__(self):
        self._job = TrainingJob()

    def set_model(self, name: str):
        self._job.model_name = name
        return self                   # Return self for fluent chaining

    def set_gpu(self, gpu: str):
        self._job.gpu_type = gpu
        return self

    def set_batch_size(self, size: int):
        self._job.batch_size = size
        return self

    def enable_fp16(self):
        self._job.use_mixed_precision = True
        return self

    def build(self) -> TrainingJob:
        built_job = self._job
        self._job = TrainingJob()     # Reset internal state for reuse
        return built_job


class JobDirector:                    # Optional director for standard recipes
    def __init__(self, builder: JobBuilder):
        self._builder = builder

    def build_quick_prototype(self) -> TrainingJob:
        return (
            self._builder.set_model("distilbert-base")
            .set_gpu("T4")
            .set_batch_size(32)
            .build()
        )

    def build_production_run(self) -> TrainingJob:
        return (
            self._builder.set_model("mistral-7b")
            .set_gpu("A100-80GB")
            .set_batch_size(128)
            .enable_fp16()
            .build()
        )


# ====================================================================
# Demo
# ====================================================================
if __name__ == "__main__":
    print("--- 1. Singleton")
    reg_a = ModelRegistry()
    reg_b = ModelRegistry()
    reg_a.config["max_tokens"] = 4096
    print("Same instance:", reg_a is reg_b)
    print("Shared config:", reg_b.config)

    print("\n--- 2. Factory Method")
    for uploader in [S3Uploader(), GCSUploader()]:
        print(uploader.deploy_artifact("weights_v1.safetensors"))

    print("\n--- 3. Builder")
    director = JobDirector(JobBuilder())
    print(director.build_quick_prototype())
    print(director.build_production_run())
    custom_job = (
        JobBuilder()
        .set_model("qwen-14b")
        .set_gpu("H100")
        .enable_fp16()
        .build()
    )
    print("Custom:", custom_job)