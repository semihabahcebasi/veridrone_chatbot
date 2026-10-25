import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def get_db():
    """Her istek için ihtiyaç olduğunda bir bağlantı açar."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            timeout=10
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):
    """İstek tamamlandığında bağlantıyı kapatır."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Henüz yoksa lead tablosunu oluşturur."""
    db = get_db()

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY,
                full_name NVARCHAR(150) NOT NULL,
                company NVARCHAR(200),
                email NVARCHAR(254) NOT NULL,
                phone NVARCHAR(30),
                message NVARCHAR(5000) NOT NULL,
                source NVARCHAR(30) NOT NULL DEFAULT 'contact_form',
                status NVARCHAR(30) NOT NULL DEFAULT 'new',
                created_at NVARCHAR(30) NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

    except sqlite3.Error:
        db.rollback()
        current_app.logger.exception(
            "Lead tablosu oluşturulamadı."
        )
        raise


@click.command("init-db")
def init_db_command():
    """Terminalden veritabanını hazırlar."""
    try:
        init_db()
    except sqlite3.Error as error:
        raise click.ClickException(
            "Veritabanı hazırlanamadı. Terminal kayıtlarını kontrol et."
        ) from error

    click.echo("VeriDrone veritabanı hazır.")


def init_app(app):
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.setdefault(
        "DATABASE",
        str(Path(app.instance_path) / "veridrone.sqlite3")
    )

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        init_db()


def insert_lead(data):
    """Kontrol edilmiş lead bilgilerini kaydeder."""
    db = get_db()

    try:
        cursor = db.execute(
            """
            INSERT INTO leads (
                full_name, company, email, phone, message
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["full_name"],
                data["company"],
                data["email"],
                data["phone"],
                data["message"],
            ),
        )
        db.commit()
        return cursor.lastrowid

    except sqlite3.Error:
        db.rollback()
        current_app.logger.exception("Lead kaydedilemedi.")
        raise

