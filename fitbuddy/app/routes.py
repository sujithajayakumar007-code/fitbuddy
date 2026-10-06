from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .ai import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
    update_workout_plan,
)
from .config import settings
from .crud import (
    get_all_users,
    get_latest_plan,
    get_user_with_plan,
    save_plan,
    save_user,
    update_plan,
)
from .database import get_db
from .schemas import FeedbackRequest, UserInput


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter()


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "demo_mode": settings.demo_mode,
        },
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):

    try:
        user_data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

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

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "active_plan": plan.original_plan,
                "demo_mode": settings.demo_mode,
            },
        )

    except ValidationError as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "message": str(exc),
            },
            status_code=400,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "message": f"Unable to generate plan: {exc}",
            },
            status_code=500,
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):

    try:
        feedback_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user_with_plan(
            db=db,
            user_id=feedback_data.user_id,
        )

        if user is None:
            raise ValueError(
                "User was not found. Please generate a plan first."
            )

        plan = get_latest_plan(
            db=db,
            user_id=feedback_data.user_id,
        )

        if plan is None:
            raise ValueError(
                "No workout plan exists for this user."
            )

        current_plan = (
            plan.updated_plan
            if plan.updated_plan
            else plan.original_plan
        )

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

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "active_plan": revised_plan,
                "demo_mode": settings.demo_mode,
            },
        )

    except ValidationError as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "message": str(exc),
            },
            status_code=400,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "message": str(exc),
            },
            status_code=400,
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    admin_key: str | None = None,
    db: Session = Depends(get_db),
):

    if settings.admin_key:

        if admin_key != settings.admin_key:

            return templates.TemplateResponse(
                request=request,
                name="error.html",
                context={
                    "request": request,
                    "message": "Invalid admin key.",
                },
                status_code=403,
            )

    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="all_user.html",
        context={
            "request": request,
            "users": users,
        },
    )


@router.get(
    "/health",
)
def health_check():

    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
    }