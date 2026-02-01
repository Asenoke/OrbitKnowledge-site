from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from starlette import status
from app import SessionDep
from app.db.models import HeroModel
from app.dependencies.dependencies import require_admin
from app.hero.schema import HeroAddSchema, HeroUpdateSchema

# Создание роутера для работы с героями
router = APIRouter(prefix="/heroes", tags=["Работа с данными героев"])

# Эндпоинт для создания нового героя
@router.post("/createHero")
async def create_hero(hero: HeroAddSchema, session: SessionDep):
    new_hero = HeroModel(
        name=hero.name,
        role=hero.role,
        description=hero.description,
        image_url=hero.image_url,
        era=hero.era,
        tags=hero.tags,
        birth_date=hero.birth_date,
        death_date=hero.death_date,
        achievements=hero.achievements,
        biography=hero.biography,
    )
    session.add(new_hero)
    await session.commit()
    await session.refresh(new_hero)

    return new_hero

# Эндпоинт для получения всех героев с пагинацией
@router.get("/getAllHeroes")
async def get_all_heroes(
        session: SessionDep,
        skip: int = Query(0, ge=0, description="Сколько героев пропустить"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит героев"),
):
    stmt = select(HeroModel)
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    heroes = result.scalars().all()

    return heroes

# Эндпоинт для получения героя по ID
@router.get("/getHero/{hero_id}")
async def get_hero(hero_id: int, session: SessionDep):
    stmt = select(HeroModel).where(HeroModel.id == hero_id)
    result = await session.execute(stmt)
    hero = result.scalar_one_or_none()

    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Герой с ID {hero_id} не найден"
        )

    return hero

# Эндпоинт для обновления героя по ID (только для админов)
@router.put("/updateHero/{hero_id}", dependencies=[Depends(require_admin)])
async def update_hero(hero_id: int, update_hero_data: HeroUpdateSchema, session: SessionDep):
    stmt = select(HeroModel).where(HeroModel.id == hero_id)
    result = await session.execute(stmt)
    hero = result.scalar_one_or_none()

    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Герой с ID {hero_id} не найден"
        )

    updated_fields = []

    if update_hero_data.name is not None:
        hero.name = update_hero_data.name
        updated_fields.append("name")

    if update_hero_data.role is not None:
        hero.role = update_hero_data.role
        updated_fields.append("role")

    if update_hero_data.description is not None:
        hero.description = update_hero_data.description
        updated_fields.append("description")

    if update_hero_data.image_url is not None:
        hero.image_url = update_hero_data.image_url
        updated_fields.append("image_url")

    if update_hero_data.era is not None:
        hero.era = update_hero_data.era
        updated_fields.append("era")

    if update_hero_data.tags is not None:
        hero.tags = update_hero_data.tags
        updated_fields.append("tags")

    if update_hero_data.birth_date is not None:
        hero.birth_date = update_hero_data.birth_date
        updated_fields.append("birth_date")

    if update_hero_data.death_date is not None:
        hero.death_date = update_hero_data.death_date
        updated_fields.append("death_date")

    if update_hero_data.achievements is not None:
        hero.achievements = update_hero_data.achievements
        updated_fields.append("achievements")

    if update_hero_data.biography is not None:
        hero.biography = update_hero_data.biography
        updated_fields.append("biography")

    if not updated_fields:
        return hero

    await session.commit()
    await session.refresh(hero)

    return hero

# Эндпоинт для удаления героя по ID (только для админов)
@router.delete("/deleteHero/{hero_id}", dependencies=[Depends(require_admin)])
async def delete_hero(hero_id: int, session: SessionDep):
    stmt = select(HeroModel).where(HeroModel.id == hero_id)
    result = await session.execute(stmt)
    hero = result.scalar_one_or_none()

    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Герой с ID {hero_id} не найден"
        )

    await session.delete(hero)
    await session.commit()

    return {
        "status": "success",
        "message": f"Герой с ID {hero_id} успешно удален",
        "deleted_hero": {
            "id": hero_id,
            "name": hero.name,
            "role": hero.role
        }
    }

# Эндпоинт для получения героев по эпохе
@router.get("/getHeroesByEra/{era}")
async def get_heroes_by_era(
        era: str,
        session: SessionDep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        only_active: bool = Query(True)
):
    stmt = select(HeroModel).where(HeroModel.era == era)

    stmt = stmt.offset(skip).limit(limit)

    result = await session.execute(stmt)
    heroes = result.scalars().all()

    return heroes
