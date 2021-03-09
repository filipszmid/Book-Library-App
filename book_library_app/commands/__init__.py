from flask import Blueprint


db_manage_bp= Blueprint('db_manage_cmd',__name__, cli_group=None) #wskazuje do jakiej grupy nalezy przyporzadkowac utworzone komendy


from book_library_app.commands import db_manage_commands