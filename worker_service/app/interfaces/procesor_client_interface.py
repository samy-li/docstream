from pydantic import BaseModel


class ProcessorRequest(BaseModel):
    job_id: str
    text: str


class ProcessorClientInterface:
    def process(self, request: ProcessorRequest) -> bool:
        raise NotImplementedError
