from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.v1.dependencies import require_roles
from app.models import User
from app.models import Category
from app.schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(400, "Categoria já cadastrada.")
    obj = Category(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Categoria não encontrada.")
    return obj

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Categoria não encontrada.")
    obj.name, obj.description = data.name, data.description
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Categoria não encontrada.")
    db.delete(obj); db.commit()
