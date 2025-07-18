import grpc
import logging
from concurrent import futures
from pathlib import Path

from processing_service.app.config.settings import Settings
from processing_service.app.core.task_engine import TaskEngine
from processing_service.app.utils.persistence import Storage
from processing_service.app.proto import summarizer_pb2, summarizer_pb2_grpc

logger = logging.getLogger(__name__)

class ProcessingServicer(summarizer_pb2_grpc.SummarizerServicer):
    def __init__(self, task_engine: TaskEngine, storage: Storage):
        self.task_engine = task_engine
        self.storage = storage

    def process(self, request, context):
        try:
            if not request.text or not request.text.strip():
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing or empty text input.")
                return summarizer_pb2.SummaryAck(success=False)

            if not request.job_id or not request.job_id.strip():
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing or empty job_id.")
                return summarizer_pb2.SummaryAck(success=False)

            result = self.task_engine.run(request.text)
            if not result:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("LLM returned empty result.")
                return summarizer_pb2.SummaryAck(success=False)

            success = self.storage.save(request.job_id, result)
            return summarizer_pb2.SummaryAck(success=success)

        except Exception as e:
            logger.exception("Unhandled error in Summarize")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal error during processing.")
            return summarizer_pb2.SummaryAck(success=False)

def serve():
    logging.basicConfig(level=logging.INFO)
    settings = Settings()

    prompt_dir = Path("processing_service/app/core/prompts")
    task_engine = TaskEngine(
        settings=settings,
        prompt_dir=prompt_dir,
        default_prompt_name="prompt1"
    )
    storage = Storage(settings)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    summarizer_pb2_grpc.add_SummarizerServicer_to_server(
        ProcessingServicer(task_engine, storage), server
    )

    server.add_insecure_port('[::]:50052')
    server.start()
    logger.info("Processing server running on port 50052")
    server.wait_for_termination()
