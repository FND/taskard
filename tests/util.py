def index_tasks(tasks, attrib):
    index = {}
    for task in tasks:
        _id = getattr(task, attrib)
        index[_id] = task
    return index
