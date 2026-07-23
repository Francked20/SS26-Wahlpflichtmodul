import hashlib
import logging
import typing

from website.engine.tasks.models import BackendRegister, TaskData, TaskWidgetConfiguration
from website.engine.tasks.mongo import Challenge, MongoDB

logger = logging.getLogger("task-engine")


class MetaTask:
    all_registered: dict[int, dict[int, BackendRegister]] = {}
    task_hashes: dict[str, TaskData] = {}
    inserted_hashes: dict[str, BackendRegister] = {}

    @classmethod
    def register(cls, data: TaskData) -> TaskWidgetConfiguration:
        h = hashlib.sha512(data.model_dump_json().encode()).hexdigest()

        if h in cls.task_hashes:
            match_obj = cls.task_hashes[h]
            logger.error("%s has already been created!", data)
            raise ValueError(f"Challenge hash on {data.day_id} exists on {match_obj.day_id}.")

        cls.task_hashes[h] = data

        try:
            category = cls.all_registered[data.day_id]
        except KeyError:
            cls.all_registered[data.day_id] = {}
            category = cls.all_registered[data.day_id]

        task_id = len(category)
        conf = TaskWidgetConfiguration(
            task_id=task_id,
            **data.model_dump(),
        )

        register = BackendRegister(**(data.model_dump() | conf.model_dump()))

        cls.inserted_hashes[register.sha256_checksum] = register
        category[task_id] = register

        return conf

    @classmethod
    async def propagate_backend(cls) -> None:
        mongo = MongoDB()
        await mongo.connect_mapper()

        logger.info("Established connection to MongoDB.")

        # inserted_hashes = {}

        created = 0
        updated = 0
        skipped = 0
        removed = 0

        try:
            for task in cls():
                # inserted_hashes[task.sha256_checksum] = task

                challenge = await Challenge.find_one(
                    Challenge.day_id == task.day_id, Challenge.task_id == task.task_id
                )

                # create new
                if not challenge:
                    logger.info(f"Creating new challenge {task.day_id}/{task.task_id}")
                    created += 1

                    await Challenge(**task.model_dump()).create()
                    continue

                # update
                if challenge.sha256_checksum != task.sha256_checksum:
                    logger.info(f"Updating existing challenge {task.day_id}/{task.task_id}")
                    updated += 1

                    await challenge.update({"$set": task.model_dump()})
                    continue

                # skip same
                logger.debug(f"No changes detected in {task.day_id}/{task.task_id}")
                skipped += 1

            # find removed
            checksums = list(cls.inserted_hashes.keys())
            unused_tasks = await Challenge.find_many({"sha256_checksum": {"$nin": checksums}}).to_list()

            for task in unused_tasks:
                logger.info(f"Removing unreferenced challenge {task.day_id}/{task.task_id}")
                await task.delete()

            logger.info(
                f"Successfully created %d, updated %d, removed %d and kept %d tasks.",
                *(created, updated, removed, skipped)
            )

        finally:
            await mongo.disconnect()

    @classmethod
    def __iter__(cls) -> typing.Iterable[BackendRegister]:
        for day in cls.all_registered.values():
            yield from day.values()
