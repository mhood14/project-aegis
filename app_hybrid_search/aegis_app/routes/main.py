from flask import Blueprint, current_app, render_template, request

from ..services.agent import answer_question
from ..services.audit import log_error, log_event, new_request_id
from ..services.storage import StorageService
from ..services.user_context import build_user_context

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    prompt = ""
    answer = ""
    error = ""
    citations = []
    scope = request.args.get("scope", current_app.config["DEFAULT_SCOPE"]).strip() or current_app.config["DEFAULT_SCOPE"]
    request_id = request.args.get("request_id", "")
    upload_status = request.args.get("upload_status", "")
    upload_message = request.args.get("upload_message", "")
    fallback_used = False

    user_context = build_user_context(request)

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        scope = request.form.get("scope", current_app.config["DEFAULT_SCOPE"]).strip() or current_app.config["DEFAULT_SCOPE"]
        request_id = new_request_id()

        log_event(
            "question_submission_started",
            {
                "request_id": request_id,
                "user_id": user_context.get("user_id"),
                "scope": scope,
                "question_length": len(prompt),
                "is_authenticated": user_context.get("is_authenticated"),
            },
            message="Question submission started",
        )

        if prompt:
            try:
                result = answer_question(
                    user_context=user_context,
                    question=prompt,
                    scope=scope,
                    request_id=request_id,
                )
                answer = result["answer"]
                citations = result["citations"]
                fallback_used = result.get("fallback_used", False)

            except Exception as ex:
                error = f"{type(ex).__name__}: {ex}"
                log_error(
                    "application_error",
                    ex,
                    {
                        "request_id": request_id,
                        "user_id": user_context.get("user_id"),
                        "scope": scope,
                        "stage": "main.index.post",
                    },
                    message="Question submission failed",
                )

    documents = StorageService().list_processed_documents(scope=scope, limit=10)

    return render_template(
        "index.html",
        app_title=current_app.config["APP_TITLE"],
        prompt=prompt,
        answer=answer,
        error=error,
        citations=citations,
        scope=scope,
        request_id=request_id,
        upload_status=upload_status,
        upload_message=upload_message,
        documents=documents,
        fallback_used=fallback_used,
        signed_in_user=user_context.get("user_id"),
        is_authenticated=user_context.get("is_authenticated"),
        user_roles=user_context.get("roles", []),
    )