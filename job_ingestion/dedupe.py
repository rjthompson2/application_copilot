from job_ingestion.normalization import make_job_signature


class JobDeduplicator:

    def __init__(self):
        self.seen_signatures = set()

    def is_duplicate(self, job: dict) -> bool:
        """
        Fast O(1) dedupe check
        """

        signature = make_job_signature(
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", "")
        )

        if signature in self.seen_signatures:
            return True

        self.seen_signatures.add(signature)
        return False

    def reset(self):
        self.seen_signatures.clear()