import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


def create_app():
    # Flask 애플리케이션 초기화
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-secret-key")

    # 데이터베이스 설정
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///todo.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 데이터베이스 초기화
    db = SQLAlchemy(app)

    # Todo 모델 정의
    class Todo(db.Model):
        __tablename__ = "todos"
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(200), nullable=False)
        completed = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Todo {self.id}: {self.content}>"

    # 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()

    # 라우트
    @app.route("/")
    def index():
        """모든 할 일을 포함한 메인 페이지를 렌더링합니다."""
        try:
            todos = Todo.query.order_by(Todo.date_created.desc()).all()
            return render_template("index.html", todos=todos)
        except Exception as e:
            flash(f"할 일 목록을 불러오는 중 오류 발생: {str(e)}", "error")
            return render_template("index.html", todos=[])

    @app.route("/add", methods=["POST"])
    def add():
        """새로운 할 일을 추가합니다."""
        content = request.form.get("content", "").strip()
        if not content:
            flash("할 일 내용은 비어 있을 수 없습니다.", "error")
            return redirect(url_for("index"))

        if len(content) > 200:
            flash("할 일 내용은 200자를 초과할 수 없습니다.", "error")
            return redirect(url_for("index"))

        try:
            new_todo = Todo(content=content)
            db.session.add(new_todo)
            db.session.commit()
            flash("할 일이 성공적으로 추가되었습니다.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"할 일 추가 중 오류 발생: {str(e)}", "error")

        return redirect(url_for("index"))

    @app.route("/delete/<int:todo_id>")
    def delete(todo_id):
        """할 일을 삭제합니다."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            db.session.delete(todo)
            db.session.commit()
            flash("할 일이 성공적으로 삭제되었습니다.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"할 일 삭제 중 오류 발생: {str(e)}", "error")

        return redirect(url_for("index"))

    @app.route("/toggle/<int:todo_id>")
    def toggle(todo_id):
        """할 일의 완료 상태를 전환합니다."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            todo.completed = not todo.completed
            db.session.commit()
            flash("할 일 상태가 업데이트되었습니다.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"할 일 상태 업데이트 중 오류 발생: {str(e)}", "error")

        return redirect(url_for("index"))

    @app.route("/edit/<int:todo_id>", methods=["POST"])
    def edit(todo_id):
        """할 일을 수정합니다."""
        try:
            todo = Todo.query.get_or_404(todo_id)
            new_content = request.form.get("content", "").strip()

            if not new_content:
                flash("할 일 내용은 비어 있을 수 없습니다.", "error")
                return redirect(url_for("index"))

            if len(new_content) > 200:
                flash("할 일 내용은 200자를 초과할 수 없습니다.", "error")
                return redirect(url_for("index"))

            todo.content = new_content
            db.session.commit()
            flash("할 일이 성공적으로 수정되었습니다.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"할 일 수정 중 오류 발생: {str(e)}", "error")

        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    # 애플리케이션 실행
    app = create_app()
    app.run(
        debug=os.environ.get("FLASK_ENV") == "development", host="0.0.0.0", port=5000
    )
