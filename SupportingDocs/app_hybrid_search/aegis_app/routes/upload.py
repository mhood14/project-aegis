from flask import Blueprint, current_app, jsonify, redirect, request, url_for

from ..services.audit import log_error, log_event, new_request_id
from ..services.authz import authorize_scope_or_raise
from ..services.ingest import process_uploaded_file
from ..services.user_context import build_user_context

upload_bp = Blueprint("upload", __name__)


def _wants_json_response() -> bool:
    accept = request.headers.get("Accept", "")
    return (
        request.args.get("format") == "json"
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in accept
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_document():
    request_id = new_request_id()
    scope = request.form.get("scope", current_app.config["DEFAULT_SCOPE"]).strip() or current_app.config["DEFAULT_SCOPE"]
    user_context = build_user_context(request)
    user_id = user_context.get("user_id", "anonymous")

    try:
        if "file" not in request.files:
            log_event(
                "invalid_upload_request",
                {
                    "request_id": request_id,
                    "user_id": user_id,
                    "scope": scope,
                    "reason": "missing_file_field",
                },
                status="denied",
                message="Upload request missing file field",
            )
            if _wants_json_response():
                return jsonify({"error": "Missing file field.", "request_id": request_id}), 400
            return redirect(
                url_for(
                    "main.index",
                    upload_status="error",
                    upload_message="Missing file field.",
                    request_id=request_id,
                    scope=scope,
                )
            )

        authorize_scope_or_raise(user_context, scope, request_id=request_id)

        file = request.files["file"]

        if not file.filename:
            log_event(
                "invalid_upload_request",
                {
                    "request_id": request_id,
                    "user_id": user_id,
                    "scope": scope,
                    "reason": "missing_filename",
                },
                status="denied",
                message="Upload request missing filename",
            )
            if _wants_json_response():
                return jsonify({"error": "No filename supplied.", "request_id": request_id}), 400
            return redirect(
                url_for(
                    "main.index",
                    upload_status="error",
                    upload_message="No filename supplied.",
                    request_id=request_id,
                    scope=scope,
                )
            )

        content = file.read()
        if len(content) > current_app.config["MAX_UPLOAD_BYTES"]:
            message = f"File exceeds {current_app.config['MAX_UPLOAD_MB']} MB limit."
            log_event(
                "upload_size_exceeded",
                {
                    "request_id": request_id,
                    "user_id": user_id,
                    "scope": scope,
                    "filename": file.filename,
                    "byte_count": len(content),
                    "max_upload_bytes": current_app.config["MAX_UPLOAD_BYTES"],
                },
                status="denied",
                message="Upload size limit exceeded",
            )
            if _wants_json_response():
                return jsonify({"error": message, "request_id": request_id}), 400
            return redirect(
                url_for(
                    "main.index",
                    upload_status="error",
                    upload_message=message,
                    request_id=request_id,
                    scope=scope,
                )
            )

        result = process_uploaded_file(
            filename=file.filename,
            content_bytes=content,
            uploaded_by=user_id,
            scope=scope,
            content_type=file.mimetype or "application/octet-stream",
            request_id=request_id,
            document_category="normal",
            is_test_document=(scope == "security-tests"),
        )

        if _wants_json_response():
            return jsonify(result), 201

        success_message = f"Uploaded {file.filename} successfully. Document ID: {result['document_id']}"
        return redirect(
            url_for(
                "main.index",
                upload_status="success",
                upload_message=success_message,
                request_id=request_id,
                scope=scope,
            )
        )

    except Exception as ex:
        log_error(
            "application_error",
            ex,
            {
                "request_id": request_id,
                "user_id": user_id,
                "scope": scope,
                "stage": "upload_document",
            },
            message="Upload request failed",
        )

        if _wants_json_response():
            status_code = 403 if isinstance(ex, PermissionError) else 400
            return jsonify({"error": str(ex), "request_id": request_id}), status_code

        return redirect(
            url_for(
                "main.index",
                upload_status="error",
                upload_message=str(ex),
                request_id=request_id,
                scope=scope,
            )
        )