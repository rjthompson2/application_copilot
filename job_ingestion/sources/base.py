class JobSource:
    name = "base"

    async def discover(self, query, location):
        """
        Return lightweight job references
        """
        raise NotImplementedError

    async def enrich(self, job_ref):
        """
        Return full normalized job data
        """
        raise NotImplementedError