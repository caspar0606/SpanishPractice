from fastapi import APIRouter, HTTPException

from src.api.schemas.onboarding import (
    GoalsRequest,
    GoalsResponse,
    OnboardingStatusResponse,
    PlacementFormResponse,
    PlacementSubmitRequest,
    PlacementSubmitResponse,
    PlanSummary,
)
from src.application import container
from src.application.services import onboarding as onboarding_file
from src.application.services import placement as placement_file

router = APIRouter()


@router.get("/status", response_model=OnboardingStatusResponse)
def onboarding_status(username: str):
    user = container.users().load(username)
    if user is None:
        raise HTTPException(status_code=400, detail=f"User '{username}' not found")

    return OnboardingStatusResponse(
        step=onboarding_file.current_step(user),
        goals=user.goals,
        plan=PlanSummary(**onboarding_file.plan_summary(user)),
    )


@router.post("/goals", response_model=GoalsResponse)
def save_goals(request: GoalsRequest):
    try:
        user = onboarding_file.save_goals(request.username, request.goals)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return GoalsResponse(
        user=user,
        step=onboarding_file.current_step(user),
        plan=PlanSummary(**onboarding_file.plan_summary(user)),
    )


@router.get("/placement", response_model=PlacementFormResponse)
def placement_form():
    try:
        return PlacementFormResponse(form=placement_file.build_form())
    except (FileNotFoundError, KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Placement bank unavailable: {e}") from e


@router.post("/placement", response_model=PlacementSubmitResponse)
def submit_placement(request: PlacementSubmitRequest):
    try:
        result = placement_file.submit(request.username, request.submission)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    user = container.users().load(request.username)
    plan = onboarding_file.plan_summary(user) if user else {}

    return PlacementSubmitResponse(**result, plan=PlanSummary(**plan))
