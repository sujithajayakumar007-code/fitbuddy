from functools import lru_cache

from google import genai
from google.genai import types

from .config import settings


SYSTEM_INSTRUCTION = """
You are FitBuddy, an AI fitness planning assistant.

Your job is to create practical, conservative general-wellness
workout plans and nutrition/recovery suggestions.

Important safety rules:

1. Do not diagnose diseases.
2. Do not prescribe medication.
3. Do not provide dangerous exercise instructions.
4. Do not encourage extreme dieting.
5. Do not recommend starvation, dehydration, or unsafe weight loss.
6. Respect the requested workout intensity.
7. Include rest/recovery where appropriate.
8. If a person has an injury, pregnancy, chronic disease,
   severe pain, or another medical concern, recommend consulting
   an appropriate healthcare professional.
9. Keep recommendations suitable for general fitness.
10. The output should be clear and easy to follow.
"""


@lru_cache
def _client():
    if not settings.gemini_api_key:
        return None

    return genai.Client(
        api_key=settings.gemini_api_key,
    )


def _generate(
    model: str,
    prompt: str,
    temperature: float = 0.7,
) -> str:

    client = _client()

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=temperature,
        ),
    )

    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()


def _demo_workout(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

User: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

DAY 1 — Full Body Strength
• Warm-up: 5–10 minutes
• Bodyweight squats: 3 × 10
• Incline push-ups: 3 × 8
• Glute bridges: 3 × 12
• Bird-dog: 3 × 8 each side
• Cool-down: 5 minutes

DAY 2 — Cardio
• Brisk walking: 25–30 minutes
• Light mobility: 10 minutes

DAY 3 — Lower Body
• Warm-up: 5–10 minutes
• Squats: 3 × 10
• Reverse lunges: 3 × 8 each leg
• Glute bridges: 3 × 12
• Calf raises: 3 × 15
• Cool-down: 5 minutes

DAY 4 — Recovery
• Easy walking: 15–20 minutes
• Full-body stretching: 10–15 minutes

DAY 5 — Upper Body
• Warm-up: 5–10 minutes
• Incline push-ups: 3 × 8
• Resistance-band rows: 3 × 10
• Shoulder raises: 3 × 10
• Bird-dog: 3 × 8 each side

DAY 6 — Cardio + Core
• Brisk walking/cycling: 25 minutes
• Dead bug: 3 × 8 each side
• Plank: 3 × 20 seconds
• Gentle stretching: 5 minutes

DAY 7 — Rest
• Complete rest or very gentle walking
• Hydration and recovery

GENERAL GUIDANCE

• Start comfortably and increase difficulty gradually.
• Stop if you experience sharp pain, dizziness,
  chest pain, or unusual shortness of breath.
• Prioritize sleep, hydration, and recovery.
""".strip()


def _demo_nutrition_tip(goal: str) -> str:

    return f"""
Nutrition & Recovery Tip

For your {goal} goal:

• Include a protein source with regular meals.
• Eat a variety of vegetables and fruits.
• Choose mostly minimally processed foods.
• Drink water regularly throughout the day.
• Avoid extreme calorie restriction.
• Get adequate sleep to support recovery.
• Adjust food intake according to hunger, activity,
  and personal requirements.

This is general wellness information, not medical nutrition advice.
""".strip()


def _demo_updated_plan(
    original_plan: str,
    feedback: str,
) -> str:

    return f"""
UPDATED FITBUDDY PLAN

The original plan has been adjusted based on this feedback:

"{feedback}"

Recommended adjustment:

• Add the requested activity or training preference gradually.
• Preserve at least one recovery/rest day.
• Avoid suddenly increasing total training volume.
• Keep sessions manageable.
• Continue monitoring how your body responds.

UPDATED 7-DAY STRUCTURE

DAY 1 — Strength + Mobility
• Full-body strength
• 5–10 minute mobility

DAY 2 — Cardio
• 25–35 minutes comfortable cardio

DAY 3 — Strength
• Lower-body and upper-body exercises

DAY 4 — Recovery
• Walking and stretching

DAY 5 — Cardio
• Moderate cardio session

DAY 6 — Strength + Core
• Full-body strength
• Core exercises

DAY 7 — Rest
• Complete rest or gentle movement

Safety reminder:
Stop exercise if you experience sharp pain, dizziness,
chest pain, or unusual shortness of breath.

Previous plan was:

{original_plan}
""".strip()


def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_workout(
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    prompt = f"""
Create a personalized 7-day workout plan.

User information:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Requested intensity: {intensity}

Requirements:

• Create exactly 7 days.
• Clearly label DAY 1 through DAY 7.
• Include exercises, sets/repetitions or duration.
• Include warm-up and cool-down where appropriate.
• Include at least one recovery/rest day.
• Respect the requested intensity.
• Keep the plan practical for a general fitness user.
• Do not make medical claims.
• Do not recommend dangerous exercises.
• Do not recommend extreme calorie restriction.
• Explain basic safety guidance at the end.

Return only the workout plan.
"""

    try:
        return _generate(
            model=settings.gemini_pro_model,
            prompt=prompt,
            temperature=0.65,
        )

    except Exception:
        # Flash is used as a fallback so the application remains
        # functional if the configured primary model is unavailable.
        return _generate(
            model=settings.gemini_flash_model,
            prompt=prompt,
            temperature=0.65,
        )


def generate_nutrition_tip_with_flash(
    goal: str,
    age: int,
    weight: float,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_nutrition_tip(goal)

    prompt = f"""
Create a concise nutrition and recovery tip for a general
fitness user.

Age: {age}
Weight: {weight} kg
Fitness goal: {goal}

Include:

• Protein guidance
• Fruits/vegetables
• Hydration
• Sleep/recovery
• Avoiding extreme diets

Do not prescribe a medical diet.
Do not diagnose conditions.
Do not recommend unsafe weight loss.

Keep the response under 250 words.
"""

    return _generate(
        model=settings.gemini_flash_model,
        prompt=prompt,
        temperature=0.5,
    )


def update_workout_plan(
    original_plan: str,
    feedback: str,
    name: str,
    age: int,
    goal: str,
    intensity: str,
) -> str:

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_updated_plan(
            original_plan=original_plan,
            feedback=feedback,
        )

    prompt = f"""
Update an existing 7-day fitness plan according to user feedback.

User:
Name: {name}
Age: {age}
Goal: {goal}
Intensity: {intensity}

Original plan:

{original_plan}

User feedback:

{feedback}

Requirements:

• Produce a complete revised 7-day plan.
• Incorporate the feedback where reasonable.
• Do not blindly follow unsafe requests.
• Maintain appropriate recovery/rest.
• Do not dramatically increase exercise volume.
• Respect the requested intensity.
• Include clear daily activities.
• End with a short safety reminder.

Return only the revised workout plan.
"""

    return _generate(
        model=settings.gemini_pro_model,
        prompt=prompt,
        temperature=0.65,
    )