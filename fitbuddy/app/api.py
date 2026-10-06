from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .ai import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
    update_workout_plan,
)
from .crud import (
    get_latest_plan,
    get_user_with_plan,
    save_plan,
    save_user,
    update_plan,
)
from .database import get_db
from .schemas import FeedbackRequest, UserInput


router = APIRouter(
    prefix="/api",
    tags=["FitBuddy API"],
)


@router.post("/plans")
def create_plan(
    user_data: UserInput,
    db: Session = Depends(get_db),
):

    try:

        workout_plan = generate_workout_gemini(
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            goal=user_data.goal,
            age=user_data.age,
            weight=user_data.weight,
        )

        user = save_user(
            db=db,
            user_data=user_data,
        )

        plan = save_plan(
            db=db,
            user=user,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        return {
            "success": True,
            "user_id": user.user_id,
            "plan_id": plan.id,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/plans/feedback")
def revise_plan(
    feedback_data: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user_with_plan(
        db=db,
        user_id=feedback_data.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_latest_plan(
        db=db,
        user_id=feedback_data.user_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found.",
        )

    current_plan = (
        plan.updated_plan
        if plan.updated_plan
        else plan.original_plan
    )

    try:

        revised_plan = update_workout_plan(
            original_plan=current_plan,
            feedback=feedback_data.feedback,
            name=user.name,
            age=user.age,
            goal=user.goal,
            intensity=user.intensity,
        )

        update_plan(
            db=db,
            plan=plan,
            updated_workout=revised_plan,
            feedback=feedback_data.feedback,
        )

        return {
            "success": True,
            "user_id": user.user_id,
            "plan_id": plan.id,
            "feedback": feedback_data.feedback,
            "updated_plan": revised_plan,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/users/{user_id}")
def get_user_plan(
    user_id: str,
    db: Session = Depends(get_db),
):

    user = get_user_with_plan(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_latest_plan(
        db=db,
        user_id=user_id,
    )

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "plan": (
            {
                "id": plan.id,
                "original_plan": plan.original_plan,
                "updated_plan": plan.updated_plan,
                "nutrition_tip": plan.nutrition_tip,
                "feedback": plan.feedback,
            }
            if plan
            else None
        ),
    }