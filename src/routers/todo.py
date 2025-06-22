from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src import models, schemas
from src.database import get_db

router = APIRouter(prefix="/lists", tags=["Todo Lists"])

def get_completion_percentage(tasks: List[models.Task]) -> float:
    """
    Calculate the completion percentage of a given list of tasks.

    This function takes a list of tasks and returns the completion percentage
    as a float. It rounds the result to two decimal places.

    If the list of tasks is empty, the function returns 0.0.

    Args:
        tasks (List[models.Task]): A list of tasks

    Returns:
        float: The completion percentage as a float
    """
    if not tasks:
        return 0.0
    done = sum(1 for task in tasks if task.status == schemas.TaskStatus.COMPLETED)
    return round((done / len(tasks)) * 100, 2)

@router.post("/", response_model=schemas.TaskList)
def create_list(task_list: schemas.TaskListCreate, db: Session = Depends(get_db)):
    """
    Create a new task list.

    This endpoint creates a new task list with the given name.

    Args:
        task_list (schemas.TaskListCreate): The task list to create

    Returns:
        schemas.TaskList: The newly created task list
    """
    db_list = models.TaskList(name=task_list.name)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

@router.get("/", response_model=List[schemas.TaskList])
def get_lists(db: Session = Depends(get_db)):
    """
    Get all task lists.

    This endpoint returns all existing task lists.

    Returns:
        List[schemas.TaskList]: A list of task lists
    """
    return db.query(models.TaskList).all()

@router.get("/{list_id}", response_model=schemas.TaskList)
def get_list(list_id: int, db: Session = Depends(get_db)):
    """
    Get a task list by ID.

    This endpoint returns a task list by its ID.

    Args:
        list_id (int): The ID of the task list to retrieve

    Returns:
        schemas.TaskList: The task list with the given ID

    Raises:
        HTTPException: If the task list with the given ID is not found
    """
    db_list = db.query(models.TaskList).filter(models.TaskList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list

@router.put("/{list_id}", response_model=schemas.TaskList)
def update_list(list_id: int, task_list: schemas.TaskListCreate, db: Session = Depends(get_db)):
    """
    Update a task list.

    This endpoint updates a task list with the given ID.

    Args:
        list_id (int): The ID of the task list to update
        task_list (schemas.TaskListCreate): The task list with the new name

    Returns:
        schemas.TaskList: The updated task list

    Raises:
        HTTPException: If the task list with the given ID is not found
    """
    db_list = db.query(models.TaskList).filter(models.TaskList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    db_list.name = task_list.name
    db.commit()
    db.refresh(db_list)
    return db_list

@router.delete("/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):
    """
    Delete a task list.

    This endpoint deletes a task list with the given ID.

    Args:
        list_id (int): The ID of the task list to delete

    Returns:
        dict: A dictionary with a "detail" key containing the message "List deleted"

    Raises:
        HTTPException: If the task list with the given ID is not found
    """
    db_list = db.query(models.TaskList).filter(models.TaskList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    db.delete(db_list)
    db.commit()
    return {"detail": "List deleted"}

@router.post("/{list_id}/tasks", response_model=schemas.Task)
def create_task(list_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task within a task list.

    This endpoint creates a new task with the given title, description, status, and priority
    within the task list with the given ID.

    Args:
        list_id (int): The ID of the task list to create the task in
        task (schemas.TaskCreate): The task to create

    Returns:
        schemas.Task: The newly created task

    Raises:
        HTTPException: If the task list with the given ID is not found
    """
    db_list = db.query(models.TaskList).filter(models.TaskList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    db_task = models.Task(**task.dict(), task_list_id=list_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{list_id}/tasks", response_model=List[schemas.Task])
def list_tasks(
    list_id: int,
    status: Optional[schemas.TaskStatus] = None,
    priority: Optional[schemas.TaskPriority] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve tasks from a specific task list.

    This endpoint returns tasks filtered by status and/or priority within the specified task list.

    Args:
        list_id (int): The ID of the task list to retrieve tasks from.
        status (Optional[schemas.TaskStatus]): The status to filter tasks by (optional).
        priority (Optional[schemas.TaskPriority]): The priority to filter tasks by (optional).
        db (Session): The database session dependency.

    Returns:
        List[schemas.Task]: A list of tasks that match the provided filters within the task list.
    """

    query = db.query(models.Task).filter(models.Task.task_list_id == list_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    return query.all()

@router.get("/{list_id}/tasks/completion")
def get_list_completion(list_id: int, db: Session = Depends(get_db)):
    """
    Get the completion percentage of a task list.

    This endpoint returns the completion percentage of the given task list
    as a float between 0.0 and 100.0.

    Args:
        list_id (int): The ID of the task list to get the completion percentage of.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the key "completion_percentage" with the
        completion percentage of the task list as its value.
    """
    tasks = db.query(models.Task).filter(models.Task.task_list_id == list_id).all()
    percentage = get_completion_percentage(tasks)
    return {"completion_percentage": percentage}

@router.get("/{list_id}/tasks/{task_id}", response_model=schemas.Task)
def get_task(list_id: int, task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a task from a task list.

    This endpoint returns a task from the task list with the given ID
    and task ID.

    Args:
        list_id (int): The ID of the task list to retrieve the task from.
        task_id (int): The ID of the task to retrieve.
        db (Session): The database session dependency.

    Returns:
        schemas.Task: The task with the given ID in the task list.

    Raises:
        HTTPException: If the task list with the given ID is not found,
            or if the task with the given ID is not found in the task list.
    """
    task = db.query(models.Task).filter(
        models.Task.task_list_id == list_id,
        models.Task.id == task_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{list_id}/tasks/{task_id}", response_model=schemas.Task)
def update_task(list_id: int, task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task in a task list.

    This endpoint updates a task with the given ID in the task list with the given ID
    with the provided updates.

    Args:
        list_id (int): The ID of the task list to update the task in.
        task_id (int): The ID of the task to update.
        updates (schemas.TaskUpdate): The updates to apply to the task.
        db (Session): The database session dependency.

    Returns:
        schemas.Task: The updated task.

    Raises:
        HTTPException: If the task list with the given ID is not found,
            or if the task with the given ID is not found in the task list.
    """
    task = db.query(models.Task).filter(
        models.Task.task_list_id == list_id,
        models.Task.id == task_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{list_id}/tasks/{task_id}")
def delete_task(list_id: int, task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task from a task list.

    This endpoint deletes a task with the given task ID from the task list
    with the given list ID.

    Args:
        list_id (int): The ID of the task list from which to delete the task.
        task_id (int): The ID of the task to delete.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the key "detail" with the message "Task deleted".

    Raises:
        HTTPException: If the task with the given ID is not found in the task list.
    """

    task = db.query(models.Task).filter(
        models.Task.task_list_id == list_id,
        models.Task.id == task_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}
