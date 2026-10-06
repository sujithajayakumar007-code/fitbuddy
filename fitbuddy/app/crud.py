from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .database import Plan, User
from .schemas import UserInput


def save_user(db: Session, user_data: UserInput) -> User:
    statement = select(User).where(User.user_id == user_data.user_id)

    user = db.scalar(statement)

    if user is None:
        user = User(
            user_id=user_data.user_id,
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )

        db.add(user)

    else:
        user.name = user_data.name
        user.age = user_data.age
        user.weight = user_data.weight
        user.goal = user_data.goal
        user.intensity = user_data.intensity

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    workout_plan: str,
    nutrition_tip: str,
) -> Plan:

    plan = Plan(
        user_id=user.id,
        original_plan=workout_plan,
        updated_plan=None,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def get_user_with_plan(
    db: Session,
    user_id: str,
):
    statement = (
        select(User)
        .options(joinedload(User.plans))
        .where(User.user_id == user_id)
    )

    return db.scalar(statement)


def get_latest_plan(
    db: Session,
    user_id: str,
):
    statement = (
        select(Plan)
        .join(User)
        .where(User.user_id == user_id)
        .order_by(Plan.created_at.desc())
    )

    return db.scalars(statement).first()


def update_plan(
    db: Session,
    plan: Plan,
    updated_workout: str,
    feedback: str,
) -> Plan:

    plan.updated_plan = updated_workout
    plan.feedback = feedback

    db.commit()
    db.refresh(plan)

    return plan


def get_all_users(db: Session):
    statement = (
        select(User)
        .options(joinedload(User.plans))
        .order_by(User.created_at.desc())
    )

    return db.execute(statement).unique().scalars().all()