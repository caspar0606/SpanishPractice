from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import current_username
from src.api.errors import http_from_value_error
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
def onboarding_status(username: str = Depends(current_username)):
    user = container.users().load(username)
    if user is None:
        raise HTTPException(status_code=400, detail=f"User '{username}' not found")

    return OnboardingStatusResponse(
        step=onboarding_file.current_step(user),
        goals=user.goals,
        plan=PlanSummary(**onboarding_file.plan_summary(user)),
    )


@router.post("/goals", response_model=GoalsResponse)
def save_goals(request: GoalsRequest, username: str = Depends(current_username)):
    try:
        user = onboarding_file.save_goals(username, request.goals)
    except ValueError as e:
        raise http_from_value_error(e) from e

    return GoalsResponse(
        step=onboarding_file.current_step(user),
        plan=PlanSummary(**onboarding_file.plan_summary(user)),
    )


@router.get("/placement", response_model=PlacementFormResponse)
def placement_form(username: str = Depends(current_username)):
    try:
        return PlacementFormResponse(form=placement_file.build_form())
    except (FileNotFoundError, KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Placement bank unavailable: {e}") from e


@router.post("/placement", response_model=PlacementSubmitResponse)
def submit_placement(request: PlacementSubmitRequest, username: str = Depends(current_username)):
    try:
        result = placement_file.submit(username, request.submission)
    except ValueError as e:
        raise http_from_value_error(e) from e

    user = container.users().load(username)
    plan = onboarding_file.plan_summary(user) if user else {}

    return PlacementSubmitResponse(**result, plan=PlanSummary(**plan))
