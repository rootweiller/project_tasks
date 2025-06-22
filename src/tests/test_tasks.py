def test_create_task(client):
    """
    Test the creation of a task within a task list.

    This test creates a new task list and adds a task to it.
    It verifies that the task is successfully created by checking
    the response status code and ensuring that the title of the
    task in the response matches the title of the task sent in
    the request.
    """

    list_res = client.post("/lists/", json={"name": "Con tareas"})
    list_id = list_res.json()["id"]

    task = {
        "title": "Write unit tests",
        "description": "Write unit tests",
        "status": "pending",
        "priority": "high"
    }
    res = client.post(f"/lists/{list_id}/tasks", json=task)
    assert res.status_code == 200
    assert res.json()["title"] == task["title"]

def test_filter_tasks_by_status(client):
    """
    Test filtering tasks by status within a task list.

    This test creates a new task list and adds multiple tasks with the
    status 'completed'. It then filters the tasks by this status and
    verifies that the response status code is 200 and that all tasks
    in the response have the status 'completed'.
    """

    list_res = client.post("/lists/", json={"name": "Filtro tareas"})
    list_id = list_res.json()["id"]

    client.post(f"/lists/{list_id}/tasks", json={
        "title": "Tarea 1", "status": "completed", "priority": "low"
    })
    client.post(f"/lists/{list_id}/tasks", json={
        "title": "Tarea 2", "status": "completed", "priority": "low"
    })

    res = client.get(f"/lists/{list_id}/tasks", params={"status": "completed"})
    assert res.status_code == 200
    assert all(task["status"] == "completed" for task in res.json())

def test_completion_percentage(client):
    """
    Test the endpoint that returns the completion percentage of a task list.

    This test creates a new task list and adds two tasks, one with the status 'done'
    and another with the status 'pending'. It then calls the endpoint and verifies
    that the response status code is 200 and that the completion percentage returned
    is 0.0.
    """
    list_res = client.post("/lists/", json={"name": "Completitud"})
    list_id = list_res.json()["id"]

    client.post(f"/lists/{list_id}/tasks", json={"title": "A", "status": "done"})
    client.post(f"/lists/{list_id}/tasks", json={"title": "B", "status": "pending"})

    res = client.get(f"/lists/{list_id}/tasks/completion")
    assert res.status_code == 200
    assert res.json()["completion_percentage"] == 0.0
