def test_create_task_list(client):
    response = client.post("/lists/", json={"name": "Trabajo"})
    assert response.status_code == 200
    assert response.json()["name"] == "Trabajo"

def test_get_task_lists(client):
    response = client.get("/lists/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_task_list(client):
    create = client.post("/lists/", json={"name": "Antigua"})
    list_id = create.json()["id"]

    update = client.put(f"/lists/{list_id}", json={"name": "Nueva"})
    assert update.status_code == 200
    assert update.json()["name"] == "Nueva"

def test_delete_task_list(client):
    create = client.post("/lists/", json={"name": "Para borrar"})
    list_id = create.json()["id"]

    delete = client.delete(f"/lists/{list_id}")
    assert delete.status_code == 200

    get = client.get(f"/lists/{list_id}")
    assert get.status_code == 404
