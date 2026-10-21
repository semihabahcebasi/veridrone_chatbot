import sqlite3

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from app.services.lead_service import create_lead
from app.services.ai_service import generate_reply, ChatServiceError
main = Blueprint("main", __name__)


@main.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "VeriDrone API"
    })


@main.post("/api/leads")
def capture_lead():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type application/json olmalı."
        }), 415

    try:
        payload = request.get_json()
        lead_id = create_lead(payload)

    except BadRequest:
        return jsonify({
            "error": "JSON biçimi geçersiz."
        }), 400

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except sqlite3.Error:
        return jsonify({
            "error": "Başvurun kaydedilemedi. Lütfen tekrar dene."
        }), 500

    return jsonify({
        "message": "Başvurun alındı.",
        "lead_id": lead_id
    }), 201

@main.post("/api/chat")
def chat():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type application/json olmalı."
        }), 415

    try:
        payload = request.get_json()

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Bir JSON nesnesi gönderilmeli."
            }), 400

        reply = generate_reply(
            message=payload.get("message"),
            history=payload.get("history", []),
        )

        return jsonify({"reply": reply})

    except BadRequest:
        return jsonify({
            "error": "JSON biçimi geçersiz."
        }), 400

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except ChatServiceError as error:
        return jsonify({
            "error": str(error)
        }), 503